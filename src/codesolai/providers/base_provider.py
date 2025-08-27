"""
Base provider class for LLM providers
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import httpx
from ..utils import Utils


class BaseProvider(ABC):
    """Base class for all LLM providers"""

    def __init__(self, timeout: float = 30.0, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries

    @abstractmethod
    async def call(self, api_key: str, prompt: str, options: Optional[Dict[str, Any]] = None) -> str:
        """Make API call to the provider"""
        pass

    async def make_request(self, url: str, headers: Dict[str, str], data: Dict[str, Any], retry_count: int = 0) -> Dict[str, Any]:
        """Make HTTP request with retry logic"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                return response.json()
            
            except (httpx.RequestError, httpx.HTTPStatusError) as error:
                # Determine if we should retry
                should_retry = retry_count < self.max_retries and self._should_retry_error(error)

                if should_retry:
                    delay = (2 ** retry_count) * 1.0  # Exponential backoff in seconds
                    Utils.log_warning(f"Request failed, retrying in {delay}s... ({retry_count + 1}/{self.max_retries})")
                    
                    await asyncio.sleep(delay)
                    return await self.make_request(url, headers, data, retry_count + 1)

                raise error

    def _should_retry_error(self, error: Exception) -> bool:
        """Determine if an error should trigger a retry"""
        # Retry on network errors
        if isinstance(error, httpx.RequestError):
            return True
        
        # Retry on 5xx server errors
        if isinstance(error, httpx.HTTPStatusError):
            return error.response.status_code >= 500
        
        return False

    @abstractmethod
    def handle_provider_error(self, error: Exception, provider: str) -> Exception:
        """Handle and format provider-specific errors"""
        pass
