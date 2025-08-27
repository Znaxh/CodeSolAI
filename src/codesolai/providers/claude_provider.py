"""
Claude (Anthropic) provider implementation
"""

import asyncio
from typing import Dict, Any, Optional
import httpx
from .base_provider import BaseProvider


class ClaudeProvider(BaseProvider):
    """Claude (Anthropic) API provider"""

    def __init__(self, timeout: float = 30.0, max_retries: int = 3):
        super().__init__(timeout, max_retries)
        self.base_url = "https://api.anthropic.com/v1"

    async def call(self, api_key: str, prompt: str, options: Optional[Dict[str, Any]] = None) -> str:
        """Make API call to Claude (Anthropic)"""
        options = options or {}
        url = f"{self.base_url}/messages"
        
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01'
        }

        model = self._get_model_for_provider(options.get('model'), 'claude')
        data = {
            'model': model,
            'max_tokens': options.get('maxTokens', 4000),
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        }

        # Add temperature if specified
        if 'temperature' in options:
            data['temperature'] = options['temperature']

        try:
            response_data = await self.make_request(url, headers, data)

            # Extract content from Claude's response format
            if (response_data and 
                'content' in response_data and 
                response_data['content'] and 
                len(response_data['content']) > 0):
                return response_data['content'][0]['text']
            else:
                raise Exception('Unexpected response format from Claude API')

        except Exception as error:
            raise self.handle_provider_error(error, 'Claude')

    def _get_model_for_provider(self, requested_model: Optional[str], provider: str) -> str:
        """Get the appropriate model for Claude"""
        available_models = [
            'claude-3-5-sonnet-20241022',
            'claude-3-5-haiku-20241022',
            'claude-3-opus-20240229',
            'claude-3-sonnet-20240229',
            'claude-3-haiku-20240307'
        ]
        default_model = 'claude-3-5-sonnet-20241022'
        
        if not requested_model:
            return default_model
        
        if requested_model in available_models:
            return requested_model
        
        return default_model

    def handle_provider_error(self, error: Exception, provider: str) -> Exception:
        """Handle and format Claude-specific errors"""
        contextual_message = str(error)
        
        if hasattr(error, 'response') and error.response:
            status = error.response.status_code
            
            if status == 401:
                contextual_message += '\nEnsure your Anthropic API key is valid and has the correct permissions.'
            elif status == 429:
                contextual_message += '\nRate limit exceeded. Please wait before making more requests.'
            elif status == 400:
                contextual_message += '\nInvalid request. Check your prompt and parameters.'
        
        provider_error = Exception(contextual_message)
        provider_error.provider = provider
        provider_error.original_error = error
        
        return provider_error
