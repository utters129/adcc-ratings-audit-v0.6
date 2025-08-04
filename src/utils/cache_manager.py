"""
Cache Manager for ADCC Analysis Engine

This module provides performance optimization through caching
frequently accessed data and expensive computations.
"""

import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from pathlib import Path
import structlog

from src.config.settings import get_settings
from src.utils.file_handler import save_json_file, load_json_file, ensure_directory_exists

logger = structlog.get_logger(__name__)
settings = get_settings()


class CacheEntry:
    """Represents a cache entry with metadata."""
    
    def __init__(
        self,
        key: str,
        value: Any,
        ttl: int = 3600,
        created_at: Optional[datetime] = None
    ):
        """
        Initialize a cache entry.
        
        Args:
            key: Cache key
            value: Cached value
            ttl: Time to live in seconds
            created_at: Creation timestamp
        """
        self.key = key
        self.value = value
        self.ttl = ttl
        self.created_at = created_at or datetime.now()
        self.access_count = 0
        self.last_accessed = self.created_at
    
    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        return datetime.now() > self.created_at + timedelta(seconds=self.ttl)
    
    def access(self):
        """Record an access to this cache entry."""
        self.access_count += 1
        self.last_accessed = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert cache entry to dictionary."""
        return {
            "key": self.key,
            "value": self.value,
            "ttl": self.ttl,
            "created_at": self.created_at.isoformat(),
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheEntry':
        """Create cache entry from dictionary."""
        entry = cls(
            key=data["key"],
            value=data["value"],
            ttl=data["ttl"],
            created_at=datetime.fromisoformat(data["created_at"])
        )
        entry.access_count = data["access_count"]
        entry.last_accessed = datetime.fromisoformat(data["last_accessed"])
        return entry


class CacheManager:
    """
    Performance optimization cache manager.
    
    Provides caching functionality for frequently accessed data
    and expensive computations to improve system performance.
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: int = 3600,
        enable_persistence: bool = True
    ):
        """
        Initialize the cache manager.
        
        Args:
            max_size: Maximum number of cache entries
            default_ttl: Default time to live in seconds
            enable_persistence: Whether to persist cache to disk
        """
        self.settings = get_settings()
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.enable_persistence = enable_persistence
        
        # Cache storage
        self.cache: Dict[str, CacheEntry] = {}
        
        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        
        # Storage
        if enable_persistence:
            self.cache_file = Path(settings.datastore_dir) / "cache_data.json"
            ensure_directory_exists(self.cache_file.parent)
            self._load_cache()
        
        logger.info("Cache manager initialized",
                   max_size=max_size,
                   default_ttl=default_ttl,
                   persistence=enable_persistence)
    
    def _load_cache(self):
        """Load cache from persistent storage."""
        try:
            if self.cache_file.exists():
                cache_data = load_json_file(self.cache_file)
                
                for entry_data in cache_data:
                    entry = CacheEntry.from_dict(entry_data)
                    
                    # Only load non-expired entries
                    if not entry.is_expired():
                        self.cache[entry.key] = entry
                
                logger.info("Loaded cache from storage", count=len(self.cache))
            else:
                logger.info("No existing cache file found")
        except Exception as e:
            logger.error("Failed to load cache", error=str(e))
    
    def _save_cache(self):
        """Save cache to persistent storage."""
        if not self.enable_persistence:
            return
        
        try:
            # Convert cache entries to dictionaries
            cache_data = [entry.to_dict() for entry in self.cache.values()]
            save_json_file(cache_data, self.cache_file)
            logger.debug("Saved cache to storage", count=len(cache_data))
        except Exception as e:
            logger.error("Failed to save cache", error=str(e))
    
    def _generate_key(self, *args, **kwargs) -> str:
        """
        Generate a cache key from arguments.
        
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Cache key string
        """
        # Create a string representation of the arguments
        key_data = {
            "args": args,
            "kwargs": sorted(kwargs.items())
        }
        
        # Generate hash
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from cache.
        
        Args:
            key: Cache key
            default: Default value if key not found
            
        Returns:
            Cached value or default
        """
        # Clean expired entries first
        self._cleanup_expired()
        
        if key in self.cache:
            entry = self.cache[key]
            entry.access()
            self.hits += 1
            
            logger.debug("Cache hit", key=key)
            return entry.value
        else:
            self.misses += 1
            logger.debug("Cache miss", key=key)
            return default
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ):
        """
        Set a value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (uses default if not specified)
        """
        if ttl is None:
            ttl = self.default_ttl
        
        # Check if we need to evict entries
        if len(self.cache) >= self.max_size:
            self._evict_entries()
        
        # Create cache entry
        entry = CacheEntry(key=key, value=value, ttl=ttl)
        self.cache[key] = entry
        
        # Save to persistent storage
        self._save_cache()
        
        logger.debug("Cached value", key=key, ttl=ttl)
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if key was found and deleted, False otherwise
        """
        if key in self.cache:
            del self.cache[key]
            self._save_cache()
            logger.debug("Deleted cache entry", key=key)
            return True
        return False
    
    def clear(self):
        """Clear all cache entries."""
        self.cache.clear()
        self._save_cache()
        logger.info("Cleared all cache entries")
    
    def exists(self, key: str) -> bool:
        """
        Check if a key exists in cache.
        
        Args:
            key: Cache key to check
            
        Returns:
            True if key exists and is not expired, False otherwise
        """
        self._cleanup_expired()
        return key in self.cache
    
    def get_or_set(
        self,
        key: str,
        default_func: Callable[[], Any],
        ttl: Optional[int] = None
    ) -> Any:
        """
        Get a value from cache or set it using a default function.
        
        Args:
            key: Cache key
            default_func: Function to call if key not found
            ttl: Time to live in seconds
            
        Returns:
            Cached value or result of default function
        """
        value = self.get(key)
        if value is None:
            value = default_func()
            self.set(key, value, ttl)
        return value
    
    def cache_function(
        self,
        ttl: Optional[int] = None,
        key_prefix: str = ""
    ) -> Callable:
        """
        Decorator to cache function results.
        
        Args:
            ttl: Time to live in seconds
            key_prefix: Prefix for cache keys
            
        Returns:
            Decorated function
        """
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self._generate_key(*args, **kwargs)
                if key_prefix:
                    cache_key = f"{key_prefix}:{cache_key}"
                
                # Try to get from cache
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Call function and cache result
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl)
                
                return result
            
            return wrapper
        return decorator
    
    def _cleanup_expired(self):
        """Remove expired cache entries."""
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.debug("Cleaned up expired entries", count=len(expired_keys))
    
    def _evict_entries(self, count: int = 1):
        """
        Evict cache entries using LRU (Least Recently Used) policy.
        
        Args:
            count: Number of entries to evict
        """
        # Sort entries by last accessed time
        sorted_entries = sorted(
            self.cache.items(),
            key=lambda x: x[1].last_accessed
        )
        
        # Remove oldest entries
        for i in range(min(count, len(sorted_entries))):
            key, entry = sorted_entries[i]
            del self.cache[key]
        
        self.evictions += count
        logger.debug("Evicted cache entries", count=count)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0
        
        return {
            "total_entries": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "hit_rate": hit_rate,
            "total_requests": total_requests
        }
    
    def get_cache_info(self) -> List[Dict[str, Any]]:
        """
        Get detailed information about cache entries.
        
        Returns:
            List of cache entry information
        """
        info = []
        for key, entry in self.cache.items():
            info.append({
                "key": key,
                "created_at": entry.created_at.isoformat(),
                "last_accessed": entry.last_accessed.isoformat(),
                "access_count": entry.access_count,
                "ttl": entry.ttl,
                "is_expired": entry.is_expired(),
                "value_type": type(entry.value).__name__
            })
        
        return info
    
    def warm_cache(self, warmup_data: Dict[str, Any]):
        """
        Warm up the cache with predefined data.
        
        Args:
            warmup_data: Dictionary of key-value pairs to cache
        """
        for key, value in warmup_data.items():
            self.set(key, value)
        
        logger.info("Warmed up cache", count=len(warmup_data))
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """
        Estimate memory usage of cache.
        
        Returns:
            Dictionary with memory usage information
        """
        total_size = 0
        entry_sizes = {}
        
        for key, entry in self.cache.items():
            # Estimate size of entry
            key_size = len(key.encode('utf-8'))
            value_size = len(json.dumps(entry.value, default=str).encode('utf-8'))
            entry_size = key_size + value_size + 100  # Approximate overhead
            
            total_size += entry_size
            entry_sizes[key] = entry_size
        
        return {
            "total_bytes": total_size,
            "total_mb": total_size / (1024 * 1024),
            "entry_sizes": entry_sizes,
            "average_entry_size": total_size / len(self.cache) if self.cache else 0
        }
    
    def optimize(self, target_size: Optional[int] = None):
        """
        Optimize cache by removing least used entries.
        
        Args:
            target_size: Target cache size (uses max_size if not specified)
        """
        if target_size is None:
            target_size = self.max_size
        
        if len(self.cache) <= target_size:
            return
        
        # Sort entries by access count and last accessed time
        sorted_entries = sorted(
            self.cache.items(),
            key=lambda x: (x[1].access_count, x[1].last_accessed)
        )
        
        # Remove least used entries
        entries_to_remove = len(self.cache) - target_size
        for i in range(entries_to_remove):
            key, entry = sorted_entries[i]
            del self.cache[key]
        
        self._save_cache()
        logger.info("Optimized cache", removed_count=entries_to_remove)
    
    def cleanup(self):
        """Clean up cache and save to storage."""
        self._cleanup_expired()
        self._save_cache()
        logger.info("Cache cleanup completed") 