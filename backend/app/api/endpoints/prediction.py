"""
API endpoints for Prediction Engine
"""
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator

from app.core.calculations.prediction_engine import PredictionEngine

router = APIRouter()

class MuhurtaRequest(BaseModel):
    """Request model for Muhurta calculation"""
    datetime_utc: str = Field(..., description="UTC datetime string")
    activity_type: str = Field(..., description="Type of activity")
    planet_positions: Dict[str, float] = Field(
        ..., 
        description="Current planetary positions"
    )
    planet_strengths: Dict[str, float] = Field(
        ..., 
        description="Current planetary strengths"
    )
    
    @validator('datetime_utc')
    def validate_datetime(cls, v):
        try:
            return datetime.fromisoformat(v)
        except ValueError:
            raise ValueError("Invalid datetime format")
    
    @validator('activity_type')
    def validate_activity(cls, v):
        valid_activities = {
            'business', 'marriage', 'travel',
            'education', 'medical', 'spiritual'
        }
        if v not in valid_activities:
            raise ValueError(f"Invalid activity type. Must be one of: {valid_activities}")
        return v
    
    @validator('planet_positions')
    def validate_positions(cls, v):
        valid_planets = {
            'sun', 'moon', 'mars', 'mercury',
            'jupiter', 'venus', 'saturn'
        }
        for planet in v:
            if planet.lower() not in valid_planets:
                raise ValueError(f"Invalid planet: {planet}")
            if not 0 <= v[planet] < 360:
                raise ValueError(f"Invalid position for {planet}: {v[planet]}")
        return v

class NextSuitableTimeRequest(MuhurtaRequest):
    """Request model for finding next suitable time"""
    max_days: int = Field(
        7, 
        ge=1, 
        le=30, 
        description="Maximum days to look ahead"
    )

class TransitPeriodRequest(BaseModel):
    """Request model for transit period analysis"""
    start_time: str = Field(..., description="Period start time (UTC)")
    end_time: str = Field(..., description="Period end time (UTC)")
    planet: str = Field(..., description="Planet to analyze")
    natal_position: float = Field(
        ..., 
        ge=0, 
        lt=360, 
        description="Planet's natal position"
    )
    transit_positions: List[Dict[str, str]] = Field(
        ..., 
        description="List of transit positions with times"
    )
    
    @validator('start_time', 'end_time')
    def validate_datetime(cls, v):
        try:
            return datetime.fromisoformat(v)
        except ValueError:
            raise ValueError("Invalid datetime format")
    
    @validator('planet')
    def validate_planet(cls, v):
        valid_planets = {
            'sun', 'moon', 'mars', 'mercury',
            'jupiter', 'venus', 'saturn'
        }
        if v.lower() not in valid_planets:
            raise ValueError(f"Invalid planet: {v}")
        return v
    
    @validator('transit_positions')
    def validate_transit_positions(cls, v):
        try:
            return [(datetime.fromisoformat(pos['time']), float(pos['position']))
                    for pos in v]
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid transit position format: {e}")

@router.post("/muhurta/calculate", tags=["Prediction"])
async def calculate_muhurta(request: MuhurtaRequest):
    """Calculate Muhurta suitability for given time and activity"""
    try:
        result = PredictionEngine.calculate_muhurta(
            request.datetime_utc,
            request.activity_type,
            request.planet_positions,
            request.planet_strengths
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/muhurta/next-suitable", tags=["Prediction"])
async def find_next_suitable_time(request: NextSuitableTimeRequest):
    """Find next suitable time for given activity"""
    try:
        result = PredictionEngine.find_next_suitable_time(
            request.datetime_utc,
            request.activity_type,
            request.planet_positions,
            request.planet_strengths,
            request.max_days
        )
        
        if result is None:
            raise HTTPException(
                status_code=404,
                detail="No suitable time found within specified period"
            )
            
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/transit/analyze", tags=["Prediction"])
async def analyze_transit_period(request: TransitPeriodRequest):
    """Analyze transit period effects"""
    try:
        result = PredictionEngine.analyze_transit_period(
            request.start_time,
            request.end_time,
            request.planet,
            request.natal_position,
            request.transit_positions
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
