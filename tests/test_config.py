"""
Tests for config module
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from codesolai.config import Config


class TestConfig:
    """Test cases for Config class"""

    def setup_method(self):
        """Set up test fixtures"""
        # Create temporary config file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.test_config_path = Path(self.temp_dir) / '.codesolairc-test'
        
        self.config = Config()
        self.original_config_path = self.config.config_path
        self.config.config_path = self.test_config_path

    def teardown_method(self):
        """Clean up test fixtures"""
        # Clean up test config file
        if self.test_config_path.exists():
            self.test_config_path.unlink()
        
        # Restore original config path
        self.config.config_path = self.original_config_path

    def test_load_default_configuration(self):
        """Test loading default configuration when file does not exist"""
        loaded_config = self.config.load()
        
        assert loaded_config['defaultProvider'] is None
        assert loaded_config['timeout'] == 30000
        assert 'agent' in loaded_config
        assert loaded_config['agent']['enabled'] is False
        assert loaded_config['agent']['confirmationEnabled'] is False
        assert loaded_config['agent']['autoApprove'] is True

    def test_load_configuration_from_file(self):
        """Test loading configuration from existing file"""
        test_config = {
            'defaultProvider': 'claude',
            'timeout': 60000,
            'agent': {
                'enabled': True,
                'maxActionsPerPrompt': 5
            }
        }
        
        # Write test config to file
        with open(self.test_config_path, 'w') as f:
            json.dump(test_config, f)
        
        loaded_config = self.config.load()
        
        assert loaded_config['defaultProvider'] == 'claude'
        assert loaded_config['timeout'] == 60000
        assert loaded_config['agent']['enabled'] is True
        assert loaded_config['agent']['maxActionsPerPrompt'] == 5
        # Should preserve defaults for missing keys
        assert loaded_config['agent']['autoApprove'] is True

    def test_load_invalid_json(self):
        """Test loading configuration with invalid JSON"""
        # Write invalid JSON to file
        with open(self.test_config_path, 'w') as f:
            f.write('{ invalid json }')
        
        # Should return default config
        loaded_config = self.config.load()
        assert loaded_config == self.config.default_config

    def test_save_configuration(self):
        """Test saving configuration to file"""
        test_config = {
            'defaultProvider': 'gpt',
            'timeout': 45000
        }
        
        result = self.config.save(test_config)
        assert result is True
        assert self.test_config_path.exists()
        
        # Verify saved content
        with open(self.test_config_path, 'r') as f:
            saved_config = json.load(f)
        
        assert saved_config['defaultProvider'] == 'gpt'
        assert saved_config['timeout'] == 45000

    def test_validate_config_valid(self):
        """Test configuration validation with valid config"""
        valid_config = {
            'defaultProvider': 'claude',
            'timeout': 30000,
            'maxRetries': 3,
            'outputFormat': 'text'
        }
        
        # Should not raise exception
        self.config.validate_config(valid_config)

    def test_validate_config_invalid_provider(self):
        """Test configuration validation with invalid provider"""
        invalid_config = {
            'defaultProvider': 'invalid_provider'
        }
        
        with pytest.raises(ValueError, match="Invalid default provider"):
            self.config.validate_config(invalid_config)

    def test_validate_config_invalid_timeout(self):
        """Test configuration validation with invalid timeout"""
        invalid_config = {
            'timeout': 500  # Too low
        }
        
        with pytest.raises(ValueError, match="Timeout must be an integer"):
            self.config.validate_config(invalid_config)

    def test_validate_config_invalid_retries(self):
        """Test configuration validation with invalid retries"""
        invalid_config = {
            'maxRetries': -1  # Negative
        }
        
        with pytest.raises(ValueError, match="Max retries must be a non-negative integer"):
            self.config.validate_config(invalid_config)

    def test_validate_config_invalid_output_format(self):
        """Test configuration validation with invalid output format"""
        invalid_config = {
            'outputFormat': 'invalid_format'
        }
        
        with pytest.raises(ValueError, match="Invalid output format"):
            self.config.validate_config(invalid_config)

    def test_get_config_with_cli_overrides(self):
        """Test getting configuration with CLI option overrides"""
        # Save base config
        base_config = {'defaultProvider': 'claude', 'timeout': 30000}
        self.config.save(base_config)
        
        # Get config with CLI overrides
        cli_options = {'defaultProvider': 'gpt', 'timeout': 60000}
        final_config = self.config.get_config(cli_options)
        
        assert final_config['defaultProvider'] == 'gpt'
        assert final_config['timeout'] == 60000

    def test_create_example(self):
        """Test creating example configuration file"""
        example_path = self.config.config_path.parent / '.codesolairc.example'
        
        result = self.config.create_example()
        assert result is True
        
        # Clean up
        if example_path.exists():
            example_path.unlink()

    def test_display_configuration(self, capsys):
        """Test displaying current configuration"""
        test_config = {'defaultProvider': 'claude', 'timeout': 30000}
        self.config.save(test_config)
        
        self.config.display()
        
        captured = capsys.readouterr()
        assert 'Current Configuration' in captured.out
        assert 'claude' in captured.out

    def test_exists_true(self):
        """Test config file existence check when file exists"""
        # Create config file
        self.test_config_path.touch()
        
        assert self.config.exists() is True

    def test_exists_false(self):
        """Test config file existence check when file doesn't exist"""
        assert self.config.exists() is False

    def test_get_config_path(self):
        """Test getting config file path"""
        path = self.config.get_config_path()
        assert path == self.test_config_path

    def test_reset_existing_file(self):
        """Test resetting configuration when file exists"""
        # Create config file
        self.test_config_path.touch()
        
        result = self.config.reset()
        assert result is True
        assert not self.test_config_path.exists()

    def test_reset_no_file(self):
        """Test resetting configuration when file doesn't exist"""
        result = self.config.reset()
        assert result is True

    def test_set_simple_value(self):
        """Test setting a simple configuration value"""
        result = self.config.set('defaultProvider', 'claude')
        assert result is True
        
        config = self.config.load()
        assert config['defaultProvider'] == 'claude'

    def test_set_nested_value(self):
        """Test setting a nested configuration value"""
        result = self.config.set('agent.enabled', True)
        assert result is True
        
        config = self.config.load()
        assert config['agent']['enabled'] is True

    def test_get_simple_value(self):
        """Test getting a simple configuration value"""
        self.config.save({'defaultProvider': 'gpt'})
        
        value = self.config.get('defaultProvider')
        assert value == 'gpt'

    def test_get_nested_value(self):
        """Test getting a nested configuration value"""
        self.config.save({'agent': {'enabled': True}})
        
        value = self.config.get('agent.enabled')
        assert value is True

    def test_get_nonexistent_value(self):
        """Test getting a non-existent configuration value"""
        value = self.config.get('nonexistent.key')
        assert value is None

    def test_set_multiple_values(self):
        """Test setting multiple configuration values"""
        settings = {
            'defaultProvider': 'claude',
            'timeout': 45000,
            'agent.enabled': True
        }
        
        result = self.config.set_multiple(settings)
        assert result is True
        
        config = self.config.load()
        assert config['defaultProvider'] == 'claude'
        assert config['timeout'] == 45000
        assert config['agent']['enabled'] is True

    def test_set_api_key_valid(self):
        """Test setting API key for valid provider"""
        result = self.config.set_api_key('claude', 'sk-ant-1234567890123456789012345')
        assert result is True
        
        config = self.config.load()
        assert config['apiKeys']['claude'] == 'sk-ant-1234567890123456789012345'

    def test_set_api_key_invalid_provider(self):
        """Test setting API key for invalid provider"""
        result = self.config.set_api_key('invalid', 'some-key')
        assert result is False

    def test_set_api_key_invalid_format(self):
        """Test setting API key with invalid format"""
        result = self.config.set_api_key('claude', 'invalid-key')
        assert result is False

    @patch.dict('os.environ', {'CLAUDE_API_KEY': 'env-key-123'})
    def test_get_api_key_from_env(self):
        """Test getting API key from environment variable"""
        key = self.config.get_api_key('claude')
        assert key == 'env-key-123'

    def test_get_api_key_from_config(self):
        """Test getting API key from config file"""
        self.config.save({'apiKeys': {'gpt': 'config-key-456'}})
        
        key = self.config.get_api_key('gpt')
        assert key == 'config-key-456'

    def test_get_api_key_not_found(self):
        """Test getting API key when not found"""
        key = self.config.get_api_key('gemini')
        assert key is None

    def test_deep_merge(self):
        """Test deep merging of dictionaries"""
        target = {
            'a': 1,
            'b': {'c': 2, 'd': 3},
            'e': 4
        }
        
        source = {
            'b': {'c': 20, 'f': 6},
            'g': 7
        }
        
        result = self.config.deep_merge(target, source)
        
        assert result['a'] == 1
        assert result['b']['c'] == 20  # Overridden
        assert result['b']['d'] == 3   # Preserved
        assert result['b']['f'] == 6   # Added
        assert result['e'] == 4
        assert result['g'] == 7
