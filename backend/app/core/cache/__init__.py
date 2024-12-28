"""Cache module initialization"""
from typing import Optional
import redis
from .calculation_cache import CalculationCache

class RedisCache:
    """Redis cache implementation"""
    _instance: Optional['RedisCache'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            try:
                self.redis = redis.Redis(
                    host='localhost',
                    port=6379,
                    db=0,
                    decode_responses=True
                )
                self.initialized = True
            except redis.ConnectionError:
                self.redis = None
                self.initialized = False
    
    def get(self, key: str) -> Optional[str]:
        """Get value from Redis"""
        if self.redis:
            try:
                return self.redis.get(key)
            except redis.RedisError:
                return None
        return None
    
    def set(self, key: str, value: str, expire: int = 3600) -> bool:
        """Set value in Redis with expiration"""
        if self.redis:
            try:
                return self.redis.set(key, value, ex=expire)
            except redis.RedisError:
                return False
        return False
    
    def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        if self.redis:
            try:
                return bool(self.redis.delete(key))
            except redis.RedisError:
                return False
        return False

# Global cache instances
calculation_cache = CalculationCache()
redis_cache = RedisCache()
