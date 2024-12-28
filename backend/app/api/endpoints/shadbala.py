"""
API endpoints for Shadbala calculations
"""
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator

from app.core.calculations.shadbala import ShadbalaSystem

router = APIRouter()

class AspectData(BaseModel):
    """Model for aspect data"""
    type: str = Field(..., description="Type of aspect")
    angle: float = Field(..., description="Aspect angle in degrees")
    
    @validator('type')
    def validate_type(cls, v):
        valid_types = {'conjunction', 'sextile', 'square', 'trine', 'opposition'}
        if v not in valid_types:
            raise ValueError(f"Invalid aspect type. Must be one of: {valid_types}")
        return v
    
    @validator('angle')
    def validate_angle(cls, v):
        if not 0 <= v < 360:
            raise ValueError("Angle must be between 0 and 360 degrees")
        return v

class ShadbalaRequest(BaseModel):
    """Request model for Shadbala calculation"""
    planet: str = Field(..., description="Planet name")
    position: float = Field(..., description="Planet position in degrees")
    house: int = Field(..., description="House number (1-12)")
    is_day: bool = Field(..., description="Whether birth is during day")
    aspects: List[AspectData] = Field(
        ..., 
        description="List of aspects to the planet"
    )
    planet_positions: Dict[str, float] = Field(
        ..., 
        description="Positions of all planets"
    )
    
    @validator('planet')
    def validate_planet(cls, v):
        valid_planets = {
            'sun', 'moon', 'mars', 'mercury',
            'jupiter', 'venus', 'saturn'
        }
        if v.lower() not in valid_planets:
            raise ValueError(f"Invalid planet: {v}")
        return v.lower()
    
    @validator('position')
    def validate_position(cls, v):
        if not 0 <= v < 360:
            raise ValueError("Position must be between 0 and 360 degrees")
        return v
    
    @validator('house')
    def validate_house(cls, v):
        if not 1 <= v <= 12:
            raise ValueError("House must be between 1 and 12")
        return v
    
    @validator('planet_positions')
    def validate_planet_positions(cls, v):
        valid_planets = {
            'sun', 'moon', 'mars', 'mercury',
            'jupiter', 'venus', 'saturn'
        }
        for planet, position in v.items():
            if planet.lower() not in valid_planets:
                raise ValueError(f"Invalid planet: {planet}")
            if not 0 <= position < 360:
                raise ValueError(f"Invalid position for {planet}: {position}")
        return {k.lower(): v for k, v in v.items()}

class ShadbalaAnalysisRequest(BaseModel):
    """Request model for complete Shadbala analysis"""
    birth_time_is_day: bool = Field(
        ..., 
        description="Whether birth time is during day"
    )
    planet_positions: Dict[str, float] = Field(
        ..., 
        description="Positions of all planets"
    )
    aspects: Dict[str, List[AspectData]] = Field(
        ..., 
        description="Aspects for each planet"
    )
    house_positions: Dict[str, int] = Field(
        ..., 
        description="House positions of planets"
    )

@router.post("/calculate", tags=["Shadbala"])
async def calculate_shadbala(request: ShadbalaRequest):
    """
    Calculate Shadbala strength for a single planet
    
    Args:
        request: ShadbalaRequest containing planet data
        
    Returns:
        Dictionary containing Shadbala analysis
    """
    try:
        result = ShadbalaSystem.calculate_shadbala(
            request.planet,
            request.position,
            request.house,
            request.is_day,
            [aspect.dict() for aspect in request.aspects],
            request.planet_positions
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/analyze", tags=["Shadbala"])
async def analyze_all_planets(request: ShadbalaAnalysisRequest):
    """
    Calculate Shadbala strength for all planets
    
    Args:
        request: ShadbalaAnalysisRequest containing birth data
        
    Returns:
        Dictionary containing Shadbala analysis for all planets
    """
    try:
        results = {}
        for planet, position in request.planet_positions.items():
            aspects = request.aspects.get(planet, [])
            house = request.house_positions.get(planet)
            
            if house is None:
                raise ValueError(f"Missing house position for {planet}")
                
            result = ShadbalaSystem.calculate_shadbala(
                planet,
                position,
                house,
                request.birth_time_is_day,
                [aspect.dict() for aspect in aspects],
                request.planet_positions
            )
            results[planet] = result
            
        # Calculate overall chart strength
        total_strength = sum(r['total_strength'] for r in results.values())
        average_strength = total_strength / len(results)
        
        return {
            'planets': results,
            'chart_analysis': {
                'total_strength': float(total_strength),
                'average_strength': float(average_strength),
                'interpretation': ShadbalaSystem._interpret_strength(average_strength)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
