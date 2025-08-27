"""
Execution tool for running commands with security controls
"""

import asyncio
import shlex
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path

from .base_tool import BaseTool, ToolMetadata, ToolValidation
from ..core.logger import Logger


class ExecTool(BaseTool):
    """Enhanced execution tool with security controls and comprehensive command handling"""

    def __init__(self, operation: str, logger: Logger, security_config: Dict[str, Any]):
        self.operation = operation
        self.allowed_commands = security_config.get('allowed_commands', [
            'npm', 'node', 'git', 'ls', 'pwd', 'cat', 'echo', 'mkdir', 'touch',
            'grep', 'find', 'curl', 'wget', 'which', 'whereis', 'ps', 'sleep',
            'python', 'python3', 'pip', 'pip3', 'uv'
        ])
        self.blocked_commands = security_config.get('blocked_commands', [
            'rm', 'rmdir', 'del', 'format', 'fdisk', 'mkfs', 'dd', 'sudo', 'su',
            'chmod', 'chown', 'passwd', 'shutdown', 'reboot', 'halt', 'init'
        ])
        self.max_execution_time = security_config.get('max_execution_time', 30)  # 30 seconds
        self.max_output_size = security_config.get('max_output_size', 1048576)  # 1MB
        self.working_directory = Path.cwd()
        
        super().__init__(f"exec_{operation}", logger, security_config)

    def _get_metadata(self) -> ToolMetadata:
        """Get execution tool metadata"""
        return ToolMetadata(
            name=f"exec_{self.operation}",
            version="2.0.0",
            description=f"Command execution operation: {self.operation}",
            capabilities=[self.operation],
            security_level="high",
            parameters={
                'required': self._get_required_parameters(),
                'optional': self._get_optional_parameters()
            }
        )

    def _get_required_parameters(self) -> List[str]:
        """Get required parameters based on operation"""
        if self.operation in ['execute_command', 'run_script']:
            return ['command']
        elif self.operation == 'install_package':
            return ['package']
        elif self.operation == 'spawn_process':
            return ['command', 'args']
        return []

    def _get_optional_parameters(self) -> List[str]:
        """Get optional parameters based on operation"""
        return ['cwd', 'env', 'timeout', 'shell']

    async def validate_action(self, parameters: Dict[str, Any]) -> ToolValidation:
        """Validate execution action"""
        validation = await super().validate_action(parameters)
        
        if not validation.valid:
            return validation
        
        # Validate command safety
        if 'command' in parameters:
            command = parameters['command']
            safety_check = self._is_command_safe(command)
            
            if not safety_check['safe']:
                validation.valid = False
                validation.errors.append(safety_check['reason'])
            
            if safety_check.get('warnings'):
                validation.warnings.extend(safety_check['warnings'])
        
        return validation

    def _is_command_safe(self, command: str) -> Dict[str, Any]:
        """Check if a command is safe to execute"""
        result = {'safe': True, 'reason': '', 'warnings': []}
        
        try:
            # Parse command to get the base command
            parts = shlex.split(command)
            if not parts:
                result['safe'] = False
                result['reason'] = 'Empty command'
                return result
            
            base_command = parts[0]
            
            # Check against blocked commands
            for blocked in self.blocked_commands:
                if blocked in command.lower():
                    result['safe'] = False
                    result['reason'] = f'Command contains blocked term: {blocked}'
                    return result
            
            # Check if command is in allowed list (if specified)
            if self.allowed_commands:
                command_allowed = False
                for allowed in self.allowed_commands:
                    if base_command == allowed or base_command.endswith(f'/{allowed}'):
                        command_allowed = True
                        break
                
                if not command_allowed:
                    result['safe'] = False
                    result['reason'] = f'Command not in allowed list: {base_command}'
                    return result
            
            # Check for dangerous patterns
            dangerous_patterns = ['>', '>>', '|', '&', ';', '$(', '`']
            for pattern in dangerous_patterns:
                if pattern in command:
                    result['warnings'].append(f'Command contains potentially dangerous pattern: {pattern}')
            
            # Check for path traversal
            if '..' in command:
                result['warnings'].append('Command contains ".." - potential path traversal')
            
        except Exception as error:
            result['safe'] = False
            result['reason'] = f'Error parsing command: {str(error)}'
        
        return result

    async def _execute_internal(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute command operation"""
        if self.operation == 'execute_command':
            return await self._execute_command(parameters)
        elif self.operation == 'install_package':
            return await self._install_package(parameters)
        elif self.operation == 'run_script':
            return await self._run_script(parameters)
        elif self.operation == 'spawn_process':
            return await self._spawn_process(parameters)
        elif self.operation == 'check_command':
            return await self._check_command(parameters)
        elif self.operation == 'get_environment':
            return await self._get_environment(parameters)
        else:
            raise ValueError(f"Unknown execution operation: {self.operation}")

    async def _execute_command(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a shell command"""
        command = parameters['command']
        cwd = parameters.get('cwd', str(self.working_directory))
        env = parameters.get('env', None)
        timeout = parameters.get('timeout', self.max_execution_time)
        shell = parameters.get('shell', True)
        
        try:
            # Create subprocess
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
                env=env
            )
            
            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise TimeoutError(f"Command timed out after {timeout} seconds")
            
            # Decode output
            stdout_text = stdout.decode('utf-8', errors='replace')
            stderr_text = stderr.decode('utf-8', errors='replace')
            
            # Check output size
            if len(stdout_text) > self.max_output_size:
                stdout_text = stdout_text[:self.max_output_size] + '\n... (output truncated)'
            
            if len(stderr_text) > self.max_output_size:
                stderr_text = stderr_text[:self.max_output_size] + '\n... (output truncated)'
            
            return {
                'command': command,
                'return_code': process.returncode,
                'stdout': stdout_text,
                'stderr': stderr_text,
                'success': process.returncode == 0,
                'cwd': cwd
            }
            
        except Exception as error:
            return {
                'command': command,
                'return_code': -1,
                'stdout': '',
                'stderr': str(error),
                'success': False,
                'error': str(error),
                'cwd': cwd
            }

    async def _install_package(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Install a package using appropriate package manager"""
        package = parameters['package']
        manager = parameters.get('manager', 'pip')  # pip, npm, etc.
        
        if manager == 'pip':
            command = f"pip install {package}"
        elif manager == 'npm':
            command = f"npm install {package}"
        elif manager == 'uv':
            command = f"uv add {package}"
        else:
            raise ValueError(f"Unsupported package manager: {manager}")
        
        # Execute the install command
        install_params = {
            'command': command,
            **{k: v for k, v in parameters.items() if k not in ['package', 'manager']}
        }
        
        result = await self._execute_command(install_params)
        result['package'] = package
        result['manager'] = manager
        
        return result

    async def _run_script(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Run a script file"""
        script_path = parameters['script_path']
        interpreter = parameters.get('interpreter', 'python')
        args = parameters.get('args', [])
        
        # Build command
        command_parts = [interpreter, script_path] + args
        command = ' '.join(shlex.quote(part) for part in command_parts)
        
        # Execute the script
        script_params = {
            'command': command,
            **{k: v for k, v in parameters.items() if k not in ['script_path', 'interpreter', 'args']}
        }
        
        result = await self._execute_command(script_params)
        result['script_path'] = script_path
        result['interpreter'] = interpreter
        result['args'] = args
        
        return result

    async def _spawn_process(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Spawn a background process"""
        command = parameters['command']
        args = parameters.get('args', [])
        cwd = parameters.get('cwd', str(self.working_directory))
        
        try:
            # Create subprocess that runs in background
            process = await asyncio.create_subprocess_exec(
                command,
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            
            return {
                'command': command,
                'args': args,
                'pid': process.pid,
                'spawned': True,
                'cwd': cwd
            }
            
        except Exception as error:
            return {
                'command': command,
                'args': args,
                'spawned': False,
                'error': str(error),
                'cwd': cwd
            }

    async def _check_command(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Check if a command exists and is executable"""
        command = parameters['command']
        
        try:
            # Use 'which' command to check if command exists
            result = await self._execute_command({
                'command': f'which {shlex.quote(command)}',
                'timeout': 5
            })
            
            exists = result['success'] and result['stdout'].strip()
            
            return {
                'command': command,
                'exists': exists,
                'path': result['stdout'].strip() if exists else None,
                'checked': True
            }
            
        except Exception as error:
            return {
                'command': command,
                'exists': False,
                'error': str(error),
                'checked': False
            }

    async def _get_environment(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get environment variables"""
        var_name = parameters.get('variable')
        
        if var_name:
            # Get specific environment variable
            value = os.environ.get(var_name)
            return {
                'variable': var_name,
                'value': value,
                'exists': value is not None
            }
        else:
            # Get all environment variables (filtered for security)
            safe_vars = {}
            for key, value in os.environ.items():
                # Filter out sensitive variables
                if not any(sensitive in key.lower() for sensitive in ['password', 'secret', 'key', 'token']):
                    safe_vars[key] = value
            
            return {
                'environment': safe_vars,
                'count': len(safe_vars)
            }
