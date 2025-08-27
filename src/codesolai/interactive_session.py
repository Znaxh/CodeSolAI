"""
Interactive Session Manager for modern conversational experience with agentic capabilities
"""

import sys
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich.rule import Rule

from .utils import Utils
from .providers.provider_manager import ProviderManager
from .spinner_manager import SpinnerManager
from .config import Config

console = Console()


class InteractiveSession:
    """Interactive Session Manager for modern conversational experience"""

    def __init__(self, config: Dict[str, Any], provider: str, api_key: str, options: Dict[str, Any] = None):
        self.config = config
        self.provider = provider
        self.api_key = api_key
        self.options = options or {}
        self.provider_manager = ProviderManager(config)
        self.conversation_history: List[Dict[str, Any]] = []
        self.is_running = False
        self.spinner = SpinnerManager()
        
        # Check if agent is enabled
        agent_enabled = options.get('agent')
        if agent_enabled is None:
            agent_enabled = config.get('agent', {}).get('enabled', False)
        self.agent_enabled = agent_enabled
        
        # Agent will be implemented in future phases
        self.agent = None

    async def start(self):
        """Start the interactive session"""
        self.is_running = True
        self.display_welcome()
        await self.conversation_loop()

    def display_welcome(self):
        """Display welcome message"""
        console.print()
        console.print(Panel.fit(
            "[cyan bold]⚒️  Welcome to CodeSolAI Interactive Mode[/cyan bold]",
            border_style="cyan"
        ))
        
        console.print(f"🤖 Provider: [cyan]{self.provider.upper()}[/cyan]")
        
        if self.options.get('model'):
            console.print(f"🧠 Model: [cyan]{self.options['model']}[/cyan]")
        
        if self.agent_enabled:
            console.print("[green]🚀 CodeSolAI agent mode enabled - Can create files, run commands, and perform complex tasks[/green]")
        else:
            console.print("[yellow]💬 Simple chat mode - Agent functionality disabled[/yellow]")
        
        console.print("[yellow]⚡ Persistent session - Use Ctrl+C or /exit to quit[/yellow]")
        
        console.print("\n[dim]Type your message and press Enter to chat.[/dim]")
        console.print("[dim]Special commands:[/dim]")
        console.print("[dim]  /help     - Show help[/dim]")
        console.print("[dim]  /clear    - Clear conversation history[/dim]")
        console.print("[dim]  /history  - Show conversation history[/dim]")
        console.print("[dim]  /switch   - Switch provider[/dim]")
        console.print("[dim]  /exit     - Exit interactive mode[/dim]")
        
        console.print(Rule(style="dim"))
        console.print()

    async def conversation_loop(self):
        """Main conversation loop - Persistent session"""
        while self.is_running:
            try:
                # Get user input
                user_input = Prompt.ask("[cyan]>[/cyan]", default="")
                
                if not user_input or not user_input.strip():
                    continue

                trimmed_input = user_input.strip()

                # Handle special commands
                if trimmed_input.startswith('/'):
                    await self.handle_command(trimmed_input)
                    continue

                # Process regular prompt
                await self.process_prompt(trimmed_input)
                
            except KeyboardInterrupt:
                await self.handle_exit()
                break
            except EOFError:
                await self.handle_exit()
                break
            except Exception as error:
                Utils.log_error(f'Error in conversation: {error}')
                Utils.log_info('Session continues - type your next message or /exit to quit')
                continue

    async def handle_command(self, command: str):
        """Handle special commands"""
        cmd = command.lower()

        if cmd == '/help':
            self.show_help()
        elif cmd == '/clear':
            self.clear_history()
        elif cmd == '/history':
            self.show_history()
        elif cmd == '/switch':
            await self.switch_provider()
        elif cmd == '/exit':
            await self.handle_exit()
        else:
            Utils.log_warning(f'Unknown command: {command}')
            Utils.log_info('Type /help for available commands')

    async def process_prompt(self, prompt: str):
        """Process a regular prompt with conditional agent capabilities"""
        # Add to conversation history
        self.conversation_history.append({
            'role': 'user',
            'content': prompt,
            'timestamp': datetime.now()
        })

        # Show modern loading with dynamic messages
        thinking_messages = [
            'Thinking', 'Processing', 'Analyzing', 'Reasoning', 'Planning actions', 'Executing tasks'
        ] if self.agent_enabled else [
            'Thinking', 'Processing', 'Analyzing', 'Generating response'
        ]
        
        import random
        random_message = random.choice(thinking_messages)
        self.spinner.start(random_message)

        try:
            response = None
            result = {}

            if self.agent_enabled and self.agent:
                # Agent mode - to be implemented
                # For now, fall back to simple provider call
                Utils.log_warning("Agent mode not yet implemented, using simple mode")
                response = await self.provider_manager.call(
                    self.provider, 
                    self.api_key, 
                    prompt, 
                    {
                        'model': self.options.get('model'),
                        'maxTokens': self.options.get('maxTokens'),
                        'temperature': self.options.get('temperature')
                    }
                )
                result = {
                    'response': response,
                    'summary': {
                        'actionsExecuted': 0,
                        'filesCreated': 0,
                        'filesModified': 0,
                        'commandsRun': 0,
                        'errors': 0
                    }
                }
            else:
                # Use simple provider call without agent
                await asyncio.sleep(1)  # Simulate processing time
                if self.spinner.is_running():
                    self.spinner.update_message('Generating')

                response = await self.provider_manager.call(
                    self.provider, 
                    self.api_key, 
                    prompt, 
                    {
                        'model': self.options.get('model'),
                        'maxTokens': self.options.get('maxTokens'),
                        'temperature': self.options.get('temperature')
                    }
                )

                result = {
                    'response': response,
                    'summary': {
                        'actionsExecuted': 0,
                        'filesCreated': 0,
                        'filesModified': 0,
                        'commandsRun': 0,
                        'errors': 0
                    }
                }

            # Stop spinner with success
            self.spinner.succeed(f'Response generated in {self.spinner.get_elapsed_time()}s')

            # Add response to history
            self.conversation_history.append({
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now()
            })

            # Display response and execution summary
            self.display_response(response)
            
            # Show execution summary only if agent mode is enabled and actions were performed
            if (self.agent_enabled and result.get('summary') and 
                (result['summary'].get('actionsExecuted', 0) > 0 or 
                 result['summary'].get('filesCreated', 0) > 0 or 
                 result['summary'].get('commandsRun', 0) > 0)):
                self.display_execution_summary(result['summary'])

        except Exception as error:
            # Stop spinner with error
            self.spinner.fail(f'Request failed after {self.spinner.get_elapsed_time()}s')
            
            Utils.log_error(f'Failed to get response: {error}')
            
            # Provide helpful suggestions
            error_str = str(error)
            if 'Invalid API key' in error_str:
                Utils.log_info('Your API key may be invalid or expired')
            elif 'Rate limit' in error_str:
                Utils.log_info('You may have hit the API rate limit. Try again in a moment.')

    def display_response(self, response: str):
        """Display AI response with nice formatting"""
        console.print()
        console.print(Rule(style="dim"))
        console.print(response)
        console.print(Rule(style="dim"))
        console.print()

    def display_execution_summary(self, summary: Dict[str, int]):
        """Display execution summary for agentic actions"""
        console.print("[cyan bold]🔧 Execution Summary:[/cyan bold]")
        
        if summary.get('actionsExecuted', 0) > 0:
            console.print(f"   Actions executed: [green]{summary['actionsExecuted']}[/green]")
        
        if summary.get('filesCreated', 0) > 0:
            console.print(f"   Files created: [green]{summary['filesCreated']}[/green]")
        
        if summary.get('filesModified', 0) > 0:
            console.print(f"   Files modified: [green]{summary['filesModified']}[/green]")
        
        if summary.get('commandsRun', 0) > 0:
            console.print(f"   Commands executed: [green]{summary['commandsRun']}[/green]")
        
        if summary.get('errors', 0) > 0:
            console.print(f"   Errors: [red]{summary['errors']}[/red]")
        
        console.print()

    def show_help(self):
        """Show help information"""
        console.print()
        console.print("[cyan bold]📖 Interactive Mode Help[/cyan bold]")
        console.print(Rule(style="dim"))
        console.print("[white]Available commands:[/white]")
        console.print("[dim]  /help     - Show this help message[/dim]")
        console.print("[dim]  /clear    - Clear conversation history[/dim]")
        console.print("[dim]  /history  - Show conversation history[/dim]")
        console.print("[dim]  /switch   - Switch to a different provider[/dim]")
        console.print("[dim]  /exit     - Exit interactive mode[/dim]")
        console.print()
        console.print("[white]Current mode:[/white]")
        if self.agent_enabled:
            console.print("[dim]  • CodeSolAI agent mode: Can create files, run commands, and perform complex tasks[/dim]")
        else:
            console.print("[dim]  • Simple chat mode: Agent functionality disabled[/dim]")
        console.print()
        console.print("[white]Tips:[/white]")
        if self.agent_enabled:
            console.print("[dim]  • Ask me to create files, run commands, or analyze code[/dim]")
            console.print("[dim]  • I can perform complex multi-step tasks automatically[/dim]")
        else:
            console.print("[dim]  • I can answer questions and provide explanations[/dim]")
            console.print("[dim]  • File creation and command execution are disabled[/dim]")
        console.print("[dim]  • Your conversation history is maintained during the session[/dim]")
        console.print("[dim]  • Use Ctrl+C or /exit to quit[/dim]")
        console.print()

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        console.print()
        Utils.log_success('Conversation history cleared')
        console.print()

    def show_history(self):
        """Show conversation history"""
        console.print()
        console.print("[cyan bold]📚 Conversation History[/cyan bold]")
        console.print(Rule(style="dim"))
        
        if not self.conversation_history:
            console.print("[dim]No conversation history yet[/dim]")
            console.print()
            return

        for entry in self.conversation_history:
            timestamp = entry['timestamp'].strftime('%H:%M:%S')
            role = "[blue]You[/blue]" if entry['role'] == 'user' else "[green]AI[/green]"
            content = entry['content']
            if len(content) > 100:
                content = content[:100] + '...'
            
            console.print(f"[dim]{timestamp}[/dim] {role}: {content}")
        console.print()

    async def switch_provider(self):
        """Switch provider"""
        console.print()
        console.print("[cyan]Available providers:[/cyan]")
        console.print("1. Claude (Anthropic)")
        console.print("2. GPT (OpenAI)")
        console.print("3. Gemini (Google)")
        console.print()

        choice = Prompt.ask("Choose provider", choices=['1', '2', '3'])
        providers = {
            '1': 'claude',
            '2': 'gpt',
            '3': 'gemini'
        }

        new_provider = providers[choice]
        
        # Check if API key is available for new provider
        config = Config()
        new_api_key = config.get_api_key(new_provider)
        
        if new_api_key:
            self.provider = new_provider
            self.api_key = new_api_key
            Utils.log_success(f'Switched to {new_provider.upper()}')
            
            # Clear history when switching providers
            self.conversation_history = []
            Utils.log_info('Conversation history cleared for new provider')
        else:
            Utils.log_error(f'No API key found for {new_provider}')
            Utils.log_info(f'Set up {new_provider} with: codesolai --setup')
        console.print()

    async def handle_exit(self):
        """Handle exit"""
        console.print()
        Utils.log_info('Thanks for using CodeSolAI! 👋')
        self.is_running = False
        
        # Cleanup agent (when implemented)
        if self.agent:
            try:
                await self.agent.shutdown()
            except Exception:
                pass  # Ignore shutdown errors

    async def stop(self):
        """Stop the session"""
        self.is_running = False
        
        # Cleanup agent (when implemented)
        if self.agent:
            try:
                await self.agent.shutdown()
            except Exception:
                pass  # Ignore shutdown errors
