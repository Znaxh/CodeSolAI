"""
Tests for utils module
"""

import pytest
import sys
from unittest.mock import patch, MagicMock
from rich.console import Console

from codesolai.utils import Utils


class TestUtils:
    """Test cases for Utils class"""

    def test_validate_api_key_claude(self):
        """Test Claude API key validation"""
        # Valid Claude API keys
        assert Utils.validate_api_key('sk-ant-1234567890123456789012345', 'claude') is True
        assert Utils.validate_api_key('sk-ant-abcdefghijklmnopqrstuvwxyz123456789', 'claude') is True
        
        # Invalid Claude API keys
        assert Utils.validate_api_key('invalid-key', 'claude') is False
        assert Utils.validate_api_key('sk-1234567890', 'claude') is False
        assert Utils.validate_api_key('sk-ant-short', 'claude') is False
        assert Utils.validate_api_key('', 'claude') is False
        assert Utils.validate_api_key(None, 'claude') is False

    def test_validate_api_key_gpt(self):
        """Test GPT API key validation"""
        # Valid GPT API keys
        assert Utils.validate_api_key('sk-1234567890123456789012345', 'gpt') is True
        assert Utils.validate_api_key('sk-abcdefghijklmnopqrstuvwxyz123456789', 'gpt') is True
        
        # Invalid GPT API keys
        assert Utils.validate_api_key('invalid-key', 'gpt') is False
        assert Utils.validate_api_key('sk-short', 'gpt') is False
        assert Utils.validate_api_key('sk-ant-1234567890', 'gpt') is False
        assert Utils.validate_api_key('', 'gpt') is False
        assert Utils.validate_api_key(None, 'gpt') is False

    def test_validate_api_key_gemini(self):
        """Test Gemini API key validation"""
        # Valid Gemini API keys
        assert Utils.validate_api_key('AIzaSyC1234567890123456789012345678', 'gemini') is True
        assert Utils.validate_api_key('abcdefghijklmnopqrstuvwxyz1234567890123', 'gemini') is True
        
        # Invalid Gemini API keys
        assert Utils.validate_api_key('short-key', 'gemini') is False
        assert Utils.validate_api_key('key with spaces', 'gemini') is False
        assert Utils.validate_api_key('', 'gemini') is False
        assert Utils.validate_api_key(None, 'gemini') is False

    def test_validate_api_key_unknown_provider(self):
        """Test API key validation for unknown provider"""
        # Should return True for unknown providers with reasonable length
        assert Utils.validate_api_key('some-long-api-key-here', 'unknown') is True
        assert Utils.validate_api_key('short', 'unknown') is False

    def test_sanitize_for_log(self):
        """Test sanitization of sensitive information"""
        text = 'Here is my API key: sk-1234567890 and some other text'
        sanitized = Utils.sanitize_for_log(text)
        assert 'sk-***' in sanitized
        assert 'sk-1234567890' not in sanitized

    def test_sanitize_for_log_multiple_keys(self):
        """Test sanitization with multiple API keys"""
        text = 'Claude: sk-ant-123 and GPT: sk-456789'
        sanitized = Utils.sanitize_for_log(text)
        assert 'sk-***' in sanitized
        assert 'sk-ant-123' not in sanitized
        assert 'sk-456789' not in sanitized

    def test_sanitize_for_log_max_length(self):
        """Test sanitization with max length limit"""
        long_text = 'a' * 200
        sanitized = Utils.sanitize_for_log(long_text, max_length=50)
        assert len(sanitized) <= 53  # 50 + '...'
        assert sanitized.endswith('...')

    def test_sanitize_for_log_empty_text(self):
        """Test sanitization with empty text"""
        assert Utils.sanitize_for_log('') == ''
        assert Utils.sanitize_for_log(None) == ''

    def test_format_error_basic(self):
        """Test basic error formatting"""
        error = Exception('Test error')
        formatted = Utils.format_error(error)
        assert formatted == 'Test error'

    def test_format_error_http_401(self):
        """Test error formatting for 401 HTTP error"""
        # Mock HTTP error
        error = MagicMock()
        error.response = MagicMock()
        error.response.status_code = 401
        
        formatted = Utils.format_error(error, 'Claude')
        assert 'Invalid API key' in formatted

    def test_format_error_http_429(self):
        """Test error formatting for 429 HTTP error"""
        error = MagicMock()
        error.response = MagicMock()
        error.response.status_code = 429
        
        formatted = Utils.format_error(error, 'GPT')
        assert 'Rate limit exceeded' in formatted

    def test_format_error_http_500(self):
        """Test error formatting for 500 HTTP error"""
        error = MagicMock()
        error.response = MagicMock()
        error.response.status_code = 500
        
        formatted = Utils.format_error(error, 'Gemini')
        assert 'server error' in formatted

    def test_format_error_network_error(self):
        """Test error formatting for network error"""
        error = MagicMock()
        error.request = MagicMock()
        # No response attribute to simulate network error
        delattr(error, 'response') if hasattr(error, 'response') else None
        
        formatted = Utils.format_error(error)
        assert 'Network error' in formatted

    @patch('sys.stdin.isatty')
    def test_is_stdin_input_tty(self, mock_isatty):
        """Test stdin detection when input is from TTY"""
        mock_isatty.return_value = True
        assert Utils.is_stdin_input() is False

    @patch('sys.stdin.isatty')
    def test_is_stdin_input_pipe(self, mock_isatty):
        """Test stdin detection when input is piped"""
        mock_isatty.return_value = False
        assert Utils.is_stdin_input() is True

    @pytest.mark.asyncio
    @patch('sys.stdin.isatty')
    @patch('sys.stdin.read')
    async def test_read_stdin_success(self, mock_read, mock_isatty):
        """Test successful stdin reading"""
        mock_isatty.return_value = False
        mock_read.return_value = 'test input\n'
        
        result = await Utils.read_stdin()
        assert result == 'test input'

    @pytest.mark.asyncio
    @patch('sys.stdin.isatty')
    async def test_read_stdin_no_pipe(self, mock_isatty):
        """Test stdin reading when no pipe input"""
        mock_isatty.return_value = True
        
        with pytest.raises(Exception, match="No piped input available"):
            await Utils.read_stdin()

    @patch('codesolai.utils.console')
    def test_log_success(self, mock_console):
        """Test success logging"""
        Utils.log_success('Test success message')
        mock_console.print.assert_called_once()
        args = mock_console.print.call_args[0]
        assert 'Test success message' in args[0]
        assert '✓' in args[0]

    @patch('codesolai.utils.Console')
    def test_log_error(self, mock_console_class):
        """Test error logging"""
        mock_console = MagicMock()
        mock_console_class.return_value = mock_console
        
        Utils.log_error('Test error message')
        mock_console_class.assert_called_once_with(stderr=True)
        mock_console.print.assert_called_once()
        args = mock_console.print.call_args[0]
        assert 'Test error message' in args[0]
        assert '✗' in args[0]

    @patch('codesolai.utils.console')
    def test_log_warning(self, mock_console):
        """Test warning logging"""
        Utils.log_warning('Test warning message')
        mock_console.print.assert_called_once()
        args = mock_console.print.call_args[0]
        assert 'Test warning message' in args[0]
        assert '⚠' in args[0]

    @patch('codesolai.utils.console')
    def test_log_info(self, mock_console):
        """Test info logging"""
        Utils.log_info('Test info message')
        mock_console.print.assert_called_once()
        args = mock_console.print.call_args[0]
        assert 'Test info message' in args[0]
        assert 'ℹ' in args[0]

    def test_format_response(self):
        """Test response formatting"""
        response = "This is a test response"
        provider = "claude"
        
        formatted = Utils.format_response(response, provider)
        assert response in formatted
        assert provider.upper() in formatted

    @patch('codesolai.utils.console')
    def test_display_help(self, mock_console):
        """Test help display"""
        Utils.display_help()
        mock_console.print.assert_called()
        # Check that help content was printed
        call_args = [call[0][0] for call in mock_console.print.call_args_list]
        help_content = ' '.join(str(arg) for arg in call_args)
        assert 'CodeSolAI CLI' in help_content
        assert 'USAGE:' in help_content

    def test_create_spinner(self):
        """Test spinner creation"""
        spinner = Utils.create_spinner('Test message', 'blue')
        assert str(spinner.text) == 'Test message'
        assert spinner.style == 'blue'
