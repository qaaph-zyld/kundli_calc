"""Health check endpoints."""
from typing import Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from redis.exceptions import RedisError

from app.api.deps import get_db
from app.core.cache import redis_cache

router = APIRouter()


@router.get("/")
async def health_check(db: Session = Depends(get_db)) -> Dict[str, Dict[str, str]]:
    """
    Check health status of services.
    
    Returns:
        dict: Health status of each service
            - status: "ok" or "error"
            - details: Additional information about the service status
    """
    health_status = {
        "database": {"status": "error", "details": ""},
        "redis": {"status": "error", "details": ""},
    }

    # Check database connection
    try:
        db.execute("SELECT 1")
        health_status["database"] = {
            "status": "ok",
            "details": "Connected to database"
        }
    except Exception as e:
        health_status["database"]["details"] = f"Database error: {str(e)}"

    # Check Redis connection
    try:
        redis_cache.redis.ping()
        health_status["redis"] = {
            "status": "ok",
            "details": "Connected to Redis"
        }
    except RedisError as e:
        health_status["redis"]["details"] = f"Redis error: {str(e)}"
    except Exception as e:
        health_status["redis"]["details"] = f"Unexpected error: {str(e)}"

    return health_status
