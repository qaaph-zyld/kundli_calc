"""Redis cache module."""
from functools import wraps
import json
import hashlib
from typing import Optional, Any, Callable
from redis import Redis
from app.core.config.settings import settings


class RedisCache:
    """Redis cache class."""

    def __init__(self):
        """Initialize Redis cache."""
        self.redis = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = self.redis.get(key)
            return json.loads(value) if value else None
        except (json.JSONDecodeError, Exception):
            return None
            
    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional expiration."""
        try:
            serialized = json.dumps(value)
            if expire:
                return bool(self.redis.setex(key, expire, serialized))
            return bool(self.redis.set(key, serialized))
        except Exception:
            return False
            
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            return bool(self.redis.delete(key))
        except Exception:
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            return bool(self.redis.exists(key))
        except Exception:
            return False

    async def clear_all(self) -> bool:
        """Clear all keys in cache."""
        try:
            self.redis.flushdb()
            return True
        except Exception:
            return False


# Create a global Redis cache instance
redis_cache = RedisCache()


def cache_response(prefix: str, expire: int = settings.REDIS_CACHE_EXPIRE_SECONDS):
    """Cache decorator for API responses."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function arguments
            key_parts = [prefix]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()

            # Try to get from cache
            cached_value = await redis_cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Get fresh value
            result = await func(*args, **kwargs)
            if result is not None:
                await redis_cache.set(cache_key, result, expire)
            return result

        return wrapper
    return decorator


async def invalidate_cache(prefix: str, *args):
    """Invalidate cache for given prefix and arguments."""
    key_parts = [prefix]
    key_parts.extend(str(arg) for arg in args)
    cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
    await redis_cache.delete(cache_key)
