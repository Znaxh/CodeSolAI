"""
Reasoning Engine for sophisticated agent reasoning and planning
"""

import json
import re
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable

from .logger import Logger
from ..providers.provider_manager import ProviderManager


class ReasoningEngine:
    """Engine for sophisticated agent reasoning and planning"""

    def __init__(self, logger: Logger, effort: str = "medium", max_iterations: int = 10, 
                 enable_reflection: bool = True, enable_planning: bool = True):
        self.logger = logger
        self.effort = effort
        self.max_iterations = max_iterations
        self.enable_reflection = enable_reflection
        self.enable_planning = enable_planning
        
        # Event handlers
        self.on_reasoning_start: Optional[Callable] = None
        self.on_reasoning_complete: Optional[Callable] = None
        
        # Initialize provider manager for LLM calls
        self.provider_manager = ProviderManager()
        
        self.logger.debug('Reasoning engine initialized', {
            'effort': effort,
            'max_iterations': max_iterations,
            'enable_reflection': enable_reflection,
            'enable_planning': enable_planning
        })

    async def process(self, reasoning_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input through the reasoning engine"""
        start_time = datetime.now()
        
        input_text = reasoning_data.get('input', '')
        context = reasoning_data.get('context', {})
        conversation = reasoning_data.get('conversation', {})
        options = reasoning_data.get('options', {})
        
        # Notify start
        if self.on_reasoning_start:
            self.on_reasoning_start({
                'input_length': len(input_text),
                'effort': self.effort,
                'start_time': start_time
            })
        
        try:
            # Step 1: Initial analysis and understanding
            analysis = await self._analyze_input(input_text, context, options)
            
            # Step 2: Planning (if enabled)
            plan = None
            if self.enable_planning:
                plan = await self._create_plan(input_text, analysis, context, options)
            
            # Step 3: Generate response
            response = await self._generate_response(input_text, analysis, plan, context, options)
            
            # Step 4: Extract actions from response
            actions = self._extract_actions(response)
            
            # Step 5: Reflection (if enabled)
            reflection = None
            if self.enable_reflection:
                reflection = await self._reflect_on_response(input_text, response, actions, context, options)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = {
                'response': response,
                'actions': actions,
                'analysis': analysis,
                'plan': plan,
                'reflection': reflection,
                'duration': duration,
                'effort': self.effort,
                'iterations': 1  # For now, single iteration
            }
            
            # Notify completion
            if self.on_reasoning_complete:
                self.on_reasoning_complete({
                    'duration': duration,
                    'actions_count': len(actions),
                    'effort': self.effort
                })
            
            self.logger.info('Reasoning completed', {
                'duration': duration,
                'actions_count': len(actions),
                'response_length': len(response)
            })
            
            return result
            
        except Exception as error:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.logger.error('Reasoning failed', {
                'error': str(error),
                'duration': duration
            })
            
            # Return error response
            return {
                'response': f"I encountered an error while processing your request: {str(error)}",
                'actions': [],
                'analysis': {},
                'plan': None,
                'reflection': None,
                'duration': duration,
                'effort': self.effort,
                'error': str(error)
            }

    async def _analyze_input(self, input_text: str, context: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the input to understand intent and requirements"""
        analysis_prompt = f"""
Analyze the following user input and provide a structured analysis:

User Input: {input_text}

Please analyze:
1. Intent: What is the user trying to accomplish?
2. Complexity: How complex is this request? (simple/medium/complex)
3. Required Actions: What actions might be needed to fulfill this request?
4. Context Needed: What additional context or information might be helpful?
5. Risks: Are there any potential risks or concerns?

Provide your analysis in a clear, structured format.
"""
        
        try:
            # Use the provider manager to get analysis
            provider = options.get('provider', 'claude')
            api_key = options.get('api_key')
            
            if not api_key:
                return {'error': 'No API key provided for analysis'}
            
            analysis_response = await self.provider_manager.call(
                provider, api_key, analysis_prompt, {
                    'temperature': 0.3,
                    'max_tokens': 1000
                }
            )
            
            return {
                'raw_analysis': analysis_response,
                'intent': self._extract_intent(analysis_response),
                'complexity': self._extract_complexity(analysis_response),
                'timestamp': datetime.now()
            }
            
        except Exception as error:
            self.logger.error('Analysis failed', {'error': str(error)})
            return {'error': str(error)}

    async def _create_plan(self, input_text: str, analysis: Dict[str, Any], context: Dict[str, Any], options: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a plan for addressing the user's request"""
        if analysis.get('error'):
            return None
        
        planning_prompt = f"""
Based on the following analysis, create a step-by-step plan:

User Input: {input_text}
Analysis: {analysis.get('raw_analysis', '')}

Create a detailed plan with:
1. Steps: List the specific steps needed
2. Tools: What tools or actions might be required for each step
3. Dependencies: Any dependencies between steps
4. Estimated Effort: How much effort each step might require

Provide a clear, actionable plan.
"""
        
        try:
            provider = options.get('provider', 'claude')
            api_key = options.get('api_key')
            
            if not api_key:
                return {'error': 'No API key provided for planning'}
            
            plan_response = await self.provider_manager.call(
                provider, api_key, planning_prompt, {
                    'temperature': 0.2,
                    'max_tokens': 1500
                }
            )
            
            return {
                'raw_plan': plan_response,
                'steps': self._extract_steps(plan_response),
                'timestamp': datetime.now()
            }
            
        except Exception as error:
            self.logger.error('Planning failed', {'error': str(error)})
            return {'error': str(error)}

    async def _generate_response(self, input_text: str, analysis: Dict[str, Any], plan: Optional[Dict[str, Any]], 
                                context: Dict[str, Any], options: Dict[str, Any]) -> str:
        """Generate the main response to the user"""
        response_prompt = f"""
User Input: {input_text}

Analysis: {analysis.get('raw_analysis', 'No analysis available')}

Plan: {plan.get('raw_plan', 'No plan available') if plan else 'No plan created'}

Based on the analysis and plan above, provide a helpful and comprehensive response to the user's request. 
If actions are needed, include them in your response using the format:

ACTION: tool_name
PARAMETERS: {{"param1": "value1", "param2": "value2"}}

Be clear, helpful, and actionable in your response.
"""
        
        try:
            provider = options.get('provider', 'claude')
            api_key = options.get('api_key')
            
            if not api_key:
                return "I need an API key to provide a response."
            
            response = await self.provider_manager.call(
                provider, api_key, response_prompt, {
                    'temperature': 0.7,
                    'max_tokens': 2000
                }
            )
            
            return response
            
        except Exception as error:
            self.logger.error('Response generation failed', {'error': str(error)})
            return f"I encountered an error while generating a response: {str(error)}"

    def _extract_actions(self, response: str) -> List[Dict[str, Any]]:
        """Extract actions from the response"""
        actions = []
        
        # Look for ACTION: and PARAMETERS: patterns
        action_pattern = r'ACTION:\s*(\w+)\s*\nPARAMETERS:\s*(\{.*?\})'
        matches = re.findall(action_pattern, response, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            tool_name = match[0].strip()
            try:
                parameters = json.loads(match[1])
                actions.append({
                    'tool': tool_name,
                    'parameters': parameters
                })
            except json.JSONDecodeError:
                self.logger.warn('Failed to parse action parameters', {
                    'tool': tool_name,
                    'raw_parameters': match[1]
                })
        
        return actions

    async def _reflect_on_response(self, input_text: str, response: str, actions: List[Dict[str, Any]], 
                                  context: Dict[str, Any], options: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Reflect on the generated response and actions"""
        reflection_prompt = f"""
Reflect on the following response and actions:

Original Input: {input_text}
Generated Response: {response}
Planned Actions: {json.dumps(actions, indent=2)}

Please evaluate:
1. Completeness: Does the response fully address the user's request?
2. Accuracy: Is the response accurate and appropriate?
3. Safety: Are there any safety concerns with the planned actions?
4. Improvements: What could be improved?

Provide a brief reflection.
"""
        
        try:
            provider = options.get('provider', 'claude')
            api_key = options.get('api_key')
            
            if not api_key:
                return {'error': 'No API key provided for reflection'}
            
            reflection_response = await self.provider_manager.call(
                provider, api_key, reflection_prompt, {
                    'temperature': 0.3,
                    'max_tokens': 800
                }
            )
            
            return {
                'raw_reflection': reflection_response,
                'timestamp': datetime.now()
            }
            
        except Exception as error:
            self.logger.error('Reflection failed', {'error': str(error)})
            return {'error': str(error)}

    def _extract_intent(self, analysis: str) -> str:
        """Extract intent from analysis"""
        # Simple pattern matching for intent
        intent_match = re.search(r'Intent:\s*(.+?)(?:\n|$)', analysis, re.IGNORECASE)
        return intent_match.group(1).strip() if intent_match else 'Unknown'

    def _extract_complexity(self, analysis: str) -> str:
        """Extract complexity from analysis"""
        complexity_match = re.search(r'Complexity:\s*(\w+)', analysis, re.IGNORECASE)
        return complexity_match.group(1).strip().lower() if complexity_match else 'medium'

    def _extract_steps(self, plan: str) -> List[str]:
        """Extract steps from plan"""
        # Simple extraction of numbered steps
        steps = []
        step_pattern = r'^\d+\.\s*(.+?)(?=\n\d+\.|\n\n|$)'
        matches = re.findall(step_pattern, plan, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            steps.append(match.strip())
        
        return steps

    async def shutdown(self):
        """Shutdown the reasoning engine"""
        self.logger.info('Shutting down reasoning engine')
