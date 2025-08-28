"""
Main CLI interface for CodeSolAI
"""

import sys
import asyncio
import signal
from typing import Optional, List, Dict, Any
import click
from rich.console import Console

from .config import Config
from .utils import Utils
from .providers.provider_manager import ProviderManager
from .spinner_manager import SpinnerManager
from .setup import Setup
from .interactive_session import InteractiveSession
from .core.enhanced_agent import EnhancedAgent
from . import __version__

console = Console()


def handle_sigint(signum, frame):
    """Handle Ctrl+C gracefully"""
    console.print("\n")
    Utils.log_info("Operation cancelled by user")
    sys.exit(0)


# Set up signal handler
signal.signal(signal.SIGINT, handle_sigint)


@click.command()
@click.option('--provider', '-p', help='LLM provider (claude, gemini, gpt)')
@click.option('--api-key', '-k', help='API key for the provider')
@click.option('--model', '-m', help='Specific model to use (optional)')
@click.option('--timeout', type=int, help='Request timeout in milliseconds')
@click.option('--max-tokens', type=int, help='Maximum tokens in response')
@click.option('--temperature', type=float, help='Temperature for response generation')
@click.option('--agent/--no-agent', default=None, help='Enable/disable agent mode')
@click.option('--autonomous', is_flag=True, help='Enable autonomous multi-step execution')
@click.option('--effort', type=click.Choice(['low', 'medium', 'high', 'maximum']),
              default='medium', help='Reasoning effort level')
@click.option('--max-iterations', type=int, help='Maximum iterations for autonomous mode')
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.option('--trace', is_flag=True, help='Enable execution tracing')
@click.option('--config', 'show_config', is_flag=True, help='Show current configuration')
@click.option('--config-example', is_flag=True, help='Create example configuration file')
@click.option('--config-reset', is_flag=True, help='Reset configuration to defaults')
@click.option('--test-key', is_flag=True, help='Test API key validity')
@click.option('--version', is_flag=True, help='Show version information')
@click.option('--setup', is_flag=True, help='Run interactive setup')
@click.option('--interactive', '-i', is_flag=True, help='Start interactive chat mode')
@click.argument('prompt', nargs=-1)
def main(**kwargs):
    """CodeSolAI - A fully autonomous agentic CLI tool for interacting with large language models"""
    # Handle special commands first
    if kwargs.get('setup'):
        async def run_setup():
            setup_wizard = Setup()
            await setup_wizard.run()
        asyncio.run(run_setup())
        return

    asyncio.run(async_main(**kwargs))


