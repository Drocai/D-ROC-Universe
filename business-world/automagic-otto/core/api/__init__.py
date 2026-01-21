"""
Async API module for AutoMagic
High-performance API clients with connection pooling and caching
"""

from .async_client import AsyncAPIClient, get_api_client

__all__ = ["AsyncAPIClient", "get_api_client"]