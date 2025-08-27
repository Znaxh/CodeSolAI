"""
CodeSolAI - A fully autonomous agentic CLI tool for interacting with large language models.

This package provides a command-line interface for interacting with various LLM providers
(Claude, Gemini, GPT) with autonomous agent capabilities for multi-step task execution.
"""

__version__ = "1.0.0"
__author__ = "znaxh"
__email__ = "anurag.ps.contact@gmail.com"

from .providers.provider_manager import ProviderManager
from .config import Config

__all__ = [
    "ProviderManager",
    "Config",
    "__version__",
]
