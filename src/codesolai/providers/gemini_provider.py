"""
Gemini (Google) provider implementation
"""

import asyncio
from typing import Dict, Any, Optional
import httpx
from .base_provider import BaseProvider


class GeminiProvider(BaseProvider):
    """Gemini (Google) API provider"""

    def __init__(self, timeout: float = 30.0, max_retries: int = 3):
        super().__init__(timeout, max_retries)
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    async def call(self, api_key: str, prompt: str, options: Optional[Dict[str, Any]] = None) -> str:
        """Make API call to Gemini (Google)"""
        options = options or {}
        model = self._get_model_for_provider(options.get('model'), 'gemini')
        url = f"{self.base_url}/models/{model}:generateContent?key={api_key}"
        
        headers = {
            'Content-Type': 'application/json'
        }

        data = {
            'contents': [
                {
                    'parts': [
                        {
                            'text': prompt
                        }
                    ]
                }
            ],
            'generationConfig': {
                'temperature': options.get('temperature', 0.7),
                'topK': options.get('topK', 40),
                'topP': options.get('topP', 0.95),
                'maxOutputTokens': options.get('maxTokens', 4000)
            }
        }

        try:
            response_data = await self.make_request(url, headers, data)

            # Extract content from Gemini's response format
            if (response_data and 
                'candidates' in response_data and 
                response_data['candidates'] and 
                len(response_data['candidates']) > 0):
                
                candidate = response_data['candidates'][0]
                if (candidate.get('content') and 
                    candidate['content'].get('parts') and 
                    len(candidate['content']['parts']) > 0):
                    return candidate['content']['parts'][0]['text']
            
            raise Exception('Unexpected response format from Gemini API')

        except Exception as error:
            raise self.handle_provider_error(error, 'Gemini')

    def _get_model_for_provider(self, requested_model: Optional[str], provider: str) -> str:
        """Get the appropriate model for Gemini"""
        available_models = [
            'gemini-1.5-pro',
            'gemini-1.5-flash',
            'gemini-1.5-flash-8b',
            'gemini-1.0-pro'
        ]
        default_model = 'gemini-1.5-flash'
        
        if not requested_model:
            return default_model
        
        if requested_model in available_models:
            return requested_model
        
        return default_model

    def handle_provider_error(self, error: Exception, provider: str) -> Exception:
        """Handle and format Gemini-specific errors"""
        contextual_message = str(error)
        
        if hasattr(error, 'response') and error.response:
            status = error.response.status_code
            
            if status == 400:
                contextual_message += '\nCheck that your Google API key is enabled for the Gemini API.'
            elif status == 401:
                contextual_message += '\nInvalid API key. Ensure your Google API key is correct.'
            elif status == 429:
                contextual_message += '\nRate limit exceeded. Please wait before making more requests.'
        
        provider_error = Exception(contextual_message)
        provider_error.provider = provider
        provider_error.original_error = error
        
        return provider_error
