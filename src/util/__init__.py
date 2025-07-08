"""Utility module - clean public API."""

from .custom_cache import Cache, CacheInvalidationHandler, ScopedCacheView, WatchedCache

__all__ = [
    "CacheInvalidationHandler",
    "ScopedCacheView",
    "WatchedCache",
    "Cache",
]