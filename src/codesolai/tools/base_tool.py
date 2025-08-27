"""
Base tool class for CodeSolAI agent tools
"""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from ..core.logger import Logger


@dataclass
class ToolValidation:
    """Tool validation result"""
    valid: bool = True
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


@dataclass
class ToolMetadata:
    """Tool metadata"""
    name: str
    version: str = "1.0.0"
    description: str = ""
    capabilities: List[str] = None
    security_level: str = "medium"  # low, medium, high
    parameters: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []
        if self.parameters is None:
            self.parameters = {}


class BaseTool(ABC):
    """Base class for all agent tools"""

    def __init__(self, name: str, logger: Logger, security_config: Dict[str, Any]):
        self.name = name
        self.logger = logger
        self.security_config = security_config
        self.metadata = self._get_metadata()
        
        self.logger.debug(f'Tool {name} initialized', {
            'security_level': self.metadata.security_level,
            'capabilities': len(self.metadata.capabilities)
        })

    @abstractmethod
    def _get_metadata(self) -> ToolMetadata:
        """Get tool metadata - must be implemented by subclasses"""
        pass

    @abstractmethod
    async def _execute_internal(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Internal execution method - must be implemented by subclasses"""
        pass

    async def validate_action(self, parameters: Dict[str, Any]) -> ToolValidation:
        """Validate action before execution - can be overridden by subclasses"""
        validation = ToolValidation()
        
        # Basic parameter validation
        if not isinstance(parameters, dict):
            validation.valid = False
            validation.errors.append("Parameters must be a dictionary")
            return validation
        
        # Check required parameters if defined in metadata
        required_params = self.metadata.parameters.get('required', [])
        for param in required_params:
            if param not in parameters:
                validation.valid = False
                validation.errors.append(f"Required parameter '{param}' is missing")
        
        return validation

    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Main execution method with validation and logging"""
        start_time = datetime.now()
        
        try:
            # Validate action
            validation = await self.validate_action(parameters)
            if not validation.valid:
                return {
                    'success': False,
                    'error': 'Validation failed',
                    'validation_errors': validation.errors,
                    'validation_warnings': validation.warnings,
                    'tool': self.name,
                    'parameters': parameters
                }
            
            # Log warnings if any
            if validation.warnings:
                for warning in validation.warnings:
                    self.logger.warn(f'Tool {self.name} warning: {warning}')
            
            # Execute the tool
            result = await self._execute_internal(parameters)
            
            # Calculate execution time
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Log performance
            self.logger.debug(f'Tool {self.name} executed successfully', {
                'duration': duration,
                'parameters_count': len(parameters),
                'success': True
            })
            
            # Return success result
            return {
                'success': True,
                'result': result,
                'tool': self.name,
                'parameters': parameters,
                'duration': duration,
                'timestamp': end_time
            }
            
        except Exception as error:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Log error
            self.logger.error(f'Tool {self.name} execution failed', {
                'error': str(error),
                'duration': duration,
                'parameters_count': len(parameters) if isinstance(parameters, dict) else 0
            })
            
            # Return error result
            return {
                'success': False,
                'error': str(error),
                'tool': self.name,
                'parameters': parameters,
                'duration': duration,
                'timestamp': end_time
            }

    def validate_security(self, parameters: Dict[str, Any], security_config: Dict[str, Any]):
        """Validate security constraints - can be overridden by subclasses"""
        # Basic security validation
        # Subclasses should implement specific security checks
        pass

    def get_metadata(self) -> ToolMetadata:
        """Get tool metadata"""
        return self.metadata

    def get_capabilities(self) -> List[str]:
        """Get tool capabilities"""
        return self.metadata.capabilities

    def get_security_level(self) -> str:
        """Get tool security level"""
        return self.metadata.security_level

    async def shutdown(self):
        """Shutdown the tool - can be overridden by subclasses"""
        self.logger.debug(f'Tool {self.name} shutting down')

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, security_level={self.metadata.security_level})"

    def __repr__(self) -> str:
        return self.__str__()
