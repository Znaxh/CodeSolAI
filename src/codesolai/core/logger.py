"""
Logger for agent system with metrics and tracing support
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from rich.console import Console
from rich.logging import RichHandler

console = Console()


class Logger:
    """Enhanced logger for agent system"""

    def __init__(self, agent_id: str, level: str = "info", enable_metrics: bool = True, enable_tracing: bool = False):
        self.agent_id = agent_id
        self.enable_metrics = enable_metrics
        self.enable_tracing = enable_tracing
        
        # Setup Python logger
        self.logger = logging.getLogger(f"codesolai.agent.{agent_id}")
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Add rich handler if not already present
        if not self.logger.handlers:
            handler = RichHandler(console=console, show_time=True, show_path=False)
            handler.setFormatter(logging.Formatter(
                "%(message)s",
                datefmt="[%X]"
            ))
            self.logger.addHandler(handler)
        
        # Metrics storage
        self.metrics = {
            'log_counts': {'debug': 0, 'info': 0, 'warning': 0, 'error': 0},
            'start_time': datetime.now(),
            'events': []
        }

    def _log_with_context(self, level: str, message: str, context: Optional[Dict[str, Any]] = None):
        """Log message with context and metrics"""
        # Update metrics
        if self.enable_metrics:
            self.metrics['log_counts'][level] += 1
        
        # Format message with context
        if context:
            formatted_message = f"[{self.agent_id}] {message} | {json.dumps(context, default=str)}"
        else:
            formatted_message = f"[{self.agent_id}] {message}"
        
        # Log to Python logger
        getattr(self.logger, level)(formatted_message)
        
        # Store for tracing if enabled
        if self.enable_tracing:
            self.metrics['events'].append({
                'timestamp': datetime.now(),
                'level': level,
                'message': message,
                'context': context
            })

    def debug(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log debug message"""
        self._log_with_context('debug', message, context)

    def info(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log info message"""
        self._log_with_context('info', message, context)

    def warn(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log warning message"""
        self._log_with_context('warning', message, context)

    def error(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log error message"""
        self._log_with_context('error', message, context)

    def get_metrics(self) -> Dict[str, Any]:
        """Get logger metrics"""
        if not self.enable_metrics:
            return {}
        
        uptime = (datetime.now() - self.metrics['start_time']).total_seconds()
        return {
            'agent_id': self.agent_id,
            'uptime': uptime,
            'log_counts': self.metrics['log_counts'],
            'total_logs': sum(self.metrics['log_counts'].values()),
            'events_count': len(self.metrics['events']) if self.enable_tracing else 0
        }

    def get_trace(self) -> list:
        """Get trace events if tracing is enabled"""
        if not self.enable_tracing:
            return []
        return self.metrics['events']

    def clear_trace(self):
        """Clear trace events"""
        if self.enable_tracing:
            self.metrics['events'] = []
