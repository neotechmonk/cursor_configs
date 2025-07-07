"""Utility module - clean public API."""

from .custom_cache import CacheInvalidationHandler, WatchedCache

__all__ = [
    "CacheInvalidationHandler",
    "WatchedCache",
]
