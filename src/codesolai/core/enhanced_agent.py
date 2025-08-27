"""
Enhanced Agent implementation with sophisticated reasoning capabilities
"""

from typing import Dict, Any, Optional
from datetime import datetime

from .agent import Agent, AgentConfig
from ..providers.provider_manager import ProviderManager
from ..utils import Utils


class EnhancedAgent(Agent):
    """
    Enhanced Agent with sophisticated reasoning and provider integration
    This replaces the old agent with advanced capabilities
    """

    def __init__(self, options: Optional[Dict[str, Any]] = None):
        """Initialize enhanced agent with provider integration"""
        options = options or {}
        
        # Create enhanced configuration
        config = AgentConfig(
            name=options.get('name', 'codesolai-agent'),
            model=options.get('model', 'claude-3-5-sonnet-20241022'),
            provider=options.get('provider', 'claude'),
            api_key=options.get('api_key'),
            temperature=options.get('temperature', 0.7),
            max_tokens=options.get('max_tokens', 4000),
            reasoning_effort=options.get('effort', 'medium'),
            max_iterations=options.get('max_iterations', 10),
            enable_reflection=options.get('enable_reflection', True),
            enable_planning=options.get('enable_planning', True),
            tools_enabled=options.get('tools_enabled', True),
            auto_approve=options.get('auto_approve', True),
            confirmation_required=options.get('confirmation_required', False),
            max_concurrent_tools=options.get('max_concurrent', 3),
            max_context_size=options.get('max_context_size', 100000),
            compression_threshold=options.get('compression_threshold', 0.8),
            retention_strategy=options.get('retention_strategy', 'importance'),
            log_level=options.get('log_level', 'info'),
            enable_metrics=options.get('enable_metrics', True),
            enable_tracing=options.get('enable_tracing', False)
        )
        
        # Initialize base agent
        super().__init__(config)
        
        # Store provider configuration
        self.provider_config = {
            'provider': config.provider,
            'api_key': config.api_key,
            'model': config.model,
            'temperature': config.temperature,
            'max_tokens': config.max_tokens
        }
        
        # Initialize provider manager
        self.provider_manager = ProviderManager()
        
        self.logger.info('Enhanced agent initialized', {
            'provider': config.provider,
            'model': config.model,
            'tools_enabled': config.tools_enabled
        })

    async def process_prompt(self, prompt: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process user prompt with enhanced reasoning
        This is the main entry point for the enhanced agent
        """
        options = options or {}
        
        try:
            # Validate inputs
            if not prompt or not isinstance(prompt, str) or not prompt.strip():
                raise ValueError('Prompt is required and must be a non-empty string')
            
            # Merge options with defaults
            process_options = {
                'provider': options.get('provider', self.provider_config['provider']),
                'api_key': options.get('api_key', self.provider_config['api_key']),
                'model': options.get('model', self.provider_config['model']),
                'temperature': options.get('temperature', self.provider_config['temperature']),
                'max_tokens': options.get('max_tokens', self.provider_config['max_tokens']),
                'auto_approve': options.get('auto_approve', self.config.auto_approve),
                'effort': options.get('effort', self.config.reasoning_effort),
                **options
            }
            
            self.logger.info('Processing prompt with enhanced agent', {
                'prompt_length': len(prompt),
                'provider': process_options['provider'],
                'model': process_options['model'],
                'effort': process_options['effort']
            })
            
            # Validate API key
            if not process_options['api_key']:
                return {
                    'success': False,
                    'error': 'API key is required',
                    'response': 'I need an API key to process your request. Please provide one using --api-key or configure it in your settings.'
                }
            
            # Validate API key format
            if not Utils.validate_api_key(process_options['api_key'], process_options['provider']):
                return {
                    'success': False,
                    'error': 'Invalid API key format',
                    'response': f'The provided API key format is invalid for {process_options["provider"]}. Please check your API key.'
                }
            
            # Step 1: Get LLM response with context
            llm_response = await self._get_llm_response(prompt, process_options)
            
            if not llm_response.get('success', False):
                return llm_response
            
            # Step 2: Parse actions from the response
            parsed_actions = self._parse_actions_from_response(llm_response['response'])
            
            # Step 3: Execute actions if tools are enabled and actions are found
            execution_results = []
            if parsed_actions and self.config.tools_enabled:
                execution_results = await self._execute_parsed_actions(
                    parsed_actions, 
                    process_options
                )
            
            # Step 4: Generate final response
            final_response = await self._generate_final_response(
                prompt,
                llm_response['response'],
                parsed_actions,
                execution_results,
                process_options
            )
            
            return {
                'success': True,
                'response': final_response,
                'llm_response': llm_response['response'],
                'actions_found': len(parsed_actions),
                'actions_executed': len(execution_results),
                'execution_results': execution_results,
                'provider': process_options['provider'],
                'model': process_options['model']
            }
            
        except Exception as error:
            self.logger.error('Error processing prompt', {
                'error': str(error),
                'prompt_length': len(prompt) if prompt else 0
            })
            
            return {
                'success': False,
                'error': str(error),
                'response': f'I encountered an error while processing your request: {str(error)}'
            }

    async def _get_llm_response(self, prompt: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Get response from LLM provider with agent capabilities"""
        try:
            # Enhance the prompt with agent capabilities if tools are enabled
            enhanced_prompt = prompt
            if options.get('tools_enabled', True):
                enhanced_prompt = f"""You are CodeSolAI, an AI assistant with the ability to perform actions using tools.

Available tools:
- read_file: Read file contents
- write_file: Write content to a file
- list_directory: List directory contents
- create_directory: Create a directory
- execute_command: Execute shell commands
- analyze_code: Analyze code structure
- http_request: Make HTTP requests

When you need to perform an action, use this format:
ACTION: tool_name
PARAMETERS: {{"param1": "value1", "param2": "value2"}}

User request: {prompt}

Please provide a helpful response and use tools when appropriate to complete the task."""

            response = await self.provider_manager.call(
                options['provider'],
                options['api_key'],
                enhanced_prompt,
                {
                    'model': options.get('model'),
                    'temperature': options.get('temperature'),
                    'max_tokens': options.get('max_tokens')
                }
            )
            
            return {
                'success': True,
                'response': response
            }
            
        except Exception as error:
            error_message = Utils.format_error(error, options['provider'])
            return {
                'success': False,
                'error': error_message,
                'response': f'I encountered an error while getting a response: {error_message}'
            }

    def _parse_actions_from_response(self, response: str) -> list:
        """Parse actions from LLM response"""
        import re
        import json

        actions = []

        # Look for ACTION: and PARAMETERS: patterns
        action_pattern = r'ACTION:\s*(\w+)\s*\nPARAMETERS:\s*(\{.*?\})'
        matches = re.findall(action_pattern, response, re.DOTALL | re.IGNORECASE)

        for match in matches:
            tool_name = match[0].strip()
            try:
                parameters = json.loads(match[1])

                # Normalize and provide default parameters for common tools
                if tool_name == 'list_directory':
                    # Handle different parameter names
                    if 'directory' in parameters:
                        parameters['path'] = parameters.pop('directory')
                    if 'hidden' in parameters:
                        parameters['include_hidden'] = parameters.pop('hidden')
                    if not parameters.get('path'):
                        parameters['path'] = '.'
                elif tool_name == 'read_file':
                    if 'file' in parameters:
                        parameters['path'] = parameters.pop('file')
                    if 'file_path' in parameters:
                        parameters['path'] = parameters.pop('file_path')
                    if 'filepath' in parameters:
                        parameters['path'] = parameters.pop('filepath')
                    if not parameters.get('path'):
                        continue  # Skip if no path provided
                elif tool_name == 'write_file':
                    if 'file' in parameters:
                        parameters['path'] = parameters.pop('file')
                    if 'file_path' in parameters:
                        parameters['path'] = parameters.pop('file_path')
                    if 'filepath' in parameters:
                        parameters['path'] = parameters.pop('filepath')
                    if not parameters.get('path'):
                        continue  # Skip if no path provided

                actions.append({
                    'tool': tool_name,
                    'parameters': parameters
                })
            except json.JSONDecodeError:
                self.logger.warning('Failed to parse action parameters', {
                    'tool': tool_name,
                    'raw_parameters': match[1]
                })

                # Try to create action with default parameters
                if tool_name == 'list_directory':
                    actions.append({
                        'tool': 'list_directory',
                        'parameters': {'path': '.'}
                    })

        # Also look for simpler patterns like "create file: filename.py"
        simple_patterns = [
            (r'create file[:\s]+([^\s\n]+)', 'write_file'),
            (r'read file[:\s]+([^\s\n]+)', 'read_file'),
            (r'list directory[:\s]+([^\s\n]+)', 'list_directory'),
            (r'run command[:\s]+([^\n]+)', 'execute_command'),
            (r'execute[:\s]+([^\n]+)', 'execute_command')
        ]

        for pattern, tool_name in simple_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches:
                if tool_name == 'write_file':
                    actions.append({
                        'tool': 'write_file',
                        'parameters': {'path': match, 'content': '# Generated file\n'}
                    })
                elif tool_name == 'read_file':
                    actions.append({
                        'tool': 'read_file',
                        'parameters': {'path': match}
                    })
                elif tool_name == 'list_directory':
                    actions.append({
                        'tool': 'list_directory',
                        'parameters': {'path': match}
                    })
                elif tool_name == 'execute_command':
                    actions.append({
                        'tool': 'execute_command',
                        'parameters': {'command': match}
                    })

        return actions

    async def _execute_parsed_actions(self, actions: list, options: Dict[str, Any]) -> list:
        """Execute parsed actions using the tool registry"""
        if not actions:
            return []

        results = []
        conversation_id = f"agent-{self.id}"

        for action in actions:
            try:
                tool_name = action.get('tool')
                parameters = action.get('parameters', {})

                self.logger.info('Executing action', {
                    'tool': tool_name,
                    'parameters': parameters
                })

                # Check if user approval is needed
                if not options.get('auto_approve', True) and options.get('confirmation_required', False):
                    # In a real implementation, this would prompt the user
                    # For now, we'll assume approval
                    pass

                # Execute the tool
                result = await self.tool_registry.execute_tool(
                    tool_name,
                    parameters,
                    conversation_id
                )

                results.append(result)

                self.logger.info('Action executed', {
                    'tool': tool_name,
                    'success': result.get('success', False)
                })

            except Exception as error:
                self.logger.error('Action execution failed', {
                    'action': action,
                    'error': str(error)
                })
                results.append({
                    'success': False,
                    'error': str(error),
                    'tool': action.get('tool', 'unknown'),
                    'parameters': action.get('parameters', {})
                })

        return results

    async def _generate_final_response(self, original_prompt: str, llm_response: str,
                                     actions: list, execution_results: list,
                                     options: Dict[str, Any]) -> str:
        """Generate final response incorporating action results"""
        # If no actions were executed, return the original LLM response
        if not execution_results:
            return llm_response

        # Build enhanced response with action results
        enhanced_response = llm_response + "\n\n"

        # Add results from executed actions
        for i, result in enumerate(execution_results, 1):
            if result.get('success'):
                tool_name = result.get('tool', 'Unknown')
                # Handle nested result structure from tool registry
                tool_result = result.get('result', {})
                if isinstance(tool_result, dict) and 'result' in tool_result:
                    tool_result = tool_result['result']

                if tool_name == 'list_directory':
                    items = tool_result.get('items', [])
                    enhanced_response += f"📁 **Directory listing for {tool_result.get('path', '.')}:**\n"
                    if items:
                        for item in items[:20]:  # Limit to first 20 items
                            icon = "📁" if item['type'] == 'directory' else "📄"
                            enhanced_response += f"  {icon} {item['name']}\n"
                        if len(items) > 20:
                            enhanced_response += f"  ... and {len(items) - 20} more items\n"
                    else:
                        enhanced_response += "  (empty directory)\n"

                elif tool_name == 'read_file':
                    content = tool_result.get('content', '')
                    path = tool_result.get('path', 'file')
                    enhanced_response += f"📄 **Contents of {path}:**\n```\n{content[:1000]}\n```\n"
                    if len(content) > 1000:
                        enhanced_response += "... (content truncated)\n"

                elif tool_name == 'execute_command':
                    command = tool_result.get('command', '')
                    stdout = tool_result.get('stdout', '')
                    stderr = tool_result.get('stderr', '')
                    return_code = tool_result.get('return_code', 0)

                    enhanced_response += f"💻 **Command executed:** `{command}`\n"
                    enhanced_response += f"**Exit code:** {return_code}\n"
                    if stdout:
                        enhanced_response += f"**Output:**\n```\n{stdout[:1000]}\n```\n"
                    if stderr:
                        enhanced_response += f"**Errors:**\n```\n{stderr[:500]}\n```\n"

                else:
                    # Generic result display
                    enhanced_response += f"🔧 **{tool_name} result:**\n{str(tool_result)[:500]}\n"
            else:
                # Show failed actions
                error = result.get('error', 'Unknown error')
                tool_name = result.get('tool', 'Unknown')
                enhanced_response += f"❌ **{tool_name} failed:** {error}\n"

        return enhanced_response

    async def test_connection(self, provider: str, api_key: str) -> Dict[str, Any]:
        """Test connection to provider"""
        try:
            test_result = await self.provider_manager.test_api_key(provider, api_key)
            
            return {
                'success': test_result,
                'provider': provider,
                'message': f'{provider.upper()} API key is {"valid" if test_result else "invalid"}'
            }
            
        except Exception as error:
            return {
                'success': False,
                'provider': provider,
                'error': str(error),
                'message': f'Failed to test {provider.upper()} API key: {str(error)}'
            }

    def get_supported_providers(self) -> list:
        """Get list of supported providers"""
        return self.provider_manager.get_supported_providers()

    def get_provider_models(self, provider: str) -> list:
        """Get available models for a provider"""
        return self.provider_manager.get_available_models(provider)

    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            'id': self.id,
            'name': self.name,
            'state': self.state.value,
            'provider': self.provider_config['provider'],
            'model': self.provider_config['model'],
            'tools_enabled': self.config.tools_enabled,
            'uptime': (datetime.now() - self.start_time).total_seconds(),
            'metrics': self.metrics.__dict__
        }
