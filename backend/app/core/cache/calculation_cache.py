"""Cache implementation for astronomical calculations."""
import hashlib
import json
from datetime import datetime
from typing import Any, Dict, Optional
from threading import RLock


class CalculationCache:
    """Thread-safe cache for astronomical calculations."""

    def __init__(self, max_size: int = 1000):
        """Initialize cache with size limit.
        
        Args:
            max_size: Maximum number of items to store in cache
        """
        self._cache: Dict[str, Any] = {}
        self._max_size = max_size
        self._lock = RLock()

    def generate_key(self, *args: Any) -> str:
        """Generate a unique cache key from arguments.
        
        Args:
            *args: Variable arguments to use for key generation
            
        Returns:
            Unique hash string for the arguments
        """
        # Convert datetime objects to ISO format strings
        processed_args = []
        for arg in args:
            if isinstance(arg, datetime):
                processed_args.append(arg.isoformat())
            else:
                processed_args.append(str(arg))

        # Create a string representation and hash it
        key_str = json.dumps(processed_args, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache.
        
        Args:
            key: Cache key to retrieve
            
        Returns:
            Cached value if found, None otherwise
        """
        with self._lock:
            return self._cache.get(key)

    def set(self, key: str, value: Any) -> None:
        """Set a value in the cache.
        
        Args:
            key: Cache key to set
            value: Value to cache
        """
        with self._lock:
            # Evict oldest entry if cache is full
            if len(self._cache) >= self._max_size:
                # Remove first item (oldest)
                self._cache.pop(next(iter(self._cache)))
            
            self._cache[key] = value

    def clear(self) -> None:
        """Clear all entries from the cache."""
        with self._lock:
            self._cache.clear()

    def size(self) -> int:
        """Get current size of cache.
        
        Returns:
            Number of items in cache
        """
        with self._lock:
            return len(self._cache)

    def contains(self, key: str) -> bool:
        """Check if key exists in cache.
        
        Args:
            key: Cache key to check
            
        Returns:
            True if key exists, False otherwise
        """
        with self._lock:
            return key in self._cache
