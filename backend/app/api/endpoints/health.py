from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import swisseph as swe

from ...core.database import get_db

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/health/db")
async def database_health_check(db: Session = Depends(get_db)):
    """Check database connectivity."""
    try:
        # Execute a simple query
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "component": "database",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "component": "database",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/health/ephemeris")
async def ephemeris_health_check():
    """Check Swiss Ephemeris functionality."""
    try:
        # Try a simple calculation
        julian_day = swe.julday(2024, 1, 1, 12.0)
        sun_pos = swe.calc_ut(julian_day, swe.SUN)[0]
        return {
            "status": "healthy",
            "component": "ephemeris",
            "test_calculation": {
                "sun_longitude": sun_pos[0]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "component": "ephemeris",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
