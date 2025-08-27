"""
Filesystem tool for file operations with security controls
"""

import os
import shutil
import glob
import aiofiles
from pathlib import Path
from typing import Dict, Any, List, Optional

from .base_tool import BaseTool, ToolMetadata, ToolValidation
from ..core.logger import Logger


class FilesystemTool(BaseTool):
    """Enhanced filesystem tool with comprehensive file operations and security"""

    def __init__(self, operation: str, logger: Logger, security_config: Dict[str, Any]):
        self.operation = operation
        self.allowed_paths = security_config.get('allowed_paths', ['./'])
        self.max_file_size = security_config.get('max_file_size', 10 * 1024 * 1024)  # 10MB
        self.blocked_extensions = security_config.get('blocked_extensions', ['.exe', '.bat', '.sh'])
        
        super().__init__(f"filesystem_{operation}", logger, security_config)

    def _get_metadata(self) -> ToolMetadata:
        """Get filesystem tool metadata"""
        return ToolMetadata(
            name=f"filesystem_{self.operation}",
            version="2.0.0",
            description=f"Filesystem operation: {self.operation}",
            capabilities=[self.operation],
            security_level="high",
            parameters={
                'required': self._get_required_parameters(),
                'optional': self._get_optional_parameters()
            }
        )

    def _get_required_parameters(self) -> List[str]:
        """Get required parameters based on operation"""
        if self.operation in ['read_file', 'delete_file', 'get_stats']:
            return ['path']
        elif self.operation in ['write_file', 'create_file']:
            return ['path', 'content']
        elif self.operation in ['copy_file', 'move_file']:
            return ['source', 'destination']
        elif self.operation in ['list_directory', 'create_directory']:
            return ['path']
        elif self.operation == 'search_files':
            return ['pattern']
        return []

    def _get_optional_parameters(self) -> List[str]:
        """Get optional parameters based on operation"""
        if self.operation == 'write_file':
            return ['encoding', 'mode']
        elif self.operation == 'list_directory':
            return ['recursive', 'include_hidden']
        elif self.operation == 'search_files':
            return ['path', 'recursive']
        return []

    async def validate_action(self, parameters: Dict[str, Any]) -> ToolValidation:
        """Validate filesystem action"""
        validation = await super().validate_action(parameters)
        
        if not validation.valid:
            return validation
        
        # Validate file paths
        paths_to_check = []
        
        if 'path' in parameters:
            paths_to_check.append(parameters['path'])
        if 'source' in parameters:
            paths_to_check.append(parameters['source'])
        if 'destination' in parameters:
            paths_to_check.append(parameters['destination'])
        
        for file_path in paths_to_check:
            path_validation = self._validate_path(file_path)
            if not path_validation.valid:
                validation.valid = False
                validation.errors.extend(path_validation.errors)
            validation.warnings.extend(path_validation.warnings)
        
        return validation

    def _validate_path(self, file_path: str) -> ToolValidation:
        """Validate a single file path"""
        validation = ToolValidation()
        
        try:
            resolved_path = Path(file_path).resolve()
            
            # Check if path is allowed
            is_allowed = False
            for allowed_path in self.allowed_paths:
                allowed_resolved = Path(allowed_path).resolve()
                try:
                    resolved_path.relative_to(allowed_resolved)
                    is_allowed = True
                    break
                except ValueError:
                    continue
            
            if not is_allowed:
                validation.valid = False
                validation.errors.append(f"Path {file_path} is not in allowed paths")
            
            # Check for blocked extensions
            if resolved_path.suffix in self.blocked_extensions:
                validation.valid = False
                validation.errors.append(f"File extension {resolved_path.suffix} is blocked")
            
            # Check for dangerous path traversal
            if '..' in file_path:
                validation.warnings.append('Path contains ".." - potential security risk')
            
        except Exception as error:
            validation.valid = False
            validation.errors.append(f"Invalid path: {str(error)}")
        
        return validation

    async def _execute_internal(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute filesystem operation"""
        if self.operation == 'read_file':
            return await self._read_file(parameters)
        elif self.operation == 'write_file':
            return await self._write_file(parameters)
        elif self.operation == 'create_file':
            return await self._create_file(parameters)
        elif self.operation == 'delete_file':
            return await self._delete_file(parameters)
        elif self.operation == 'list_directory':
            return await self._list_directory(parameters)
        elif self.operation == 'create_directory':
            return await self._create_directory(parameters)
        elif self.operation == 'copy_file':
            return await self._copy_file(parameters)
        elif self.operation == 'move_file':
            return await self._move_file(parameters)
        elif self.operation == 'search_files':
            return await self._search_files(parameters)
        elif self.operation == 'get_stats':
            return await self._get_stats(parameters)
        else:
            raise ValueError(f"Unknown filesystem operation: {self.operation}")

    async def _read_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Read file contents"""
        file_path = parameters['path']
        encoding = parameters.get('encoding', 'utf-8')
        
        path_obj = Path(file_path)
        
        if not path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not path_obj.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        # Check file size
        file_size = path_obj.stat().st_size
        if file_size > self.max_file_size:
            raise ValueError(f"File too large: {file_size} bytes (max: {self.max_file_size})")
        
        async with aiofiles.open(file_path, 'r', encoding=encoding) as f:
            content = await f.read()
        
        return {
            'content': content,
            'size': file_size,
            'encoding': encoding,
            'path': str(path_obj.resolve())
        }

    async def _write_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Write content to file"""
        file_path = parameters['path']
        content = parameters['content']
        encoding = parameters.get('encoding', 'utf-8')
        mode = parameters.get('mode', 'w')
        
        path_obj = Path(file_path)
        
        # Create parent directories if they don't exist
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        # Check content size
        content_size = len(content.encode(encoding))
        if content_size > self.max_file_size:
            raise ValueError(f"Content too large: {content_size} bytes (max: {self.max_file_size})")
        
        async with aiofiles.open(file_path, mode, encoding=encoding) as f:
            await f.write(content)
        
        return {
            'path': str(path_obj.resolve()),
            'size': content_size,
            'encoding': encoding,
            'mode': mode
        }

    async def _create_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new file"""
        return await self._write_file(parameters)

    async def _delete_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a file"""
        file_path = parameters['path']
        path_obj = Path(file_path)
        
        if not path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if path_obj.is_file():
            path_obj.unlink()
        elif path_obj.is_dir():
            shutil.rmtree(path_obj)
        else:
            raise ValueError(f"Unknown file type: {file_path}")
        
        return {
            'path': str(path_obj.resolve()),
            'deleted': True
        }

    async def _list_directory(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """List directory contents"""
        dir_path = parameters['path']
        recursive = parameters.get('recursive', False)
        include_hidden = parameters.get('include_hidden', False)
        
        path_obj = Path(dir_path)
        
        if not path_obj.exists():
            raise FileNotFoundError(f"Directory not found: {dir_path}")
        
        if not path_obj.is_dir():
            raise ValueError(f"Path is not a directory: {dir_path}")
        
        items = []
        
        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"
        
        for item in path_obj.glob(pattern):
            if not include_hidden and item.name.startswith('.'):
                continue
            
            stat = item.stat()
            items.append({
                'name': item.name,
                'path': str(item.resolve()),
                'type': 'file' if item.is_file() else 'directory',
                'size': stat.st_size if item.is_file() else None,
                'modified': stat.st_mtime
            })
        
        return {
            'path': str(path_obj.resolve()),
            'items': items,
            'count': len(items),
            'recursive': recursive
        }

    async def _create_directory(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a directory"""
        dir_path = parameters['path']
        path_obj = Path(dir_path)
        
        path_obj.mkdir(parents=True, exist_ok=True)
        
        return {
            'path': str(path_obj.resolve()),
            'created': True
        }

    async def _copy_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Copy a file"""
        source = parameters['source']
        destination = parameters['destination']
        
        source_path = Path(source)
        dest_path = Path(destination)
        
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source}")
        
        # Create destination directory if needed
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        if source_path.is_file():
            shutil.copy2(source_path, dest_path)
        else:
            shutil.copytree(source_path, dest_path)
        
        return {
            'source': str(source_path.resolve()),
            'destination': str(dest_path.resolve()),
            'copied': True
        }

    async def _move_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Move a file"""
        source = parameters['source']
        destination = parameters['destination']
        
        source_path = Path(source)
        dest_path = Path(destination)
        
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source}")
        
        # Create destination directory if needed
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.move(str(source_path), str(dest_path))
        
        return {
            'source': source,
            'destination': str(dest_path.resolve()),
            'moved': True
        }

    async def _search_files(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Search for files matching a pattern"""
        pattern = parameters['pattern']
        search_path = parameters.get('path', '.')
        recursive = parameters.get('recursive', True)
        
        path_obj = Path(search_path)
        
        if not path_obj.exists():
            raise FileNotFoundError(f"Search path not found: {search_path}")
        
        matches = []
        
        if recursive:
            search_pattern = f"**/{pattern}"
        else:
            search_pattern = pattern
        
        for match in path_obj.glob(search_pattern):
            stat = match.stat()
            matches.append({
                'name': match.name,
                'path': str(match.resolve()),
                'type': 'file' if match.is_file() else 'directory',
                'size': stat.st_size if match.is_file() else None,
                'modified': stat.st_mtime
            })
        
        return {
            'pattern': pattern,
            'search_path': str(path_obj.resolve()),
            'matches': matches,
            'count': len(matches),
            'recursive': recursive
        }

    async def _get_stats(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get file/directory statistics"""
        file_path = parameters['path']
        path_obj = Path(file_path)
        
        if not path_obj.exists():
            raise FileNotFoundError(f"Path not found: {file_path}")
        
        stat = path_obj.stat()
        
        return {
            'path': str(path_obj.resolve()),
            'type': 'file' if path_obj.is_file() else 'directory',
            'size': stat.st_size,
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'accessed': stat.st_atime,
            'permissions': oct(stat.st_mode)[-3:]
        }
