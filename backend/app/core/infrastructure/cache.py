from typing import Any, Optional, Union
import aioredis
import json
from datetime import datetime, timedelta

class CacheManager:
    def __init__(self):
        self.redis = None
        self.default_ttl = 3600  # 1 hour
        
    async def initialize(self, redis_url: str):
        """Initialize Redis connection"""
        self.redis = await aioredis.create_redis_pool(redis_url)
        
    async def get(self, key: str, default: Any = None) -> Optional[Any]:
        """Get value from cache"""
        value = await self.redis.get(key)
        if value is None:
            return default
        return json.loads(value)
        
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        ttl = ttl or self.default_ttl
        await self.redis.set(
            key,
            json.dumps(value),
            expire=ttl
        )
        
    async def invalidate(self, key: str):
        """Invalidate cache entry"""
        await self.redis.delete(key)
        
    async def invalidate_pattern(self, pattern: str):
        """Invalidate cache entries matching pattern"""
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
            
    async def get_or_set(self, key: str, getter_func, ttl: Optional[int] = None) -> Any:
        """Get from cache or set if missing"""
        value = await self.get(key)
        if value is None:
            value = await getter_func()
            await self.set(key, value, ttl)
        return value
