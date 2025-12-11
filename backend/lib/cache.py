"""
Cache System - Laravel-style caching with TTL support
Provides in-memory caching with time-to-live (TTL) functionality
"""

import time
import logging
from typing import Any, Optional, Callable, Dict, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CacheItem:
    """Represents a single cached item with expiration"""
    
    def __init__(self, value: Any, expires_at: Optional[float] = None):
        """
        Initialize cache item
        
        Args:
            value: The value to cache
            expires_at: Unix timestamp when item expires (None = never)
        """
        self.value = value
        self.expires_at = expires_at
        self.created_at = time.time()
    
    def is_expired(self) -> bool:
        """Check if cache item has expired"""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at
    
    def ttl(self) -> Optional[float]:
        """Get remaining time-to-live in seconds"""
        if self.expires_at is None:
            return None
        remaining = self.expires_at - time.time()
        return max(0, remaining)


class Cache:
    """
    Laravel-style cache system with TTL support
    Provides methods similar to Laravel's cache facade
    """
    
    def __init__(self, default_ttl: Optional[int] = None):
        """
        Initialize cache
        
        Args:
            default_ttl: Default TTL in seconds (None = forever)
        """
        self._store: Dict[str, CacheItem] = {}
        self.default_ttl = default_ttl
        self._hits = 0
        self._misses = 0
    
    def put(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """
        Store an item in the cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None = use default)
        """
        if ttl is None:
            ttl = self.default_ttl
        
        expires_at = None
        if ttl is not None:
            expires_at = time.time() + ttl
        
        self._store[key] = CacheItem(value, expires_at)
        logger.debug(f"[Cache] Stored key '{key}' with TTL: {ttl}")
    
    def get(
        self,
        key: str,
        default: Any = None
    ) -> Any:
        """
        Retrieve an item from the cache
        
        Args:
            key: Cache key
            default: Default value if key not found or expired
            
        Returns:
            Cached value or default
        """
        if key not in self._store:
            self._misses += 1
            logger.debug(f"[Cache] Miss for key '{key}'")
            return default
        
        item = self._store[key]
        
        if item.is_expired():
            self._misses += 1
            logger.debug(f"[Cache] Expired key '{key}'")
            del self._store[key]
            return default
        
        self._hits += 1
        logger.debug(f"[Cache] Hit for key '{key}'")
        return item.value
    
    def has(self, key: str) -> bool:
        """
        Check if an item exists and is not expired
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists and is valid
        """
        if key not in self._store:
            return False
        
        item = self._store[key]
        if item.is_expired():
            del self._store[key]
            return False
        
        return True
    
    def forget(self, key: str) -> bool:
        """
        Remove an item from the cache
        
        Args:
            key: Cache key
            
        Returns:
            True if key was removed, False if not found
        """
        if key in self._store:
            del self._store[key]
            logger.debug(f"[Cache] Forgot key '{key}'")
            return True
        return False
    
    def flush(self) -> None:
        """Clear all items from the cache"""
        count = len(self._store)
        self._store.clear()
        self._hits = 0
        self._misses = 0
        logger.info(f"[Cache] Flushed {count} items")
    
    def remember(
        self,
        key: str,
        ttl: Optional[int],
        callback: Callable[[], Any]
    ) -> Any:
        """
        Get an item from cache, or store the result of callback if not found
        Similar to Laravel's Cache::remember()
        
        Args:
            key: Cache key
            ttl: Time-to-live in seconds
            callback: Function to call if key not found
            
        Returns:
            Cached value or callback result
        """
        if self.has(key):
            return self.get(key)
        
        value = callback()
        self.put(key, value, ttl)
        return value
    
    def remember_forever(
        self,
        key: str,
        callback: Callable[[], Any]
    ) -> Any:
        """
        Get an item from cache, or store forever if not found
        Similar to Laravel's Cache::rememberForever()
        
        Args:
            key: Cache key
            callback: Function to call if key not found
            
        Returns:
            Cached value or callback result
        """
        return self.remember(key, None, callback)
    
    def pull(self, key: str, default: Any = None) -> Any:
        """
        Retrieve and delete an item from cache
        
        Args:
            key: Cache key
            default: Default value if not found
            
        Returns:
            Cached value or default
        """
        value = self.get(key, default)
        self.forget(key)
        return value
    
    def add(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Store an item only if it doesn't exist
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
            
        Returns:
            True if added, False if key already exists
        """
        if self.has(key):
            return False
        
        self.put(key, value, ttl)
        return True
    
    def increment(
        self,
        key: str,
        amount: int = 1
    ) -> int:
        """
        Increment a numeric cache value
        
        Args:
            key: Cache key
            amount: Amount to increment
            
        Returns:
            New value
        """
        current = self.get(key, 0)
        if not isinstance(current, (int, float)):
            current = 0
        
        new_value = current + amount
        self.put(key, new_value)
        return new_value
    
    def decrement(
        self,
        key: str,
        amount: int = 1
    ) -> int:
        """
        Decrement a numeric cache value
        
        Args:
            key: Cache key
            amount: Amount to decrement
            
        Returns:
            New value
        """
        return self.increment(key, -amount)
    
    def get_ttl(self, key: str) -> Optional[float]:
        """
        Get remaining TTL for a key
        
        Args:
            key: Cache key
            
        Returns:
            Remaining seconds or None if not found/no expiry
        """
        if key not in self._store:
            return None
        
        item = self._store[key]
        return item.ttl()
    
    def clean_expired(self) -> int:
        """
        Remove all expired items from cache
        
        Returns:
            Number of items removed
        """
        expired_keys = [
            key for key, item in self._store.items()
            if item.is_expired()
        ]
        
        for key in expired_keys:
            del self._store[key]
        
        if expired_keys:
            logger.info(f"[Cache] Cleaned {len(expired_keys)} expired items")
        
        return len(expired_keys)
    
    def stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """
        total_requests = self._hits + self._misses
        hit_rate = (
            (self._hits / total_requests * 100)
            if total_requests > 0
            else 0
        )
        
        return {
            'size': len(self._store),
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': round(hit_rate, 2),
            'total_requests': total_requests
        }
    
    def keys(self) -> list:
        """Get all cache keys"""
        return list(self._store.keys())
    
    def size(self) -> int:
        """Get number of items in cache"""
        return len(self._store)


class CacheManager:
    """
    Cache Manager - Manages multiple named cache instances
    Similar to Laravel's cache manager
    """
    
    _instances: Dict[str, Cache] = {}
    _default_store = 'default'
    
    @classmethod
    def store(cls, name: str = None) -> Cache:
        """
        Get a cache store instance
        
        Args:
            name: Store name (uses default if None)
            
        Returns:
            Cache instance
        """
        if name is None:
            name = cls._default_store
        
        if name not in cls._instances:
            cls._instances[name] = Cache()
            logger.info(f"[CacheManager] Created cache store '{name}'")
        
        return cls._instances[name]
    
    @classmethod
    def flush_all(cls) -> None:
        """Flush all cache stores"""
        for store in cls._instances.values():
            store.flush()
        logger.info("[CacheManager] Flushed all stores")
    
    @classmethod
    def stats_all(cls) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all stores"""
        return {
            name: store.stats()
            for name, store in cls._instances.items()
        }


# Convenience function for default cache
def cache(store_name: str = None) -> Cache:
    """
    Get a cache instance
    
    Args:
        store_name: Optional store name
        
    Returns:
        Cache instance
    """
    return CacheManager.store(store_name)