async def async_main(**kwargs):
    """Async main function"""
    # Handle version command
    if kwargs.get('version'):
        console.print(__version__)
        return

    # Handle configuration commands
    config = Config()

    if kwargs.get('show_config'):
        config.display()
        return

    if kwargs.get('config_example'):
        config.create_example()
        return

    if kwargs.get('config_reset'):
        config.reset()
        return

    # Get prompt from arguments
    prompt_args = list(kwargs.get('prompt', []))

    # Check if we should enter interactive mode
    should_enter_interactive_mode = (
        kwargs.get('interactive') or
        (len(prompt_args) == 0 and not Utils.is_stdin_input())
    )

    if should_enter_interactive_mode:
        # Load config for interactive mode
        config = Config()
        app_config = config.get_config(kwargs)

        # Need provider and API key for interactive mode
        provider = kwargs.get('provider') or app_config.get('defaultProvider')
        if not provider:
            Utils.log_error('No provider configured for interactive mode.')
            Utils.log_info('Run "codesolai --setup" to configure your first provider.')
            sys.exit(1)

        api_key = kwargs.get('api_key') or config.get_api_key(provider)
        if not api_key:
            Utils.log_error(f'No API key found for {provider}')
            Utils.log_info('Run "codesolai --setup" to configure your API key.')
            sys.exit(1)

        # Start interactive session
        session = InteractiveSession(app_config, provider, api_key, kwargs)
        await session.start()
        return

    # Get prompt from arguments or stdin
    prompt = ''

    if prompt_args:
        # Prompt provided as command line arguments
        prompt = ' '.join(prompt_args)
    elif Utils.is_stdin_input():
        # Read from stdin (piped input)
        try:
            prompt = await Utils.read_stdin()
        except Exception as error:
            Utils.log_error(f'Failed to read from stdin: {error}')
            sys.exit(1)
    else:
        # No prompt provided
        Utils.log_error('No prompt provided')
        Utils.log_info('Provide a prompt as arguments or pipe input via stdin')
        Utils.log_info('Examples:')
        Utils.log_info('  codesolai "Explain quantum computing"')
        Utils.log_info('  echo "Write a Python function" | codesolai')
        Utils.log_info('  codesolai --help  # for more options')
        sys.exit(1)

    if not prompt or not prompt.strip():
        Utils.log_error('Prompt cannot be empty')
        sys.exit(1)

    # Load configuration
    app_config = config.get_config({
        'defaultProvider': kwargs.get('provider'),
        'timeout': kwargs.get('timeout')
    })

    # Determine provider
    provider = kwargs.get('provider') or app_config.get('defaultProvider')
    if not provider:
        Utils.log_error('No provider configured.')
        Utils.log_info('Run "codesolai setup" to configure your first provider, or use --provider flag.')
        Utils.log_info('Example: codesolai --provider claude --api-key sk-ant-xxx "your prompt"')
        sys.exit(1)

    # Validate provider
    valid_providers = ['claude', 'gemini', 'gpt']
    if provider not in valid_providers:
        Utils.log_error(f'Invalid provider: {provider}')
        Utils.log_info(f'Supported providers: {", ".join(valid_providers)}')
        sys.exit(1)

    # Get API key
    api_key = kwargs.get('api_key') or config.get_api_key(provider)
    if not api_key:
        Utils.log_error(f'No API key found for {provider}')
        Utils.log_info('Set up your API key using one of these methods:')
        Utils.log_info('1. Run "codesolai setup" for interactive configuration')
        Utils.log_info(f'2. Use: codesolai config-set --set-api-key <key> --set-provider {provider}')
        Utils.log_info(f'3. Set environment variable: {provider.upper()}_API_KEY=<key>')
        Utils.log_info(f'4. Use --api-key flag: codesolai --provider {provider} --api-key <key> "prompt"')
        sys.exit(1)

    # Test API key if requested
    if kwargs.get('test_key'):
        spinner = SpinnerManager()
        spinner.start('Testing API key')

        provider_manager = ProviderManager(app_config)
        is_valid = await provider_manager.test_api_key(provider, api_key)

        if is_valid:
            spinner.succeed(f'{provider.upper()} API key is valid and working')
        else:
            spinner.fail(f'{provider.upper()} API key test failed')
            sys.exit(1)
        return

    # Validate API key format
    if not Utils.validate_api_key(api_key, provider):
        Utils.log_error(f'Invalid API key format for {provider}')
        Utils.log_info('Please check your API key and try again')
        sys.exit(1)

    # Show security warning for command-line API keys
    if kwargs.get('api_key'):
        Utils.log_warning('API key provided via command line is visible in process lists')
        Utils.log_info('Consider using environment variables or config file for better security')

    # Determine agent mode and effort level
    agent_enabled = kwargs.get('agent')
    if agent_enabled is None:
        agent_enabled = app_config.get('agent', {}).get('enabled', False)
    
    autonomous_mode = kwargs.get('autonomous') or app_config.get('agent', {}).get('autonomous', False)
    effort_level = kwargs.get('effort') or app_config.get('agent', {}).get('effort', 'medium')

    max_iterations = kwargs.get('max_iterations') or app_config.get('agent', {}).get('maxIterations', 10)

    # Use agent mode if enabled
    if agent_enabled:
        await handle_agent_prompt(provider, api_key, prompt, kwargs, app_config, effort_level, max_iterations, autonomous_mode)
    else:
        await handle_simple_prompt(provider, api_key, prompt, kwargs, app_config)


