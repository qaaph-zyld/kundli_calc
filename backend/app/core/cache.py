from typing import Optional, Any
import json
from redis import Redis
from datetime import timedelta

from .config import settings

class RedisCache:
    def __init__(self):
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
        except Exception:
            return None
            
    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[timedelta] = None
    ) -> bool:
        """Set value in cache with optional expiration."""
        try:
            serialized = json.dumps(value)
            if expire:
                return self.redis.setex(
                    key,
                    expire.total_seconds(),
                    serialized
                )
            return self.redis.set(key, serialized)
        except Exception:
            return False
            
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            return bool(self.redis.delete(key))
        except Exception:
            return False
            
    def generate_key(self, *args) -> str:
        """Generate cache key from arguments."""
        return ":".join(str(arg) for arg in args)
