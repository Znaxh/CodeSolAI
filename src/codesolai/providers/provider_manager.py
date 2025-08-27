"""
LLM Provider implementations for Claude, Gemini, and GPT
"""

import asyncio
from typing import Dict, Any, Optional, List
from .claude_provider import ClaudeProvider
from .gemini_provider import GeminiProvider
from .gpt_provider import GPTProvider
from ..utils import Utils


class ProviderManager:
    """Manager for different LLM providers"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        self.timeout = config.get('timeout', 30000) / 1000  # Convert to seconds
        self.max_retries = config.get('maxRetries', 3)
        
        # Initialize providers
        self.providers = {
            'claude': ClaudeProvider(timeout=self.timeout, max_retries=self.max_retries),
            'gpt': GPTProvider(timeout=self.timeout, max_retries=self.max_retries),
            'gemini': GeminiProvider(timeout=self.timeout, max_retries=self.max_retries)
        }

    async def call(self, provider: str, api_key: str, prompt: str, options: Optional[Dict[str, Any]] = None) -> str:
        """Generic method to call any provider"""
        options = options or {}
        
        # Validate inputs
        if not provider or not api_key or not prompt:
            raise ValueError('Provider, API key, and prompt are required')

        if not Utils.validate_api_key(api_key, provider):
            raise ValueError(f'Invalid API key format for {provider}')

        trimmed_prompt = prompt.strip()
        if not trimmed_prompt:
            raise ValueError('Prompt cannot be empty')

        # Get the provider instance
        provider_lower = provider.lower()
        if provider_lower not in self.providers:
            supported = ', '.join(self.providers.keys())
            raise ValueError(f'Unsupported provider: {provider}. Supported providers: {supported}')

        # Call the appropriate provider
        provider_instance = self.providers[provider_lower]
        return await provider_instance.call(api_key, trimmed_prompt, options)

    def get_available_models(self, provider: str) -> List[str]:
        """Get available models for each provider"""
        models = {
            'claude': [
                'claude-3-5-sonnet-20241022',
                'claude-3-5-haiku-20241022',
                'claude-3-opus-20240229',
                'claude-3-sonnet-20240229',
                'claude-3-haiku-20240307'
            ],
            'gpt': [
                'gpt-4o',
                'gpt-4o-mini',
                'gpt-4-turbo',
                'gpt-4',
                'gpt-3.5-turbo'
            ],
            'gemini': [
                'gemini-1.5-pro',
                'gemini-1.5-flash',
                'gemini-1.5-flash-8b',
                'gemini-1.0-pro'
            ]
        }
        return models.get(provider, [])

    def get_default_model(self, provider: str) -> Optional[str]:
        """Get default model for each provider"""
        defaults = {
            'claude': 'claude-3-5-sonnet-20241022',
            'gpt': 'gpt-4o-mini',
            'gemini': 'gemini-1.5-flash'
        }
        return defaults.get(provider)

    def validate_model_for_provider(self, model: str, provider: str) -> bool:
        """Validate if a model is compatible with a provider"""
        if not model or not provider:
            return False

        available_models = self.get_available_models(provider)
        return model in available_models

    def get_model_for_provider(self, requested_model: Optional[str], provider: str) -> str:
        """Get the appropriate model for a provider, with validation"""
        # If no model requested, use provider default
        if not requested_model:
            return self.get_default_model(provider)

        # Validate requested model is compatible with provider
        if self.validate_model_for_provider(requested_model, provider):
            return requested_model

        # If invalid model requested, log warning and use default
        default_model = self.get_default_model(provider)
        Utils.log_warning(f"Model '{requested_model}' is not compatible with provider '{provider}'")
        Utils.log_info(f"Using default model '{default_model}' instead")
        
        return default_model

    async def test_api_key(self, provider: str, api_key: str) -> bool:
        """Test API key validity for a provider"""
        try:
            test_prompt = 'Hello, please respond with "API key is working"'
            response = await self.call(provider, api_key, test_prompt)
            return 'api key is working' in response.lower() or len(response) > 0
        except Exception:
            return False

    def get_supported_providers(self) -> List[str]:
        """Get list of supported providers"""
        return list(self.providers.keys())

    def get_provider_info(self, provider: str) -> Dict[str, Any]:
        """Get information about a specific provider"""
        if provider not in self.providers:
            raise ValueError(f'Unknown provider: {provider}')
        
        return {
            'name': provider,
            'models': self.get_available_models(provider),
            'default_model': self.get_default_model(provider),
            'supports_streaming': False,  # Can be extended later
            'supports_function_calling': provider in ['gpt', 'claude']  # Basic info
        }
