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
            
            # Step 3: Execute actions if agent mode is enabled and actions are found
            execution_results = []
            if process_options.get('agent', False) and parsed_actions and self.config.tools_enabled:
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
        """Get response from LLM provider"""
        try:
            response = await self.provider_manager.call(
                options['provider'],
                options['api_key'],
                prompt,
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
        # This would implement action parsing logic
        # For now, return empty list as actions are not fully implemented
        return []

    async def _execute_parsed_actions(self, actions: list, options: Dict[str, Any]) -> list:
        """Execute parsed actions"""
        # This would implement action execution
        # For now, return empty list as actions are not fully implemented
        return []

    async def _generate_final_response(self, original_prompt: str, llm_response: str, 
                                     actions: list, execution_results: list, 
                                     options: Dict[str, Any]) -> str:
        """Generate final response incorporating action results"""
        # If no actions were executed, return the original LLM response
        if not execution_results:
            return llm_response
        
        # If actions were executed, we could enhance the response
        # For now, just return the original response
        return llm_response

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
