"""
Utility functions for formatting, logging, and user feedback
"""

import sys
import re
import asyncio
from typing import Optional, Any
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.spinner import Spinner
from rich.live import Live
import colorama
from colorama import Fore, Style

# Initialize colorama for cross-platform colored output
colorama.init()

console = Console()


class Utils:
    """Utility functions for formatting, logging, and user feedback"""

    @staticmethod
    def log_success(message: str) -> None:
        """Log success message with green checkmark"""
        console.print(f"[green]✓[/green] {message}")

    @staticmethod
    def log_error(message: str) -> None:
        """Log error message with red X"""
        error_console = Console(stderr=True)
        error_console.print(f"[red]✗[/red] {message}")

    @staticmethod
    def log_warning(message: str) -> None:
        """Log warning message with yellow triangle"""
        console.print(f"[yellow]⚠[/yellow] {message}")

    @staticmethod
    def log_info(message: str) -> None:
        """Log info message with blue info icon"""
        console.print(f"[blue]ℹ[/blue] {message}")

    @staticmethod
    def format_response(response: str, provider: str) -> str:
        """Format the LLM response for display"""
        panel = Panel(
            response,
            title=f"📤 Response from {provider.upper()}",
            title_align="left",
            border_style="cyan",
            padding=(1, 2)
        )
        
        # Return the panel as a string for consistent output
        with console.capture() as capture:
            console.print(panel)
        return capture.get()

    @staticmethod
    def format_error(error: Exception, provider: Optional[str] = None) -> str:
        """Format error messages with context"""
        message = "An error occurred"
        
        # Handle HTTP errors (assuming httpx exceptions)
        if hasattr(error, 'response') and error.response:
            status = error.response.status_code
            
            if status == 401:
                message = "Invalid API key. Please check your API key and try again."
            elif status == 429:
                message = "Rate limit exceeded. Please wait a moment and try again."
            elif status == 403:
                message = "Access forbidden. Please check your API key permissions."
            elif status >= 500:
                message = f"{provider or 'API'} server error ({status}). Please try again later."
            else:
                message = f"API error: {status} {getattr(error.response, 'reason_phrase', '')}"
        
        # Handle network errors
        elif hasattr(error, 'request') and not hasattr(error, 'response'):
            message = "Network error. Please check your internet connection."
        elif str(error):
            message = str(error)

        return message

    @staticmethod
    def validate_api_key(api_key: str, provider: str) -> bool:
        """Validate API key format for different providers"""
        if not api_key or not isinstance(api_key, str) or not api_key.strip():
            return False

        trimmed_key = api_key.strip()

        if provider == 'claude':
            # Anthropic API keys typically start with 'sk-ant-'
            return trimmed_key.startswith('sk-ant-') and len(trimmed_key) > 20
        elif provider == 'gpt':
            # OpenAI API keys typically start with 'sk-'
            return trimmed_key.startswith('sk-') and len(trimmed_key) > 20
        elif provider == 'gemini':
            # Google API keys are typically 39 characters long
            return len(trimmed_key) >= 30 and ' ' not in trimmed_key
        else:
            return len(trimmed_key) > 10

    @staticmethod
    def sanitize_for_log(text: str, max_length: int = 100) -> str:
        """Sanitize input text for logging (remove sensitive information)"""
        if not text:
            return ''
        
        # Remove API keys from logs
        sanitized = re.sub(r'sk-[a-zA-Z0-9\-_]+', 'sk-***', text)
        
        return sanitized[:max_length] + '...' if len(sanitized) > max_length else sanitized

    @staticmethod
    def is_stdin_input() -> bool:
        """Check if input is coming from stdin (piped input)"""
        return not sys.stdin.isatty()

    @staticmethod
    async def read_stdin() -> str:
        """Read input from stdin asynchronously"""
        if Utils.is_stdin_input():
            loop = asyncio.get_event_loop()
            # Read from stdin in a thread to avoid blocking
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = loop.run_in_executor(executor, sys.stdin.read)
                try:
                    content = await asyncio.wait_for(future, timeout=5.0)
                    return content.strip()
                except asyncio.TimeoutError:
                    raise Exception("No input received from stdin")
        else:
            raise Exception("No piped input available")

    @staticmethod
    def display_help() -> None:
        """Display help information with colored formatting"""
        help_text = """
[cyan bold]CodeSolAI CLI[/cyan bold] - Interact with Large Language Models

[yellow]USAGE:[/yellow]
  codesolai [options] <prompt>
  echo "prompt" | codesolai [options]

[yellow]OPTIONS:[/yellow]
  --provider, -p    LLM provider (claude, gemini, gpt) [dim][required][/dim]
  --api-key, -k     API key for the provider [dim][required][/dim]
  --help, -h        Show this help message
  --version, -v     Show version information
  --agent           Enable agent mode for complex tasks
  --autonomous      Enable autonomous multi-step execution

[yellow]EXAMPLES:[/yellow]
  [dim]# Direct prompt[/dim]
  codesolai --provider claude --api-key sk-ant-xxx "Explain quantum computing"
  
  [dim]# Piped input[/dim]
  echo "Write a Python function" | codesolai --provider gpt --api-key sk-xxx
  
  [dim]# Using short flags[/dim]
  codesolai -p gemini -k your-api-key "What is machine learning?"
  
  [dim]# Agent mode[/dim]
  codesolai --agent --provider claude "Create a web scraper"

[yellow]CONFIGURATION:[/yellow]
  Create a [cyan].codesolairc[/cyan] file in your home directory to set default values:
  [dim]{[/dim]
  [dim]  "defaultProvider": "claude",[/dim]
  [dim]  "timeout": 30000[/dim]
  [dim]}[/dim]

[yellow]SECURITY NOTE:[/yellow]
  [red]⚠ API keys passed via command line are visible in process lists.[/red]
  [white]Consider using environment variables or the config file.[/white]
"""
        console.print(help_text)

    @staticmethod
    def create_spinner(text: str, color: str = "green") -> Spinner:
        """Create a spinner with custom text and color"""
        return Spinner("dots", text=text, style=color)
