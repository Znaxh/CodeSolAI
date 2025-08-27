"""
GPT (OpenAI) provider implementation
"""

import asyncio
from typing import Dict, Any, Optional
import httpx
from .base_provider import BaseProvider


class GPTProvider(BaseProvider):
    """GPT (OpenAI) API provider"""

    def __init__(self, timeout: float = 30.0, max_retries: int = 3):
        super().__init__(timeout, max_retries)
        self.base_url = "https://api.openai.com/v1"

    async def call(self, api_key: str, prompt: str, options: Optional[Dict[str, Any]] = None) -> str:
        """Make API call to GPT (OpenAI)"""
        options = options or {}
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }

        model = self._get_model_for_provider(options.get('model'), 'gpt')
        data = {
            'model': model,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': options.get('maxTokens', 4000),
            'temperature': options.get('temperature', 0.7)
        }

        try:
            response_data = await self.make_request(url, headers, data)

            # Extract content from OpenAI's response format
            if (response_data and 
                'choices' in response_data and 
                response_data['choices'] and 
                len(response_data['choices']) > 0):
                return response_data['choices'][0]['message']['content']
            else:
                raise Exception('Unexpected response format from OpenAI API')

        except Exception as error:
            raise self.handle_provider_error(error, 'GPT')

    def _get_model_for_provider(self, requested_model: Optional[str], provider: str) -> str:
        """Get the appropriate model for GPT"""
        available_models = [
            'gpt-4o',
            'gpt-4o-mini',
            'gpt-4-turbo',
            'gpt-4',
            'gpt-3.5-turbo'
        ]
        default_model = 'gpt-4o-mini'
        
        if not requested_model:
            return default_model
        
        if requested_model in available_models:
            return requested_model
        
        return default_model

    def handle_provider_error(self, error: Exception, provider: str) -> Exception:
        """Handle and format GPT-specific errors"""
        contextual_message = str(error)
        
        if hasattr(error, 'response') and error.response:
            status = error.response.status_code
            
            if status == 401:
                contextual_message += '\nEnsure your OpenAI API key is valid and has sufficient credits.'
            elif status == 429:
                contextual_message += '\nRate limit exceeded or insufficient quota. Check your OpenAI usage.'
            elif status == 400:
                contextual_message += '\nInvalid request. Check your prompt and parameters.'
        
        provider_error = Exception(contextual_message)
        provider_error.provider = provider
        provider_error.original_error = error
        
        return provider_error
