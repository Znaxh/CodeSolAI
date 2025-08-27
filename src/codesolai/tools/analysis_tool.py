"""
Analysis tool for code and file analysis
"""

import ast
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional

from .base_tool import BaseTool, ToolMetadata, ToolValidation
from ..core.logger import Logger


class AnalysisTool(BaseTool):
    """Tool for analyzing code and files"""

    def __init__(self, operation: str, logger: Logger, security_config: Dict[str, Any]):
        self.operation = operation
        self.max_file_size = security_config.get('max_file_size', 10 * 1024 * 1024)  # 10MB
        
        super().__init__(f"analysis_{operation}", logger, security_config)

    def _get_metadata(self) -> ToolMetadata:
        """Get analysis tool metadata"""
        return ToolMetadata(
            name=f"analysis_{self.operation}",
            version="1.0.0",
            description=f"Analysis operation: {self.operation}",
            capabilities=[self.operation],
            security_level="medium",
            parameters={
                'required': self._get_required_parameters(),
                'optional': self._get_optional_parameters()
            }
        )

    def _get_required_parameters(self) -> List[str]:
        """Get required parameters based on operation"""
        if self.operation == 'analyze_code':
            return ['code']
        elif self.operation == 'analyze_file':
            return ['path']
        return []

    def _get_optional_parameters(self) -> List[str]:
        """Get optional parameters based on operation"""
        return ['language', 'include_metrics', 'include_structure']

    async def _execute_internal(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute analysis operation"""
        if self.operation == 'analyze_code':
            return await self._analyze_code(parameters)
        elif self.operation == 'analyze_file':
            return await self._analyze_file(parameters)
        else:
            raise ValueError(f"Unknown analysis operation: {self.operation}")

    async def _analyze_code(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code content"""
        code = parameters['code']
        language = parameters.get('language', 'python')
        include_metrics = parameters.get('include_metrics', True)
        include_structure = parameters.get('include_structure', True)
        
        analysis = {
            'language': language,
            'length': len(code),
            'lines': len(code.splitlines()),
            'analysis_type': 'code_content'
        }
        
        if language.lower() == 'python':
            analysis.update(await self._analyze_python_code(code, include_metrics, include_structure))
        elif language.lower() in ['javascript', 'js']:
            analysis.update(await self._analyze_javascript_code(code, include_metrics, include_structure))
        else:
            analysis.update(await self._analyze_generic_code(code, include_metrics, include_structure))
        
        return analysis

    async def _analyze_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a file"""
        file_path = parameters['path']
        include_metrics = parameters.get('include_metrics', True)
        include_structure = parameters.get('include_structure', True)
        
        path_obj = Path(file_path)
        
        if not path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not path_obj.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        # Check file size
        file_size = path_obj.stat().st_size
        if file_size > self.max_file_size:
            raise ValueError(f"File too large: {file_size} bytes (max: {self.max_file_size})")
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        
        # Determine language from file extension
        language = self._detect_language(path_obj.suffix)
        
        analysis = {
            'file_path': str(path_obj.resolve()),
            'file_size': file_size,
            'language': language,
            'length': len(content),
            'lines': len(content.splitlines()),
            'analysis_type': 'file_content'
        }
        
        # Analyze based on detected language
        if language == 'python':
            analysis.update(await self._analyze_python_code(content, include_metrics, include_structure))
        elif language in ['javascript', 'js']:
            analysis.update(await self._analyze_javascript_code(content, include_metrics, include_structure))
        else:
            analysis.update(await self._analyze_generic_code(content, include_metrics, include_structure))
        
        return analysis

    def _detect_language(self, extension: str) -> str:
        """Detect programming language from file extension"""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.xml': 'xml',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.md': 'markdown',
            '.txt': 'text'
        }
        return ext_map.get(extension.lower(), 'unknown')

    async def _analyze_python_code(self, code: str, include_metrics: bool, include_structure: bool) -> Dict[str, Any]:
        """Analyze Python code"""
        analysis = {}
        
        try:
            # Parse AST
            tree = ast.parse(code)
            
            if include_structure:
                structure = {
                    'classes': [],
                    'functions': [],
                    'imports': [],
                    'variables': []
                }
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        structure['classes'].append({
                            'name': node.name,
                            'line': node.lineno,
                            'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                        })
                    elif isinstance(node, ast.FunctionDef):
                        if not any(node.lineno >= cls['line'] for cls in structure['classes']):
                            structure['functions'].append({
                                'name': node.name,
                                'line': node.lineno,
                                'args': len(node.args.args)
                            })
                    elif isinstance(node, (ast.Import, ast.ImportFrom)):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                structure['imports'].append(alias.name)
                        else:
                            module = node.module or ''
                            for alias in node.names:
                                structure['imports'].append(f"{module}.{alias.name}")
                    elif isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                structure['variables'].append({
                                    'name': target.id,
                                    'line': node.lineno
                                })
                
                analysis['structure'] = structure
            
            if include_metrics:
                metrics = {
                    'complexity': self._calculate_complexity(tree),
                    'class_count': len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]),
                    'function_count': len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]),
                    'import_count': len([n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]),
                    'comment_lines': len([line for line in code.splitlines() if line.strip().startswith('#')])
                }
                analysis['metrics'] = metrics
            
            analysis['syntax_valid'] = True
            
        except SyntaxError as e:
            analysis['syntax_valid'] = False
            analysis['syntax_error'] = {
                'message': str(e),
                'line': e.lineno,
                'offset': e.offset
            }
        
        return analysis

    async def _analyze_javascript_code(self, code: str, include_metrics: bool, include_structure: bool) -> Dict[str, Any]:
        """Analyze JavaScript code (basic analysis)"""
        analysis = {}
        
        if include_structure:
            structure = {
                'functions': [],
                'classes': [],
                'variables': [],
                'imports': []
            }
            
            # Basic regex-based analysis for JavaScript
            # Function declarations
            func_pattern = r'function\s+(\w+)\s*\('
            for match in re.finditer(func_pattern, code):
                structure['functions'].append({
                    'name': match.group(1),
                    'type': 'function_declaration'
                })
            
            # Arrow functions
            arrow_pattern = r'(\w+)\s*=\s*\([^)]*\)\s*=>'
            for match in re.finditer(arrow_pattern, code):
                structure['functions'].append({
                    'name': match.group(1),
                    'type': 'arrow_function'
                })
            
            # Class declarations
            class_pattern = r'class\s+(\w+)'
            for match in re.finditer(class_pattern, code):
                structure['classes'].append({
                    'name': match.group(1)
                })
            
            # Import statements
            import_pattern = r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]'
            for match in re.finditer(import_pattern, code):
                structure['imports'].append(match.group(1))
            
            analysis['structure'] = structure
        
        if include_metrics:
            metrics = {
                'function_count': len(re.findall(r'function\s+\w+', code)),
                'class_count': len(re.findall(r'class\s+\w+', code)),
                'comment_lines': len([line for line in code.splitlines() if line.strip().startswith('//')]),
                'semicolon_count': code.count(';')
            }
            analysis['metrics'] = metrics
        
        return analysis

    async def _analyze_generic_code(self, code: str, include_metrics: bool, include_structure: bool) -> Dict[str, Any]:
        """Generic code analysis for unknown languages"""
        analysis = {}
        
        if include_metrics:
            lines = code.splitlines()
            metrics = {
                'blank_lines': len([line for line in lines if not line.strip()]),
                'non_blank_lines': len([line for line in lines if line.strip()]),
                'average_line_length': sum(len(line) for line in lines) / len(lines) if lines else 0,
                'max_line_length': max(len(line) for line in lines) if lines else 0,
                'character_count': len(code),
                'word_count': len(code.split())
            }
            analysis['metrics'] = metrics
        
        if include_structure:
            # Basic structure analysis
            structure = {
                'brackets': {
                    'curly': code.count('{'),
                    'square': code.count('['),
                    'round': code.count('(')
                },
                'indentation_style': self._detect_indentation(code)
            }
            analysis['structure'] = structure
        
        return analysis

    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity of Python code"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity

    def _detect_indentation(self, code: str) -> str:
        """Detect indentation style (spaces vs tabs)"""
        lines = code.splitlines()
        space_count = 0
        tab_count = 0
        
        for line in lines:
            if line.startswith('    '):
                space_count += 1
            elif line.startswith('\t'):
                tab_count += 1
        
        if space_count > tab_count:
            return 'spaces'
        elif tab_count > space_count:
            return 'tabs'
        else:
            return 'mixed_or_none'
