"""Redis client configuration."""
import redis
from typing import List, Optional
import logging
from .settings import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis client singleton."""

    _instance = None
    _initialized = False

    def __new__(cls):
        """Create singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize Redis client."""
        if not self._initialized:
            try:
                self._client = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    password=settings.REDIS_PASSWORD,
                    username=settings.REDIS_USERNAME,
                    ssl=settings.REDIS_SSL,
                    socket_timeout=settings.REDIS_TIMEOUT,
                    decode_responses=True
                )
                self._initialized = True
            except Exception as e:
                logger.error(f"Failed to initialize Redis client: {str(e)}")
                self._client = None
                self._initialized = False

    def is_connected(self) -> bool:
        """Check if Redis is connected.
        
        Returns:
            True if connected, False otherwise
        """
        if not self._initialized or not self._client:
            return False
            
        try:
            self._client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis connection check failed: {str(e)}")
            return False

    def get(self, key: str) -> Optional[str]:
        """Get value from Redis.
        
        Args:
            key: Key to retrieve
            
        Returns:
            Value if found, None otherwise
        """
        if not self.is_connected():
            return None
            
        try:
            return self._client.get(key)
        except Exception as e:
            logger.error(f"Redis get failed for key '{key}': {str(e)}")
            return None

    def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """Set value in Redis.
        
        Args:
            key: Key to set
            value: Value to store
            expire: Optional expiration in seconds
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            return False
            
        try:
            return bool(self._client.set(key, value, ex=expire))
        except Exception as e:
            logger.error(f"Redis set failed for key '{key}': {str(e)}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from Redis.
        
        Args:
            key: Key to delete
            
        Returns:
            True if deleted, False otherwise
        """
        if not self.is_connected():
            return False
            
        try:
            return bool(self._client.delete(key))
        except Exception as e:
            logger.error(f"Redis delete failed for key '{key}': {str(e)}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in Redis.
        
        Args:
            key: Key to check
            
        Returns:
            True if exists, False otherwise
        """
        if not self.is_connected():
            return False
            
        try:
            return bool(self._client.exists(key))
        except Exception as e:
            logger.error(f"Redis exists check failed for key '{key}': {str(e)}")
            return False

    def get_keys(self, pattern: str) -> List[str]:
        """Get keys matching pattern.
        
        Args:
            pattern: Pattern to match (e.g. "prefix:*")
            
        Returns:
            List of matching keys
        """
        if not self.is_connected():
            return []
            
        try:
            keys = self._client.scan_iter(match=pattern)
            return [key if isinstance(key, str) else key.decode() for key in keys]
        except Exception as e:
            logger.error(f"Redis keys lookup failed for pattern '{pattern}': {str(e)}")
            return []

    def get_ttl(self, key: str) -> int:
        """Get TTL for a key.
        
        Args:
            key: Key to check TTL for
            
        Returns:
            TTL in seconds, -2 if key doesn't exist, -1 if key exists but has no TTL
        """
        if not self.is_connected():
            return -2
            
        try:
            return self._client.ttl(key)
        except Exception as e:
            logger.error(f"Redis TTL check failed for key '{key}': {str(e)}")
            return -2

    def clear_all(self) -> bool:
        """Clear all keys in Redis.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            return False
            
        try:
            self._client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Redis flush failed: {str(e)}")
            return False

    @classmethod
    def reset(cls):
        """Reset the singleton instance. Useful for testing."""
        cls._instance = None
        cls._initialized = False


redis_client = RedisClient()
