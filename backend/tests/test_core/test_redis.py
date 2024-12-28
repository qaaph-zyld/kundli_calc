"""Test Redis module."""
import pytest
from unittest.mock import Mock, patch
from app.core.config.redis import RedisClient


@pytest.fixture(autouse=True)
def reset_redis_client():
    """Reset Redis client before each test."""
    RedisClient.reset()
    yield


@pytest.fixture
def redis_client():
    """Create Redis client instance."""
    with patch('redis.Redis') as mock_redis:
        # Mock successful connection
        mock_instance = mock_redis.return_value
        mock_instance.ping.return_value = True
        mock_instance.set.return_value = True
        mock_instance.get.return_value = "test_value"
        mock_instance.delete.return_value = 1
        mock_instance.exists.return_value = 1
        mock_instance.scan_iter.return_value = ["test:1", "test:2"]
        mock_instance.ttl.return_value = 3600
        
        # Create client and replace its Redis instance
        client = RedisClient()
        client._client = mock_instance
        client._initialized = True  # Important: set initialized flag
        yield client


def test_redis_connection(redis_client):
    """Test Redis connection."""
    assert redis_client.is_connected()


def test_redis_set_get(redis_client):
    """Test Redis set and get operations."""
    # Test set operation
    assert redis_client.set("test_key", "test_value", 3600)

    # Test get operation
    assert redis_client.get("test_key") == "test_value"


def test_redis_delete(redis_client):
    """Test Redis delete operation."""
    assert redis_client.delete("test_key")


def test_redis_exists(redis_client):
    """Test Redis exists operation."""
    # Test key exists
    assert redis_client.exists("test_key")

    # Test key does not exist
    redis_client._client.exists.return_value = 0
    assert not redis_client.exists("non_existent_key")


def test_redis_connection_error():
    """Test Redis connection error handling."""
    with patch('redis.Redis') as mock_redis:
        # Mock connection failure
        mock_redis.return_value.ping.side_effect = Exception("Connection failed")
        client = RedisClient()
        assert not client.is_connected()


def test_redis_operation_error(redis_client):
    """Test Redis operation error handling."""
    # Mock operation failure
    redis_client._client.set.side_effect = Exception("Operation failed")
    assert not redis_client.set("test_key", "test_value", 3600)


def test_redis_key_pattern(redis_client):
    """Test Redis key pattern operations."""
    keys = redis_client.get_keys("test:*")
    assert len(keys) == 2
    assert "test:1" in keys
    assert "test:2" in keys


def test_redis_ttl(redis_client):
    """Test Redis TTL operations."""
    # Test normal TTL
    assert redis_client.get_ttl("test_key") == 3600

    # Test key does not exist
    redis_client._client.ttl.return_value = -2
    assert redis_client.get_ttl("non_existent_key") == -2

    # Test key exists but has no TTL
    redis_client._client.ttl.return_value = -1
    assert redis_client.get_ttl("persistent_key") == -1
