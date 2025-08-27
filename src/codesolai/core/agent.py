"""
Core Agent class implementing sophisticated reasoning and tool execution
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

from ..utils import Utils
from .logger import Logger
from .tool_registry import ToolRegistry
from .conversation_manager import ConversationManager
from .reasoning_engine import ReasoningEngine
from .context_manager import ContextManager


class AgentState(Enum):
    """Agent state enumeration"""
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    ERROR = "error"


@dataclass
class AgentMetrics:
    """Agent performance metrics"""
    conversations: int = 0
    tool_calls: int = 0
    errors: int = 0
    total_thinking_time: float = 0.0
    average_response_time: float = 0.0


@dataclass
class AgentConfig:
    """Agent configuration"""
    # Basic settings
    id: Optional[str] = None
    name: str = "codesolai-agent"
    model: str = "claude-3-5-sonnet-20241022"
    provider: str = "claude"
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4000
    
    # Reasoning settings
    reasoning_effort: str = "medium"  # low, medium, high, maximum
    max_iterations: int = 10
    enable_reflection: bool = True
    enable_planning: bool = True
    
    # Tool settings
    tools_enabled: bool = True
    auto_approve: bool = True
    confirmation_required: bool = False
    max_concurrent_tools: int = 3
    
    # Context settings
    max_context_size: int = 100000
    compression_threshold: float = 0.8
    retention_strategy: str = "importance"  # fifo, importance, recency
    
    # Security settings
    allowed_paths: List[str] = field(default_factory=lambda: ["./"])
    allowed_commands: Optional[List[str]] = None
    blocked_commands: List[str] = field(default_factory=lambda: [
        "rm -rf", "sudo", "format", "fdisk", "mkfs", "dd", "shutdown", "reboot"
    ])
    max_file_size: int = 10485760  # 10MB
    max_execution_time: Optional[int] = None
    max_output_size: Optional[int] = None
    sandbox_mode: bool = False
    
    # Logging settings
    log_level: str = "info"
    enable_metrics: bool = True
    enable_tracing: bool = False


class Agent:
    """
    Core Agent class implementing sophisticated reasoning and tool execution
    This is the main orchestrator that coordinates all agent activities
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize the agent with configuration"""
        self.config = config or AgentConfig()
        
        # Generate ID if not provided
        if not self.config.id:
            self.config.id = str(uuid.uuid4())
        
        # Initialize core properties
        self.id = self.config.id
        self.name = self.config.name
        self.state = AgentState.IDLE
        self.start_time = datetime.now()
        self.metrics = AgentMetrics()
        
        # Initialize core components
        self.logger = Logger(
            agent_id=self.id,
            level=self.config.log_level,
            enable_metrics=self.config.enable_metrics,
            enable_tracing=self.config.enable_tracing
        )
        
        self.tool_registry = ToolRegistry(
            logger=self.logger,
            security_config={
                'allowed_paths': self.config.allowed_paths,
                'allowed_commands': self.config.allowed_commands,
                'blocked_commands': self.config.blocked_commands,
                'max_file_size': self.config.max_file_size,
                'max_execution_time': self.config.max_execution_time,
                'max_output_size': self.config.max_output_size,
                'sandbox_mode': self.config.sandbox_mode
            },
            max_concurrent=self.config.max_concurrent_tools
        )
        
        self.conversation_manager = ConversationManager(
            logger=self.logger,
            agent_id=self.id
        )
        
        self.reasoning_engine = ReasoningEngine(
            logger=self.logger,
            effort=self.config.reasoning_effort,
            max_iterations=self.config.max_iterations,
            enable_reflection=self.config.enable_reflection,
            enable_planning=self.config.enable_planning
        )
        
        self.context_manager = ContextManager(
            logger=self.logger,
            max_size=self.config.max_context_size,
            compression_threshold=self.config.compression_threshold,
            retention_strategy=self.config.retention_strategy
        )
        
        # Setup event handlers
        self.setup_event_handlers()
        
        self.logger.info('Agent initialized', {
            'id': self.id,
            'name': self.name,
            'config': self.config.__dict__
        })

    def setup_event_handlers(self):
        """Setup event handlers for component coordination"""
        # Tool execution events
        self.tool_registry.on_tool_start = self._on_tool_start
        self.tool_registry.on_tool_complete = self._on_tool_complete
        self.tool_registry.on_tool_error = self._on_tool_error
        
        # Reasoning events
        self.reasoning_engine.on_reasoning_start = self._on_reasoning_start
        self.reasoning_engine.on_reasoning_complete = self._on_reasoning_complete
        
        # Conversation events
        self.conversation_manager.on_conversation_start = self._on_conversation_start
        self.conversation_manager.on_conversation_end = self._on_conversation_end

    def _on_tool_start(self, data: Dict[str, Any]):
        """Handle tool start event"""
        self.logger.debug('Tool execution started', data)

    def _on_tool_complete(self, data: Dict[str, Any]):
        """Handle tool complete event"""
        self.metrics.tool_calls += 1
        self.logger.debug('Tool execution completed', data)

    def _on_tool_error(self, data: Dict[str, Any]):
        """Handle tool error event"""
        self.metrics.errors += 1
        self.logger.error('Tool execution failed', data)

    def _on_reasoning_start(self, data: Dict[str, Any]):
        """Handle reasoning start event"""
        self.state = AgentState.THINKING
        self.logger.debug('Reasoning started', data)

    def _on_reasoning_complete(self, data: Dict[str, Any]):
        """Handle reasoning complete event"""
        duration = data.get('duration', 0)
        self.metrics.total_thinking_time += duration
        self.logger.debug('Reasoning completed', data)

    def _on_conversation_start(self, data: Dict[str, Any]):
        """Handle conversation start event"""
        self.metrics.conversations += 1
        self.logger.debug('Conversation started', data)

    def _on_conversation_end(self, data: Dict[str, Any]):
        """Handle conversation end event"""
        self.state = AgentState.IDLE
        self.logger.debug('Conversation ended', data)

    async def process_input(self, input_text: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main entry point for processing user input
        This implements the core agent reasoning loop
        """
        start_time = datetime.now()
        conversation_id = str(uuid.uuid4())
        options = options or {}

        try:
            self.logger.info('Processing input', {
                'conversation_id': conversation_id,
                'input_length': len(input_text),
                'options': options
            })

            # Start conversation
            conversation = await self.conversation_manager.start_conversation({
                'id': conversation_id,
                'input': input_text,
                'options': options,
                'agent_id': self.id
            })

            # Build context for reasoning
            context = await self.context_manager.build_context({
                'input': input_text,
                'conversation': conversation,
                'options': options
            })

            # Engage reasoning engine
            reasoning_result = await self.reasoning_engine.process({
                'input': input_text,
                'context': context,
                'conversation': conversation,
                'options': options
            })

            # Execute actions if any were planned
            execution_results = []
            if reasoning_result.get('actions') and self.config.tools_enabled:
                execution_results = await self._execute_actions(
                    reasoning_result['actions'],
                    conversation_id,
                    options
                )

            # End conversation
            await self.conversation_manager.end_conversation(conversation_id, {
                'reasoning': reasoning_result,
                'execution_results': execution_results
            })

            # Calculate metrics
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            self.metrics.average_response_time = (
                (self.metrics.average_response_time * (self.metrics.conversations - 1) + duration) /
                self.metrics.conversations
            )

            return {
                'conversation_id': conversation_id,
                'response': reasoning_result.get('response', ''),
                'actions_executed': len(execution_results),
                'execution_results': execution_results,
                'reasoning': reasoning_result,
                'duration': duration,
                'metrics': self.metrics.__dict__
            }

        except Exception as error:
            self.metrics.errors += 1
            self.state = AgentState.ERROR
            self.logger.error('Error processing input', {
                'conversation_id': conversation_id,
                'error': str(error)
            })
            raise

    async def _execute_actions(self, actions: List[Dict[str, Any]], conversation_id: str, options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute planned actions using the tool registry"""
        results = []
        
        for action in actions:
            try:
                if not self.config.auto_approve and self.config.confirmation_required:
                    # In a real implementation, this would prompt the user
                    # For now, we'll assume approval
                    pass
                
                result = await self.tool_registry.execute_tool(
                    action['tool'],
                    action.get('parameters', {}),
                    conversation_id
                )
                results.append(result)
                
            except Exception as error:
                self.logger.error('Action execution failed', {
                    'action': action,
                    'error': str(error)
                })
                results.append({
                    'action': action,
                    'success': False,
                    'error': str(error)
                })
        
        return results

    async def shutdown(self):
        """Shutdown the agent and cleanup resources"""
        self.logger.info('Shutting down agent', {'id': self.id})
        
        # Cleanup components
        if hasattr(self.tool_registry, 'shutdown'):
            await self.tool_registry.shutdown()
        
        if hasattr(self.conversation_manager, 'shutdown'):
            await self.conversation_manager.shutdown()
        
        if hasattr(self.reasoning_engine, 'shutdown'):
            await self.reasoning_engine.shutdown()
        
        if hasattr(self.context_manager, 'shutdown'):
            await self.context_manager.shutdown()
        
        self.state = AgentState.IDLE

    def get_metrics(self) -> Dict[str, Any]:
        """Get current agent metrics"""
        return {
            'id': self.id,
            'name': self.name,
            'state': self.state.value,
            'uptime': (datetime.now() - self.start_time).total_seconds(),
            'metrics': self.metrics.__dict__
        }
