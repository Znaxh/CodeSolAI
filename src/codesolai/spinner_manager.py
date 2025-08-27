"""
Advanced Spinner Manager with animated loading and timing
Provides animated spinners with elapsed time tracking and dynamic messages
"""

import time
import asyncio
from typing import Optional
from rich.console import Console
from rich.spinner import Spinner
from rich.live import Live
from rich.text import Text

console = Console()


class SpinnerManager:
    """Advanced Spinner Manager with animated loading and timing"""

    def __init__(self):
        self.live: Optional[Live] = None
        self.start_time: Optional[float] = None
        self.message: Optional[str] = None
        self.is_active: bool = False
        self._update_task: Optional[asyncio.Task] = None

    def start(self, message: Optional[str] = None) -> 'SpinnerManager':
        """Start the spinner with a message"""
        # Stop any existing spinner first
        self.stop()

        words = [
            'Thinking',
            'Processing', 
            'Analyzing',
            'Working',
            'Researching',
            'Synthesizing',
            'Reasoning',
            'Contemplating',
            'Computing',
            'Generating'
        ]

        # Use a random word from the list if no message provided
        import random
        word = message or random.choice(words)
        
        # Store the base message for timer updates
        self.message = word
        self.start_time = time.time()
        self.is_active = True

        # Create the spinner with modern styling
        spinner = Spinner("dots", text=self._format_message(0), style="green")
        self.live = Live(spinner, console=console, refresh_per_second=10)
        self.live.start()

        # Start async update task if we're in an async context
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                self._update_task = loop.create_task(self._update_loop())
        except RuntimeError:
            # Not in async context, that's fine
            pass

        return self

    def _format_message(self, seconds: int) -> str:
        """Format the message with elapsed time"""
        time_info = f"{seconds}s"
        hint = "Ctrl+C to interrupt"
        
        return f"{self.message} {time_info} · {hint}"

    async def _update_loop(self):
        """Async loop to update elapsed time"""
        while self.is_active and self.start_time:
            await asyncio.sleep(0.5)  # Update every 500ms
            if self.is_active and self.live and self.start_time:
                elapsed = int(time.time() - self.start_time)
                spinner = Spinner("dots", text=self._format_message(elapsed), style="green")
                self.live.update(spinner)

    def stop(self, message: Optional[str] = None) -> 'SpinnerManager':
        """Stop the spinner with optional completion message"""
        if self._update_task:
            self._update_task.cancel()
            self._update_task = None

        if self.live:
            self.live.stop()
            self.live = None

        self.is_active = False

        # Print completion message if provided
        if message:
            console.print(message)

        # Reset state
        self.start_time = None
        self.message = None

        return self

    def write_ln(self, message: str) -> 'SpinnerManager':
        """Write a line while preserving spinner state"""
        was_running = self.is_active
        prev_message = self.message
        
        # Stop spinner, print message, restart if it was running
        self.stop()
        console.print(message)
        
        if was_running and prev_message:
            # Small delay to ensure clean output
            time.sleep(0.01)
            self.start(prev_message)

        return self

    def update_message(self, new_message: str) -> 'SpinnerManager':
        """Update the spinner message without restarting"""
        if self.is_active:
            self.message = new_message
            if self.live and self.start_time:
                elapsed = int(time.time() - self.start_time)
                spinner = Spinner("dots", text=self._format_message(elapsed), style="green")
                self.live.update(spinner)
        return self

    def is_running(self) -> bool:
        """Check if spinner is currently active"""
        return self.is_active

    def get_elapsed_time(self) -> int:
        """Get elapsed time in seconds"""
        if self.start_time:
            return int(time.time() - self.start_time)
        return 0

    def succeed(self, message: Optional[str] = None) -> 'SpinnerManager':
        """Succeed and stop with success message"""
        self.stop()
        if message:
            console.print(f"[green]✓[/green] {message}")
        return self

    def fail(self, message: Optional[str] = None) -> 'SpinnerManager':
        """Fail and stop with error message"""
        self.stop()
        if message:
            console.print(f"[red]✗[/red] {message}")
        return self

    def warn(self, message: Optional[str] = None) -> 'SpinnerManager':
        """Warn and stop with warning message"""
        self.stop()
        if message:
            console.print(f"[yellow]⚠[/yellow] {message}")
        return self

    def info(self, message: Optional[str] = None) -> 'SpinnerManager':
        """Info and stop with info message"""
        self.stop()
        if message:
            console.print(f"[blue]ℹ[/blue] {message}")
        return self

    def cleanup(self) -> None:
        """Internal cleanup method"""
        if self._update_task:
            self._update_task.cancel()
            self._update_task = None
        
        if self.live:
            self.live.stop()
            self.live = None
            
        self.is_active = False
        self.start_time = None
        self.message = None

    def __enter__(self) -> 'SpinnerManager':
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit"""
        self.cleanup()
