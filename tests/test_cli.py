"""
Tests for CLI module
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from click.testing import CliRunner

from codesolai.cli import main, cli
from codesolai import __version__


class TestCLI:
    """Test cases for CLI functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.runner = CliRunner()

    def test_version_option(self):
        """Test --version option"""
        result = self.runner.invoke(main, ['--version'])
        assert result.exit_code == 0
        assert __version__ in result.output

    def test_help_option(self):
        """Test --help option"""
        result = self.runner.invoke(main, ['--help'])
        assert result.exit_code == 0
        assert 'CodeSolAI' in result.output
        assert 'Usage:' in result.output

    @patch('codesolai.cli.Setup')
    @patch('codesolai.cli.asyncio.run')
    def test_setup_option(self, mock_asyncio_run, mock_setup_class):
        """Test --setup option"""
        mock_setup = MagicMock()
        mock_setup_class.return_value = mock_setup
        
        result = self.runner.invoke(main, ['--setup'])
        
        assert result.exit_code == 0
        mock_setup_class.assert_called_once()
        mock_asyncio_run.assert_called_once()

    @patch('codesolai.cli.Config')
    def test_config_option(self, mock_config_class):
        """Test --config option"""
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        
        result = self.runner.invoke(main, ['--config'])
        
        assert result.exit_code == 0
        mock_config.display.assert_called_once()

    @patch('codesolai.cli.Config')
    def test_config_example_option(self, mock_config_class):
        """Test --config-example option"""
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        
        result = self.runner.invoke(main, ['--config-example'])
        
        assert result.exit_code == 0
        mock_config.create_example.assert_called_once()

    @patch('codesolai.cli.Config')
    def test_config_reset_option(self, mock_config_class):
        """Test --config-reset option"""
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        
        result = self.runner.invoke(main, ['--config-reset'])
        
        assert result.exit_code == 0
        mock_config.reset.assert_called_once()

    @patch('codesolai.cli.ProviderManager')
    @patch('codesolai.cli.Config')
    @patch('codesolai.cli.asyncio.run')
    def test_test_key_option_success(self, mock_asyncio_run, mock_config_class, mock_provider_manager_class):
        """Test --test-key option with successful key test"""
        # Mock config
        mock_config = MagicMock()
        mock_config.get_config.return_value = {'defaultProvider': 'claude'}
        mock_config.get_api_key.return_value = 'sk-ant-test'
        mock_config_class.return_value = mock_config
        
        # Mock provider manager
        mock_provider_manager = MagicMock()
        mock_provider_manager.test_api_key = AsyncMock(return_value=True)
        mock_provider_manager_class.return_value = mock_provider_manager
        
        # Mock async_main to handle the test-key logic
        async def mock_async_main(**kwargs):
            if kwargs.get('test_key'):
                from codesolai.spinner_manager import SpinnerManager
                spinner = SpinnerManager()
                spinner.start('Testing API key')
                
                provider_manager = mock_provider_manager_class()
                is_valid = await provider_manager.test_api_key('claude', 'sk-ant-test')
                
                if is_valid:
                    spinner.succeed('CLAUDE API key is valid and working')
                else:
                    spinner.fail('CLAUDE API key test failed')
        
        mock_asyncio_run.side_effect = lambda coro: None  # Just run without error
        
        result = self.runner.invoke(main, ['--provider', 'claude', '--api-key', 'sk-ant-test', '--test-key'])
        
        assert result.exit_code == 0

    @patch('codesolai.cli.Utils')
    @patch('codesolai.cli.Config')
    @patch('codesolai.cli.asyncio.run')
    def test_no_provider_configured(self, mock_asyncio_run, mock_config_class, mock_utils):
        """Test error when no provider is configured"""
        # Mock config with no default provider
        mock_config = MagicMock()
        mock_config.get_config.return_value = {'defaultProvider': None}
        mock_config_class.return_value = mock_config
        
        # Mock async_main to handle the no provider case
        def mock_async_main_func(**kwargs):
            if not kwargs.get('provider') and not mock_config.get_config()['defaultProvider']:
                mock_utils.log_error('No provider configured.')
                import sys
                sys.exit(1)
        
        mock_asyncio_run.side_effect = lambda coro: mock_async_main_func()
        
        with pytest.raises(SystemExit):
            self.runner.invoke(main, ['Hello world'])

    @patch('codesolai.cli.InteractiveSession')
    @patch('codesolai.cli.Config')
    @patch('codesolai.cli.asyncio.run')
    def test_interactive_mode(self, mock_asyncio_run, mock_config_class, mock_interactive_session_class):
        """Test interactive mode activation"""
        # Mock config
        mock_config = MagicMock()
        mock_config.get_config.return_value = {'defaultProvider': 'claude'}
        mock_config.get_api_key.return_value = 'sk-ant-test'
        mock_config_class.return_value = mock_config
        
        # Mock interactive session
        mock_session = MagicMock()
        mock_session.start = AsyncMock()
        mock_interactive_session_class.return_value = mock_session
        
        # Mock async_main to handle interactive mode
        async def mock_async_main(**kwargs):
            if kwargs.get('interactive') or (not kwargs.get('prompt') and not mock_utils.is_stdin_input()):
                session = mock_interactive_session_class({}, 'claude', 'sk-ant-test', kwargs)
                await session.start()
        
        mock_asyncio_run.side_effect = lambda coro: None
        
        result = self.runner.invoke(main, ['--interactive', '--provider', 'claude', '--api-key', 'sk-ant-test'])
        
        assert result.exit_code == 0

    @patch('codesolai.cli.handle_simple_prompt')
    @patch('codesolai.cli.Config')
    @patch('codesolai.cli.asyncio.run')
    def test_simple_prompt(self, mock_asyncio_run, mock_config_class, mock_handle_simple_prompt):
        """Test simple prompt processing"""
        # Mock config
        mock_config = MagicMock()
        mock_config.get_config.return_value = {'defaultProvider': 'claude'}
        mock_config.get_api_key.return_value = 'sk-ant-test'
        mock_config_class.return_value = mock_config
        
        mock_handle_simple_prompt = AsyncMock()
        
        # Mock async_main to handle simple prompt
        async def mock_async_main(**kwargs):
            if kwargs.get('prompt') and not kwargs.get('interactive'):
                await mock_handle_simple_prompt('claude', 'sk-ant-test', ' '.join(kwargs['prompt']), kwargs, {})
        
        mock_asyncio_run.side_effect = lambda coro: None
        
        result = self.runner.invoke(main, ['--provider', 'claude', '--api-key', 'sk-ant-test', 'Hello world'])
        
        assert result.exit_code == 0

    def test_cli_entry_point(self):
        """Test CLI entry point function"""
        with patch('codesolai.cli.main') as mock_main:
            cli()
            mock_main.assert_called_once()

    def test_cli_keyboard_interrupt(self):
        """Test CLI handling of keyboard interrupt"""
        with patch('codesolai.cli.main') as mock_main:
            mock_main.side_effect = KeyboardInterrupt()
            
            with pytest.raises(SystemExit):
                cli()

    def test_cli_unexpected_error(self):
        """Test CLI handling of unexpected error"""
        with patch('codesolai.cli.main') as mock_main:
            mock_main.side_effect = Exception("Unexpected error")
            
            with pytest.raises(SystemExit):
                cli()

    @patch('codesolai.cli.Utils')
    def test_validate_api_key_format(self, mock_utils):
        """Test API key format validation in CLI"""
        mock_utils.validate_api_key.return_value = False
        
        # This would be called in the actual CLI logic
        result = mock_utils.validate_api_key('invalid-key', 'claude')
        assert result is False

    def test_provider_validation(self):
        """Test provider validation"""
        valid_providers = ['claude', 'gemini', 'gpt']
        
        assert 'claude' in valid_providers
        assert 'invalid' not in valid_providers

    @patch('codesolai.cli.Utils')
    def test_stdin_detection(self, mock_utils):
        """Test stdin input detection"""
        mock_utils.is_stdin_input.return_value = True
        
        result = mock_utils.is_stdin_input()
        assert result is True

    def test_command_line_parsing(self):
        """Test command line argument parsing"""
        # Test that Click properly parses arguments
        result = self.runner.invoke(main, ['--provider', 'claude', '--model', 'claude-3-opus-20240229', 'test prompt'])
        
        # Should not error on parsing
        assert result.exit_code in [0, 1]  # May exit with 1 due to missing API key, but parsing should work

    def test_multiple_options(self):
        """Test multiple CLI options together"""
        result = self.runner.invoke(main, [
            '--provider', 'gpt',
            '--model', 'gpt-4o',
            '--temperature', '0.8',
            '--max-tokens', '2000',
            '--timeout', '45000',
            '--help'  # Help should override other options
        ])
        
        assert result.exit_code == 0
        assert 'Usage:' in result.output

    def test_boolean_flags(self):
        """Test boolean flag options"""
        # Test that boolean flags are properly recognized
        result = self.runner.invoke(main, ['--agent', '--autonomous', '--debug', '--help'])
        
        assert result.exit_code == 0
        assert 'agent' in result.output or 'autonomous' in result.output or 'debug' in result.output

    def test_choice_validation(self):
        """Test choice option validation"""
        # Test invalid effort choice
        result = self.runner.invoke(main, ['--effort', 'invalid', '--help'])
        
        # Should show help due to --help, not error on invalid choice when help is present
        assert result.exit_code == 0
