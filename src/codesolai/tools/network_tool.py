"""
Network tool for HTTP requests and network operations
"""

import json
import httpx
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

from .base_tool import BaseTool, ToolMetadata, ToolValidation
from ..core.logger import Logger


class NetworkTool(BaseTool):
    """Tool for network operations and HTTP requests"""

    def __init__(self, operation: str, logger: Logger, security_config: Dict[str, Any]):
        self.operation = operation
        self.allowed_domains = security_config.get('allowed_domains', [])
        self.blocked_domains = security_config.get('blocked_domains', [
            'localhost', '127.0.0.1', '0.0.0.0', '::1'
        ])
        self.max_response_size = security_config.get('max_response_size', 10 * 1024 * 1024)  # 10MB
        self.timeout = security_config.get('network_timeout', 30)
        
        super().__init__(f"network_{operation}", logger, security_config)

    def _get_metadata(self) -> ToolMetadata:
        """Get network tool metadata"""
        return ToolMetadata(
            name=f"network_{self.operation}",
            version="1.0.0",
            description=f"Network operation: {self.operation}",
            capabilities=[self.operation],
            security_level="high",
            parameters={
                'required': self._get_required_parameters(),
                'optional': self._get_optional_parameters()
            }
        )

    def _get_required_parameters(self) -> List[str]:
        """Get required parameters based on operation"""
        if self.operation == 'http_request':
            return ['url']
        elif self.operation == 'download_file':
            return ['url', 'destination']
        elif self.operation == 'ping':
            return ['host']
        return []

    def _get_optional_parameters(self) -> List[str]:
        """Get optional parameters based on operation"""
        return ['method', 'headers', 'data', 'params', 'timeout', 'follow_redirects']

    async def validate_action(self, parameters: Dict[str, Any]) -> ToolValidation:
        """Validate network action"""
        validation = await super().validate_action(parameters)
        
        if not validation.valid:
            return validation
        
        # Validate URL if present
        if 'url' in parameters:
            url_validation = self._validate_url(parameters['url'])
            if not url_validation.valid:
                validation.valid = False
                validation.errors.extend(url_validation.errors)
            validation.warnings.extend(url_validation.warnings)
        
        # Validate host if present
        if 'host' in parameters:
            host_validation = self._validate_host(parameters['host'])
            if not host_validation.valid:
                validation.valid = False
                validation.errors.extend(host_validation.errors)
            validation.warnings.extend(host_validation.warnings)
        
        return validation

    def _validate_url(self, url: str) -> ToolValidation:
        """Validate URL for security"""
        validation = ToolValidation()
        
        try:
            parsed = urlparse(url)
            
            # Check scheme
            if parsed.scheme not in ['http', 'https']:
                validation.valid = False
                validation.errors.append(f"Unsupported URL scheme: {parsed.scheme}")
                return validation
            
            # Check domain
            domain = parsed.hostname
            if not domain:
                validation.valid = False
                validation.errors.append("Invalid URL: no hostname")
                return validation
            
            # Check against blocked domains
            if any(blocked in domain.lower() for blocked in self.blocked_domains):
                validation.valid = False
                validation.errors.append(f"Domain is blocked: {domain}")
                return validation
            
            # Check against allowed domains (if specified)
            if self.allowed_domains:
                if not any(allowed in domain.lower() for allowed in self.allowed_domains):
                    validation.valid = False
                    validation.errors.append(f"Domain not in allowed list: {domain}")
                    return validation
            
            # Check for private IP ranges
            if self._is_private_ip(domain):
                validation.warnings.append(f"URL points to private IP range: {domain}")
            
        except Exception as error:
            validation.valid = False
            validation.errors.append(f"Invalid URL: {str(error)}")
        
        return validation

    def _validate_host(self, host: str) -> ToolValidation:
        """Validate host for security"""
        validation = ToolValidation()
        
        # Check against blocked hosts
        if any(blocked in host.lower() for blocked in self.blocked_domains):
            validation.valid = False
            validation.errors.append(f"Host is blocked: {host}")
            return validation
        
        # Check for private IP ranges
        if self._is_private_ip(host):
            validation.warnings.append(f"Host is in private IP range: {host}")
        
        return validation

    def _is_private_ip(self, host: str) -> bool:
        """Check if host is in private IP range"""
        private_ranges = [
            '127.', '10.', '192.168.', '172.16.', '172.17.', '172.18.',
            '172.19.', '172.20.', '172.21.', '172.22.', '172.23.',
            '172.24.', '172.25.', '172.26.', '172.27.', '172.28.',
            '172.29.', '172.30.', '172.31.', 'localhost'
        ]
        return any(host.startswith(prefix) for prefix in private_ranges)

    async def _execute_internal(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute network operation"""
        if self.operation == 'http_request':
            return await self._http_request(parameters)
        elif self.operation == 'download_file':
            return await self._download_file(parameters)
        elif self.operation == 'ping':
            return await self._ping(parameters)
        else:
            raise ValueError(f"Unknown network operation: {self.operation}")

    async def _http_request(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request"""
        url = parameters['url']
        method = parameters.get('method', 'GET').upper()
        headers = parameters.get('headers', {})
        data = parameters.get('data')
        params = parameters.get('params', {})
        timeout = parameters.get('timeout', self.timeout)
        follow_redirects = parameters.get('follow_redirects', True)
        
        try:
            async with httpx.AsyncClient(
                timeout=timeout,
                follow_redirects=follow_redirects,
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
            ) as client:
                
                # Prepare request data
                request_kwargs = {
                    'method': method,
                    'url': url,
                    'headers': headers,
                    'params': params
                }
                
                if data:
                    if isinstance(data, dict):
                        request_kwargs['json'] = data
                    else:
                        request_kwargs['data'] = data
                
                # Make request
                response = await client.request(**request_kwargs)
                
                # Check response size
                content_length = response.headers.get('content-length')
                if content_length and int(content_length) > self.max_response_size:
                    raise ValueError(f"Response too large: {content_length} bytes (max: {self.max_response_size})")
                
                # Get response content
                try:
                    response_text = response.text
                    if len(response_text) > self.max_response_size:
                        response_text = response_text[:self.max_response_size] + '\n... (response truncated)'
                except Exception:
                    response_text = '<binary content>'
                
                # Try to parse JSON if content type suggests it
                response_json = None
                content_type = response.headers.get('content-type', '')
                if 'application/json' in content_type:
                    try:
                        response_json = response.json()
                    except Exception:
                        pass
                
                return {
                    'url': str(response.url),
                    'method': method,
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'text': response_text,
                    'json': response_json,
                    'success': 200 <= response.status_code < 300,
                    'elapsed': response.elapsed.total_seconds(),
                    'size': len(response.content)
                }
                
        except httpx.TimeoutException:
            return {
                'url': url,
                'method': method,
                'success': False,
                'error': f'Request timed out after {timeout} seconds'
            }
        except Exception as error:
            return {
                'url': url,
                'method': method,
                'success': False,
                'error': str(error)
            }

    async def _download_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Download file from URL"""
        url = parameters['url']
        destination = parameters['destination']
        timeout = parameters.get('timeout', self.timeout)
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                async with client.stream('GET', url) as response:
                    response.raise_for_status()
                    
                    # Check content length
                    content_length = response.headers.get('content-length')
                    if content_length and int(content_length) > self.max_response_size:
                        raise ValueError(f"File too large: {content_length} bytes (max: {self.max_response_size})")
                    
                    # Download file
                    total_size = 0
                    with open(destination, 'wb') as f:
                        async for chunk in response.aiter_bytes():
                            total_size += len(chunk)
                            if total_size > self.max_response_size:
                                raise ValueError(f"File too large: {total_size} bytes (max: {self.max_response_size})")
                            f.write(chunk)
                    
                    return {
                        'url': url,
                        'destination': destination,
                        'size': total_size,
                        'success': True,
                        'downloaded': True
                    }
                    
        except Exception as error:
            return {
                'url': url,
                'destination': destination,
                'success': False,
                'error': str(error),
                'downloaded': False
            }

    async def _ping(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Ping a host (simplified version using HTTP request)"""
        host = parameters['host']
        timeout = parameters.get('timeout', 5)
        
        # For security, we'll do a simple HTTP request instead of actual ping
        try:
            url = f"http://{host}"
            if not host.startswith(('http://', 'https://')):
                url = f"http://{host}"
            else:
                url = host
            
            ping_result = await self._http_request({
                'url': url,
                'method': 'HEAD',
                'timeout': timeout
            })
            
            return {
                'host': host,
                'reachable': ping_result.get('success', False),
                'response_time': ping_result.get('elapsed', 0),
                'status_code': ping_result.get('status_code'),
                'method': 'http_head'
            }
            
        except Exception as error:
            return {
                'host': host,
                'reachable': False,
                'error': str(error),
                'method': 'http_head'
            }
