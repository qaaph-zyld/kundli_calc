"""
API endpoints for Ashtakavarga calculations
"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator
from app.core.calculations.ashtakavarga import Ashtakavarga

router = APIRouter()

class AshtakavargaRequest(BaseModel):
    """Request model for Ashtakavarga calculations"""
    planet_positions: Dict[str, int] = Field(
        ..., 
        description="Dictionary of planet positions in houses (1-12)"
    )
    
    @validator('planet_positions')
    def validate_positions(cls, v):
        valid_planets = {'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn'}
        for planet, position in v.items():
            if planet not in valid_planets:
                raise ValueError(f"Invalid planet: {planet}")
            if not 1 <= position <= 12:
                raise ValueError(f"Invalid house position for {planet}: {position}")
        return v

@router.post("/calculate", response_model=Dict[str, Any], tags=["Ashtakavarga"])
async def calculate_ashtakavarga(request: AshtakavargaRequest) -> Dict[str, Any]:
    """
    Calculate Sarvashtakavarga and analyze planetary strengths
    
    Args:
        request: AshtakavargaRequest containing planet positions
        
    Returns:
        Dictionary containing Sarvashtakavarga and analysis results
        
    Raises:
        HTTPException: If calculation fails
    """
    try:
        # Calculate Sarvashtakavarga
        sarvashtakavarga = Ashtakavarga.calculate_sarvashtakavarga(
            request.planet_positions
        )
        
        # Analyze each planet's strength
        planet_analysis = {}
        for planet in request.planet_positions.keys():
            analysis = Ashtakavarga.analyze_planet_strength(
                planet,
                sarvashtakavarga
            )
            planet_analysis[planet] = analysis
        
        # Get strong houses
        strong_houses = Ashtakavarga.get_strong_houses(sarvashtakavarga)
        
        return {
            'sarvashtakavarga': sarvashtakavarga,
            'planet_analysis': planet_analysis,
            'strong_houses': strong_houses
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/analyze_planet", response_model=Dict[str, Any], tags=["Ashtakavarga"])
async def analyze_planet(
    planet: str,
    request: AshtakavargaRequest
) -> Dict[str, Any]:
    """
    Analyze specific planet's strength using Ashtakavarga
    
    Args:
        planet: Name of the planet to analyze
        request: AshtakavargaRequest containing planet positions
        
    Returns:
        Dictionary containing analysis results for the specified planet
        
    Raises:
        HTTPException: If planet is invalid or calculation fails
    """
    try:
        # Calculate Sarvashtakavarga
        sarvashtakavarga = Ashtakavarga.calculate_sarvashtakavarga(
            request.planet_positions
        )
        
        # Analyze specified planet
        analysis = Ashtakavarga.analyze_planet_strength(
            planet,
            sarvashtakavarga
        )
        
        return {
            'planet': planet,
            'analysis': analysis,
            'bindus_per_house': sarvashtakavarga.get(planet, [])
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
