"""
Interactive setup for first-time users
"""

import asyncio
from typing import Optional, List
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text

from .utils import Utils
from .config import Config
from .providers.provider_manager import ProviderManager

console = Console()


class Setup:
    """Interactive setup for first-time users"""

    def __init__(self):
        self.config = Config()

    async def run(self):
        """Run interactive setup"""
        console.print()
        Utils.log_info('🚀 Welcome to CodeSolAI CLI Setup!')
        console.print()
        Utils.log_info('This setup will help you configure CodeSolAI for first use.')
        Utils.log_info('You can always change these settings later using: codesolai config-set')
        console.print()

        # Check if config already exists
        if self.config.exists():
            Utils.log_warning(f'Configuration file already exists at: {self.config.get_config_path()}')
            console.print()
            
            should_continue = Confirm.ask('Do you want to update your existing configuration?')
            if not should_continue:
                Utils.log_info('Setup cancelled. Your existing configuration is unchanged.')
                return
            console.print()

        try:
            # Step 1: Choose default provider
            provider = await self.choose_provider()
            
            # Step 2: Set API key for chosen provider
            api_key = await self.get_api_key(provider)
            
            # Step 3: Choose default model (optional)
            model = await self.choose_model(provider)
            
            # Step 4: Agent settings
            agent_enabled = await self.configure_agent()

            # Step 5: Save configuration
            settings = {
                'defaultProvider': provider
            }

            if model:
                settings['defaultModel'] = model

            if agent_enabled is not None:
                settings['agent.enabled'] = agent_enabled

            # Save settings
            if self.config.set_multiple(settings):
                # Save API key
                if self.config.set_api_key(provider, api_key):
                    console.print()
                    Utils.log_success('🎉 Setup completed successfully!')
                    console.print()
                    self.show_quick_start(provider)
                else:
                    Utils.log_error('Failed to save API key')
            else:
                Utils.log_error('Failed to save configuration')

        except KeyboardInterrupt:
            console.print()
            Utils.log_info('Setup cancelled by user')
        except Exception as error:
            Utils.log_error(f'Setup failed: {error}')

    async def choose_provider(self) -> str:
        """Choose default provider"""
        Utils.log_info('📡 Choose your default AI provider:')
        console.print()
        
        providers_info = [
            ("1", "claude", "Claude (Anthropic) - Great for reasoning and analysis"),
            ("2", "gpt", "GPT (OpenAI) - Popular choice with good general capabilities"),
            ("3", "gemini", "Gemini (Google) - Fast and efficient for most tasks")
        ]
        
        for choice, _, description in providers_info:
            console.print(f"{choice}. {description}")
        console.print()

        choice = Prompt.ask(
            'Enter your choice',
            choices=['1', '2', '3'],
            default='1'
        )
        
        providers = {
            '1': 'claude',
            '2': 'gpt', 
            '3': 'gemini'
        }

        return providers[choice]

    async def get_api_key(self, provider: str) -> str:
        """Get API key for provider"""
        console.print()
        Utils.log_info(f'🔑 Setting up {provider.upper()} API key:')
        console.print()
        
        # Show provider-specific instructions
        self.show_api_key_instructions(provider)
        
        api_key = None
        is_valid = False
        
        while not is_valid:
            api_key = Prompt.ask(
                f'Enter your {provider.upper()} API key',
                password=True
            )
            
            if not api_key or not api_key.strip():
                Utils.log_error('API key cannot be empty')
                continue

            # Validate API key format
            if not Utils.validate_api_key(api_key, provider):
                Utils.log_error(f'Invalid API key format for {provider}')
                self.show_api_key_format(provider)
                continue

            # Test API key
            Utils.log_info('Testing API key...')
            provider_manager = ProviderManager()
            
            try:
                is_valid = await provider_manager.test_api_key(provider, api_key)
                if not is_valid:
                    Utils.log_error('API key test failed. Please check your key and try again.')
            except Exception as error:
                Utils.log_error(f'Failed to test API key: {error}')
                is_valid = False

        Utils.log_success('API key validated successfully!')
        return api_key

    async def choose_model(self, provider: str) -> Optional[str]:
        """Choose default model"""
        console.print()
        use_default = Confirm.ask(
            f'Use default model for {provider}? (recommended for beginners)',
            default=True
        )
        
        if use_default:
            return None  # Use provider default

        Utils.log_info(f'Available models for {provider}:')
        provider_manager = ProviderManager()
        models = provider_manager.get_available_models(provider)
        
        console.print()
        choices = []
        for i, model in enumerate(models, 1):
            console.print(f"{i}. {model}")
            choices.append(str(i))
        
        console.print(f"{len(models) + 1}. Use default")
        choices.append(str(len(models) + 1))
        console.print()

        choice = Prompt.ask('Choose a model', choices=choices, default=str(len(models) + 1))
        choice_index = int(choice) - 1
        
        if choice_index == len(models):
            return None  # Use default
        
        return models[choice_index]

    async def configure_agent(self) -> bool:
        """Configure agent settings"""
        console.print()
        Utils.log_info('🤖 Agent Mode Configuration:')
        console.print()
        Utils.log_info('Agent mode allows CodeSolAI to execute actions based on AI responses')
        Utils.log_info('(like creating files, running commands, etc.)')
        console.print()
        
        return Confirm.ask('Enable agent mode? (recommended)', default=True)

    def show_api_key_instructions(self, provider: str):
        """Show API key instructions for provider"""
        instructions = {
            'claude': [
                'To get your Claude API key:',
                '1. Go to https://console.anthropic.com',
                '2. Sign up or log in to your account',
                '3. Navigate to API Keys section',
                '4. Create a new API key',
                '5. Copy the key (starts with "sk-ant-")'
            ],
            'gpt': [
                'To get your OpenAI API key:',
                '1. Go to https://platform.openai.com',
                '2. Sign up or log in to your account',
                '3. Navigate to API Keys section',
                '4. Create a new API key',
                '5. Copy the key (starts with "sk-")'
            ],
            'gemini': [
                'To get your Gemini API key:',
                '1. Go to https://makersuite.google.com',
                '2. Sign in with your Google account',
                '3. Create a new API key',
                '4. Copy the generated key'
            ]
        }

        for line in instructions[provider]:
            Utils.log_info(line)
        console.print()

    def show_api_key_format(self, provider: str):
        """Show API key format for provider"""
        formats = {
            'claude': 'Claude API keys start with "sk-ant-" followed by alphanumeric characters',
            'gpt': 'OpenAI API keys start with "sk-" followed by alphanumeric characters',
            'gemini': 'Gemini API keys are alphanumeric strings (usually 39 characters)'
        }

        Utils.log_info(f'Expected format: {formats[provider]}')

    def show_quick_start(self, provider: str):
        """Show quick start guide"""
        Utils.log_info('🎯 Quick Start Guide:')
        console.print()
        Utils.log_info('Now you can use CodeSolAI with simple commands:')
        console.print()
        console.print('  codesolai "Explain quantum computing"')
        console.print('  echo "Write a Python function" | codesolai')
        console.print()
        Utils.log_info('Other useful commands:')
        console.print()
        console.print('  codesolai --help              Show all options')
        console.print('  codesolai --config             Show current configuration')
        console.print('  codesolai config-set --help    Update configuration')
        console.print()
        Utils.log_info('For more information, visit: https://github.com/Znaxh/codesolai')
        console.print()
