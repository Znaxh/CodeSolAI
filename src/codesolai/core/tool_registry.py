"""
Tool Registry for managing and executing agent tools
"""

import asyncio
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime

from .logger import Logger
from ..tools.filesystem_tool import FilesystemTool
from ..tools.exec_tool import ExecTool
from ..tools.analysis_tool import AnalysisTool
from ..tools.network_tool import NetworkTool


class ToolRegistry:
    """Registry for managing and executing agent tools"""

    def __init__(self, logger: Logger, security_config: Dict[str, Any], max_concurrent: int = 3):
        self.logger = logger
        self.security_config = security_config
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        # Event handlers
        self.on_tool_start: Optional[Callable] = None
        self.on_tool_complete: Optional[Callable] = None
        self.on_tool_error: Optional[Callable] = None
        
        # Initialize tools
        self.tools = {}
        self._register_default_tools()
        
        self.logger.info('Tool registry initialized', {
            'max_concurrent': max_concurrent,
            'tools_count': len(self.tools)
        })

    def _register_default_tools(self):
        """Register default tools"""
        # Filesystem operations
        self.tools['read_file'] = FilesystemTool('read_file', self.logger, self.security_config)
        self.tools['write_file'] = FilesystemTool('write_file', self.logger, self.security_config)
        self.tools['list_directory'] = FilesystemTool('list_directory', self.logger, self.security_config)
        self.tools['create_directory'] = FilesystemTool('create_directory', self.logger, self.security_config)
        self.tools['delete_file'] = FilesystemTool('delete_file', self.logger, self.security_config)
        self.tools['copy_file'] = FilesystemTool('copy_file', self.logger, self.security_config)
        self.tools['move_file'] = FilesystemTool('move_file', self.logger, self.security_config)
        self.tools['search_files'] = FilesystemTool('search_files', self.logger, self.security_config)
        self.tools['get_stats'] = FilesystemTool('get_stats', self.logger, self.security_config)

        # Command execution
        self.tools['execute_command'] = ExecTool('execute_command', self.logger, self.security_config)
        self.tools['install_package'] = ExecTool('install_package', self.logger, self.security_config)
        self.tools['run_script'] = ExecTool('run_script', self.logger, self.security_config)
        self.tools['check_command'] = ExecTool('check_command', self.logger, self.security_config)

        # Analysis tools
        self.tools['analyze_code'] = AnalysisTool('analyze_code', self.logger, self.security_config)
        self.tools['analyze_file'] = AnalysisTool('analyze_file', self.logger, self.security_config)

        # Network tools
        self.tools['http_request'] = NetworkTool('http_request', self.logger, self.security_config)
        self.tools['download_file'] = NetworkTool('download_file', self.logger, self.security_config)
        self.tools['ping'] = NetworkTool('ping', self.logger, self.security_config)

    def register_tool(self, name: str, tool_instance):
        """Register a custom tool"""
        self.tools[name] = tool_instance
        self.logger.info('Tool registered', {'name': name})

    def unregister_tool(self, name: str):
        """Unregister a tool"""
        if name in self.tools:
            del self.tools[name]
            self.logger.info('Tool unregistered', {'name': name})

    def get_available_tools(self) -> List[str]:
        """Get list of available tools"""
        return list(self.tools.keys())

    def get_tool_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool"""
        if name not in self.tools:
            return None
        
        tool = self.tools[name]
        return {
            'name': name,
            'description': getattr(tool, 'description', 'No description available'),
            'parameters': getattr(tool, 'parameters', {}),
            'security_level': getattr(tool, 'security_level', 'medium')
        }

    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any], conversation_id: str) -> Dict[str, Any]:
        """Execute a tool with the given parameters"""
        if tool_name not in self.tools:
            error_msg = f"Tool '{tool_name}' not found"
            self.logger.error(error_msg, {'available_tools': list(self.tools.keys())})
            return {
                'success': False,
                'error': error_msg,
                'tool': tool_name,
                'parameters': parameters
            }

        # Use semaphore to limit concurrent executions
        async with self.semaphore:
            start_time = datetime.now()
            
            # Notify start
            if self.on_tool_start:
                self.on_tool_start({
                    'tool': tool_name,
                    'parameters': parameters,
                    'conversation_id': conversation_id,
                    'start_time': start_time
                })

            try:
                tool = self.tools[tool_name]
                
                # Validate security constraints
                self._validate_security(tool_name, parameters)
                
                # Execute the tool
                result = await tool.execute(parameters)
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                # Prepare success result
                execution_result = {
                    'success': True,
                    'result': result,
                    'tool': tool_name,
                    'parameters': parameters,
                    'duration': duration,
                    'conversation_id': conversation_id
                }
                
                # Notify completion
                if self.on_tool_complete:
                    self.on_tool_complete(execution_result)
                
                self.logger.info('Tool executed successfully', {
                    'tool': tool_name,
                    'duration': duration,
                    'conversation_id': conversation_id
                })
                
                return execution_result

            except Exception as error:
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                # Prepare error result
                execution_result = {
                    'success': False,
                    'error': str(error),
                    'tool': tool_name,
                    'parameters': parameters,
                    'duration': duration,
                    'conversation_id': conversation_id
                }
                
                # Notify error
                if self.on_tool_error:
                    self.on_tool_error(execution_result)
                
                self.logger.error('Tool execution failed', {
                    'tool': tool_name,
                    'error': str(error),
                    'duration': duration,
                    'conversation_id': conversation_id
                })
                
                return execution_result

    def _validate_security(self, tool_name: str, parameters: Dict[str, Any]):
        """Validate security constraints for tool execution"""
        tool = self.tools[tool_name]
        
        # Check if tool has security validation
        if hasattr(tool, 'validate_security'):
            tool.validate_security(parameters, self.security_config)
        
        # Additional global security checks can be added here
        # For example, checking against blocked commands, file paths, etc.

    async def execute_multiple_tools(self, tool_calls: List[Dict[str, Any]], conversation_id: str) -> List[Dict[str, Any]]:
        """Execute multiple tools concurrently"""
        tasks = []
        
        for tool_call in tool_calls:
            task = self.execute_tool(
                tool_call['tool'],
                tool_call.get('parameters', {}),
                conversation_id
            )
            tasks.append(task)
        
        # Execute all tools concurrently (limited by semaphore)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'success': False,
                    'error': str(result),
                    'tool': tool_calls[i]['tool'],
                    'parameters': tool_calls[i].get('parameters', {}),
                    'conversation_id': conversation_id
                })
            else:
                processed_results.append(result)
        
        return processed_results

    def get_tool_usage_stats(self) -> Dict[str, Any]:
        """Get tool usage statistics"""
        # This would be implemented with proper metrics collection
        # For now, return basic info
        return {
            'total_tools': len(self.tools),
            'available_tools': list(self.tools.keys()),
            'max_concurrent': self.max_concurrent
        }

    async def shutdown(self):
        """Shutdown the tool registry"""
        self.logger.info('Shutting down tool registry')
        
        # Cleanup tools if they have shutdown methods
        for tool in self.tools.values():
            if hasattr(tool, 'shutdown'):
                try:
                    await tool.shutdown()
                except Exception as error:
                    self.logger.error('Error shutting down tool', {
                        'tool': str(tool),
                        'error': str(error)
                    })