async def handle_simple_prompt(provider: str, api_key: str, prompt: str, 
                              options: Dict[str, Any], config: Dict[str, Any]):
    """Handle simple prompt without agent mode"""
    spinner = SpinnerManager()
    
    # Start with random thinking message
    thinking_messages = ['Thinking', 'Processing', 'Analyzing', 'Reasoning', 'Computing']
    import random
    random_message = random.choice(thinking_messages)
    spinner.start(random_message)

    try:
        # Update message during processing
        await asyncio.sleep(1)
        if spinner.is_running():
            spinner.update_message('Processing')

        await asyncio.sleep(1)
        if spinner.is_running():
            spinner.update_message('Generating')

        provider_manager = ProviderManager(config)
        response = await provider_manager.call(provider, api_key, prompt, {
            'model': options.get('model'),
            'maxTokens': options.get('max_tokens'),
            'temperature': options.get('temperature')
        })
        
        # Success with timing
        spinner.succeed(f'Response generated in {spinner.get_elapsed_time()}s')
        
        # Clean output without technical artifacts
        console.print(f'\n{response}\n')
        
    except Exception as error:
        # Error with timing
        spinner.fail(f'Request failed after {spinner.get_elapsed_time()}s')
        Utils.log_error(f'Request failed: {error}')
        
        # Provide helpful suggestions based on error type
        error_str = str(error)
        if 'Invalid API key' in error_str:
            Utils.log_info('Double-check your API key and ensure it has the correct permissions')
            Utils.log_info(f'Set via: codesolai config-set --set-api-key <key> --set-provider {provider}')
        elif 'Rate limit' in error_str:
            Utils.log_info('Wait a moment before trying again, or check your API usage limits')
        elif 'Network error' in error_str:
            Utils.log_info('Check your internet connection and try again')
        
        sys.exit(1)


async def handle_agent_prompt(provider: str, api_key: str, prompt: str,
                             options: Dict[str, Any], config: Dict[str, Any],
                             effort_level: str, max_iterations: int, autonomous_mode: bool):
    """Handle prompt using the enhanced agent system"""
    spinner = SpinnerManager()

    try:
        # Initialize the enhanced agent
        agent_options = {
            'provider': provider,
            'api_key': api_key,
            'model': options.get('model'),
            'temperature': options.get('temperature', 0.7),
            'max_tokens': options.get('max_tokens', 4000),
            'effort': effort_level,
            'max_iterations': max_iterations,
            'tools_enabled': True,
            'auto_approve': autonomous_mode,
            'confirmation_required': not autonomous_mode,
            'autonomous': autonomous_mode  # Explicitly pass autonomous flag
        }

        spinner.start('Initializing agent')
        agent = EnhancedAgent(agent_options)

        # Process the prompt through the agent
        spinner.update_message('Agent processing')
        result = await agent.process_prompt(prompt, agent_options)

        if result.get('success', False):
            # Success with timing and agent info
            elapsed = spinner.get_elapsed_time()
            actions_count = result.get('actions_executed', 0)

            if actions_count > 0:
                spinner.succeed(f'Agent completed {actions_count} actions in {elapsed}s')
            else:
                spinner.succeed(f'Agent response generated in {elapsed}s')

            # Display the response
            response = result.get('response', '')
            console.print(f'\n{response}\n')

            # Show execution results if any
            execution_results = result.get('execution_results', [])
            if execution_results:
                console.print("🔧 [bold blue]Agent Actions Executed:[/bold blue]")
                for i, exec_result in enumerate(execution_results, 1):
                    if exec_result.get('success'):
                        console.print(f"  {i}. ✅ {exec_result.get('tool', 'Unknown')}")
                    else:
                        console.print(f"  {i}. ❌ {exec_result.get('tool', 'Unknown')}: {exec_result.get('error', 'Failed')}")
                console.print()
        else:
            # Agent processing failed
            spinner.fail(f'Agent processing failed after {spinner.get_elapsed_time()}s')
            error_msg = result.get('error', 'Unknown agent error')
            Utils.log_error(f'Agent error: {error_msg}')

            # Fallback to simple response if available
            response = result.get('response', '')
            if response:
                console.print(f'\n{response}\n')

            sys.exit(1)

    except Exception as error:
        # Agent system error
        spinner.fail(f'Agent system error after {spinner.get_elapsed_time()}s')
        Utils.log_error(f'Agent system failed: {error}')
        Utils.log_info('Falling back to simple mode...')

        # Fallback to simple prompt handling
        await handle_simple_prompt(provider, api_key, prompt, options, config)


def cli():
    """Entry point for the CLI"""
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n")
        Utils.log_info("Operation cancelled by user")
        sys.exit(0)
    except Exception as error:
        Utils.log_error(f'Unexpected error: {error}')
        sys.exit(1)


if __name__ == '__main__':
    cli()
