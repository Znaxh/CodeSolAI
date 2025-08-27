"""
Configuration management for .codesolairc files
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union
from .utils import Utils


class Config:
    """Configuration management for CodeSolAI"""

    def __init__(self):
        self.config_path = Path.home() / '.codesolairc'
        self.default_config = {
            "defaultProvider": None,
            "timeout": 30000,
            "maxRetries": 3,
            "outputFormat": "text",
            # Agent-specific settings
            "agent": {
                "enabled": False,  # Changed default to false
                "confirmationEnabled": False,  # No confirmation required for tool execution
                "autoApprove": True,  # Always auto-approve tool and command execution
                "maxActionsPerPrompt": 10,
                "autonomous": False,
                "effort": "medium",
                "maxIterations": 10,
                "toolSecurity": {
                    "allowedCommands": [
                        "npm", "node", "git", "ls", "pwd", "cat", "echo", "mkdir", "touch",
                        "grep", "find", "curl", "wget", "which", "whereis", "ps", "python",
                        "pip", "poetry", "uv", "pytest", "black", "isort", "mypy"
                    ],
                    "blockedCommands": [
                        "rm", "rmdir", "del", "format", "fdisk", "mkfs", "dd", "sudo", "su",
                        "chmod", "chown", "passwd", "shutdown", "reboot", "halt", "init"
                    ],
                    "maxExecutionTime": 30000,
                    "maxOutputSize": 1048576
                }
            },
            # API keys (optional - can use env vars instead)
            "apiKeys": {}
        }

    def deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        result = target.copy()
        
        for key, value in source.items():
            if (key in result and 
                isinstance(result[key], dict) and 
                isinstance(value, dict)):
                result[key] = self.deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result

    def load(self) -> Dict[str, Any]:
        """Load configuration from .codesolairc file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                
                # Deep merge with defaults to preserve nested default values
                config = self.deep_merge(self.default_config, user_config)
                
                # Validate configuration
                self.validate_config(config)
                
                return config
        except json.JSONDecodeError:
            Utils.log_warning(f"Invalid JSON in config file: {self.config_path}")
            Utils.log_info("Using default configuration")
        except Exception as error:
            Utils.log_warning(f"Could not read config file: {error}")
            Utils.log_info("Using default configuration")
        
        return self.default_config.copy()

    def save(self, config: Dict[str, Any]) -> bool:
        """Save configuration to .codesolairc file"""
        try:
            config_to_save = self.deep_merge(self.default_config, config)
            self.validate_config(config_to_save)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=2)
            
            Utils.log_success(f"Configuration saved to {self.config_path}")
            return True
        except Exception as error:
            Utils.log_error(f"Could not save config file: {error}")
            return False

    def validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration object"""
        valid_providers = ['claude', 'gemini', 'gpt']
        valid_output_formats = ['text', 'json', 'markdown']

        if config.get('defaultProvider') and config['defaultProvider'] not in valid_providers:
            raise ValueError(f"Invalid default provider: {config['defaultProvider']}. "
                           f"Must be one of: {', '.join(valid_providers)}")

        if config.get('timeout') and (not isinstance(config['timeout'], int) or config['timeout'] < 1000):
            raise ValueError('Timeout must be an integer >= 1000 milliseconds')

        if config.get('maxRetries') and (not isinstance(config['maxRetries'], int) or config['maxRetries'] < 0):
            raise ValueError('Max retries must be a non-negative integer')

        if config.get('outputFormat') and config['outputFormat'] not in valid_output_formats:
            raise ValueError(f"Invalid output format: {config['outputFormat']}. "
                           f"Must be one of: {', '.join(valid_output_formats)}")

        # Validate agent settings
        if config.get('agent'):
            agent = config['agent']
            
            if (agent.get('maxActionsPerPrompt') is not None and 
                (not isinstance(agent['maxActionsPerPrompt'], int) or agent['maxActionsPerPrompt'] < 1)):
                raise ValueError('Agent maxActionsPerPrompt must be a positive integer')

            if agent.get('toolSecurity'):
                security = agent['toolSecurity']
                
                if (security.get('maxExecutionTime') and 
                    (not isinstance(security['maxExecutionTime'], int) or security['maxExecutionTime'] < 1000)):
                    raise ValueError('Tool security maxExecutionTime must be >= 1000 milliseconds')

                if (security.get('maxOutputSize') and 
                    (not isinstance(security['maxOutputSize'], int) or security['maxOutputSize'] < 1024)):
                    raise ValueError('Tool security maxOutputSize must be >= 1024 bytes')

    def get_config(self, cli_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get configuration with command line overrides"""
        file_config = self.load()
        
        if cli_options:
            # CLI options override file config
            final_config = file_config.copy()
            for key, value in cli_options.items():
                if value is not None:
                    final_config[key] = value
            return final_config
        
        return file_config

    def create_example(self) -> bool:
        """Create example configuration file"""
        example_config = {
            "defaultProvider": "claude",
            "timeout": 30000,
            "maxRetries": 3,
            "outputFormat": "text"
        }

        example_path = Path.home() / '.codesolairc.example'
        
        try:
            with open(example_path, 'w', encoding='utf-8') as f:
                json.dump(example_config, f, indent=2)
            
            Utils.log_success(f"Example configuration created at {example_path}")
            Utils.log_info("Copy this file to .codesolairc and modify as needed")
            
            return True
        except Exception as error:
            Utils.log_error(f"Could not create example config: {error}")
            return False

    def display(self) -> None:
        """Display current configuration"""
        config = self.load()
        
        print('\n📋 Current Configuration:')
        print('─' * 30)
        
        for key, value in config.items():
            if value is None:
                display_value = 'not set'
            elif isinstance(value, dict):
                display_value = json.dumps(value, indent=2)
            else:
                display_value = str(value)
            print(f"{key}: {display_value}")
        
        print(f"\nConfig file: {self.config_path}")
        print(f"Exists: {'Yes' if self.config_path.exists() else 'No'}\n")

    def exists(self) -> bool:
        """Check if config file exists"""
        return self.config_path.exists()

    def get_config_path(self) -> Path:
        """Get config file path"""
        return self.config_path

    def reset(self) -> bool:
        """Reset configuration to defaults"""
        try:
            if self.config_path.exists():
                self.config_path.unlink()
                Utils.log_success('Configuration file deleted')
            else:
                Utils.log_info('No configuration file to delete')
            return True
        except Exception as error:
            Utils.log_error(f"Could not delete config file: {error}")
            return False

    def set(self, key: str, value: Any) -> bool:
        """Set configuration value"""
        try:
            config = self.load()

            # Handle nested keys (e.g., 'agent.enabled')
            keys = key.split('.')
            current = config

            for i in range(len(keys) - 1):
                if keys[i] not in current:
                    current[keys[i]] = {}
                current = current[keys[i]]

            current[keys[-1]] = value

            # Validate and save
            self.validate_config(config)
            return self.save(config)
        except Exception as error:
            Utils.log_error(f"Could not set config value: {error}")
            return False

    def get(self, key: str) -> Any:
        """Get configuration value"""
        try:
            config = self.load()

            # Handle nested keys
            keys = key.split('.')
            current = config

            for k in keys:
                if k not in current:
                    return None
                current = current[k]

            return current
        except Exception as error:
            Utils.log_error(f"Could not get config value: {error}")
            return None

    def set_multiple(self, settings: Dict[str, Any]) -> bool:
        """Set multiple configuration values"""
        try:
            config = self.load()

            # Apply all settings
            for key, value in settings.items():
                keys = key.split('.')
                current = config

                for i in range(len(keys) - 1):
                    if keys[i] not in current:
                        current[keys[i]] = {}
                    current = current[keys[i]]

                current[keys[-1]] = value

            # Validate and save
            self.validate_config(config)
            return self.save(config)
        except Exception as error:
            Utils.log_error(f"Could not set config values: {error}")
            return False

    def set_api_key(self, provider: str, api_key: str) -> bool:
        """Set API key for provider"""
        valid_providers = ['claude', 'gemini', 'gpt']

        if provider not in valid_providers:
            Utils.log_error(f"Invalid provider: {provider}. Must be one of: {', '.join(valid_providers)}")
            return False

        if not Utils.validate_api_key(api_key, provider):
            Utils.log_error(f"Invalid API key format for {provider}")
            return False

        return self.set(f"apiKeys.{provider}", api_key)

    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for provider"""
        # First check config file
        config_key = self.get(f"apiKeys.{provider}")
        if config_key:
            return config_key

        # Fall back to environment variables
        return os.environ.get(f"{provider.upper()}_API_KEY")
