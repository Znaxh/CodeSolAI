"""
Tests for provider modules
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from codesolai.providers.provider_manager import ProviderManager
from codesolai.providers.claude_provider import ClaudeProvider
from codesolai.providers.gpt_provider import GPTProvider
from codesolai.providers.gemini_provider import GeminiProvider


class TestProviderManager:
    """Test cases for ProviderManager class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.manager = ProviderManager()

    @pytest.mark.asyncio
    async def test_call_claude_success(self):
        """Test successful call to Claude provider"""
        with patch.object(self.manager.providers['claude'], 'call', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = "Hello from Claude!"

            result = await self.manager.call('claude', 'sk-ant-1234567890123456789012345', 'Hello')

            assert result == "Hello from Claude!"
            mock_call.assert_called_once_with('sk-ant-1234567890123456789012345', 'Hello', {})

    @pytest.mark.asyncio
    async def test_call_invalid_provider(self):
        """Test call with invalid provider"""
        with pytest.raises(ValueError, match="Invalid API key format"):
            await self.manager.call('invalid', 'key', 'prompt')

    @pytest.mark.asyncio
    async def test_call_empty_prompt(self):
        """Test call with empty prompt"""
        with pytest.raises(ValueError, match="Provider, API key, and prompt are required"):
            await self.manager.call('claude', 'sk-ant-1234567890123456789012345', '')

    @pytest.mark.asyncio
    async def test_call_invalid_api_key(self):
        """Test call with invalid API key"""
        with pytest.raises(ValueError, match="Invalid API key format"):
            await self.manager.call('claude', 'invalid-key', 'Hello')

    def test_get_available_models(self):
        """Test getting available models for providers"""
        claude_models = self.manager.get_available_models('claude')
        assert 'claude-3-5-sonnet-20241022' in claude_models
        
        gpt_models = self.manager.get_available_models('gpt')
        assert 'gpt-4o' in gpt_models
        
        gemini_models = self.manager.get_available_models('gemini')
        assert 'gemini-1.5-pro' in gemini_models

    def test_get_default_model(self):
        """Test getting default model for providers"""
        assert self.manager.get_default_model('claude') == 'claude-3-5-sonnet-20241022'
        assert self.manager.get_default_model('gpt') == 'gpt-4o-mini'
        assert self.manager.get_default_model('gemini') == 'gemini-1.5-flash'

    def test_validate_model_for_provider(self):
        """Test model validation for providers"""
        assert self.manager.validate_model_for_provider('claude-3-5-sonnet-20241022', 'claude') is True
        assert self.manager.validate_model_for_provider('gpt-4o', 'gpt') is True
        assert self.manager.validate_model_for_provider('gemini-1.5-pro', 'gemini') is True
        
        # Invalid combinations
        assert self.manager.validate_model_for_provider('gpt-4o', 'claude') is False
        assert self.manager.validate_model_for_provider('invalid-model', 'gpt') is False

    def test_get_model_for_provider_default(self):
        """Test getting model when none requested"""
        model = self.manager.get_model_for_provider(None, 'claude')
        assert model == 'claude-3-5-sonnet-20241022'

    def test_get_model_for_provider_valid(self):
        """Test getting model when valid model requested"""
        model = self.manager.get_model_for_provider('claude-3-opus-20240229', 'claude')
        assert model == 'claude-3-opus-20240229'

    def test_get_model_for_provider_invalid(self):
        """Test getting model when invalid model requested"""
        with patch('codesolai.providers.provider_manager.Utils') as mock_utils:
            model = self.manager.get_model_for_provider('invalid-model', 'claude')
            assert model == 'claude-3-5-sonnet-20241022'  # Should return default
            mock_utils.log_warning.assert_called()

    @pytest.mark.asyncio
    async def test_test_api_key_success(self):
        """Test API key testing with successful response"""
        with patch.object(self.manager, 'call', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = "API key is working"
            
            result = await self.manager.test_api_key('claude', 'sk-ant-test')
            assert result is True

    @pytest.mark.asyncio
    async def test_test_api_key_failure(self):
        """Test API key testing with failure"""
        with patch.object(self.manager, 'call', new_callable=AsyncMock) as mock_call:
            mock_call.side_effect = Exception("Invalid API key")
            
            result = await self.manager.test_api_key('claude', 'sk-ant-test')
            assert result is False

    def test_get_supported_providers(self):
        """Test getting list of supported providers"""
        providers = self.manager.get_supported_providers()
        assert 'claude' in providers
        assert 'gpt' in providers
        assert 'gemini' in providers

    def test_get_provider_info(self):
        """Test getting provider information"""
        info = self.manager.get_provider_info('claude')
        assert info['name'] == 'claude'
        assert 'models' in info
        assert 'default_model' in info
        assert info['supports_function_calling'] is True

    def test_get_provider_info_invalid(self):
        """Test getting info for invalid provider"""
        with pytest.raises(ValueError, match="Unknown provider"):
            self.manager.get_provider_info('invalid')


class TestClaudeProvider:
    """Test cases for ClaudeProvider class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.provider = ClaudeProvider()

    @pytest.mark.asyncio
    async def test_call_success(self):
        """Test successful Claude API call"""
        mock_response_data = {
            'content': [{'text': 'Hello from Claude!'}]
        }
        
        with patch.object(self.provider, 'make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response_data
            
            result = await self.provider.call('sk-ant-test', 'Hello')
            
            assert result == 'Hello from Claude!'
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_call_with_options(self):
        """Test Claude API call with options"""
        mock_response_data = {
            'content': [{'text': 'Response with options'}]
        }
        
        options = {
            'model': 'claude-3-opus-20240229',
            'maxTokens': 2000,
            'temperature': 0.8
        }
        
        with patch.object(self.provider, 'make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response_data
            
            result = await self.provider.call('sk-ant-test', 'Hello', options)
            
            assert result == 'Response with options'
            # Verify request was made with correct data
            call_args = mock_request.call_args
            data = call_args[0][2]  # Third argument is data
            assert data['model'] == 'claude-3-opus-20240229'
            assert data['max_tokens'] == 2000
            assert data['temperature'] == 0.8

    @pytest.mark.asyncio
    async def test_call_unexpected_response_format(self):
        """Test Claude API call with unexpected response format"""
        mock_response_data = {'unexpected': 'format'}
        
        with patch.object(self.provider, 'make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response_data
            
            with pytest.raises(Exception, match="Unexpected response format"):
                await self.provider.call('sk-ant-test', 'Hello')

    def test_get_model_for_provider_default(self):
        """Test getting default model"""
        model = self.provider._get_model_for_provider(None, 'claude')
        assert model == 'claude-3-5-sonnet-20241022'

    def test_get_model_for_provider_valid(self):
        """Test getting valid model"""
        model = self.provider._get_model_for_provider('claude-3-opus-20240229', 'claude')
        assert model == 'claude-3-opus-20240229'

    def test_get_model_for_provider_invalid(self):
        """Test getting invalid model returns default"""
        model = self.provider._get_model_for_provider('invalid-model', 'claude')
        assert model == 'claude-3-5-sonnet-20241022'

    def test_handle_provider_error_401(self):
        """Test error handling for 401 status"""
        error = MagicMock()
        error.response = MagicMock()
        error.response.status_code = 401
        
        result = self.provider.handle_provider_error(error, 'Claude')
        
        assert result.provider == 'Claude'
        assert 'Anthropic API key' in str(result)

    def test_handle_provider_error_429(self):
        """Test error handling for 429 status"""
        error = MagicMock()
        error.response = MagicMock()
        error.response.status_code = 429
        
        result = self.provider.handle_provider_error(error, 'Claude')
        
        assert 'Rate limit exceeded' in str(result)


class TestGPTProvider:
    """Test cases for GPTProvider class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.provider = GPTProvider()

    @pytest.mark.asyncio
    async def test_call_success(self):
        """Test successful GPT API call"""
        mock_response_data = {
            'choices': [{'message': {'content': 'Hello from GPT!'}}]
        }
        
        with patch.object(self.provider, 'make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response_data
            
            result = await self.provider.call('sk-test', 'Hello')
            
            assert result == 'Hello from GPT!'

    def test_get_model_for_provider_default(self):
        """Test getting default GPT model"""
        model = self.provider._get_model_for_provider(None, 'gpt')
        assert model == 'gpt-4o-mini'


class TestGeminiProvider:
    """Test cases for GeminiProvider class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.provider = GeminiProvider()

    @pytest.mark.asyncio
    async def test_call_success(self):
        """Test successful Gemini API call"""
        mock_response_data = {
            'candidates': [{
                'content': {
                    'parts': [{'text': 'Hello from Gemini!'}]
                }
            }]
        }
        
        with patch.object(self.provider, 'make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response_data
            
            result = await self.provider.call('test-key', 'Hello')
            
            assert result == 'Hello from Gemini!'

    def test_get_model_for_provider_default(self):
        """Test getting default Gemini model"""
        model = self.provider._get_model_for_provider(None, 'gemini')
        assert model == 'gemini-1.5-flash'
