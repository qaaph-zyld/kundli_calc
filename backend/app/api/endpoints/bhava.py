"""
API endpoints for Bhava (House) analysis
"""
from typing import Dict, List, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator
from app.core.calculations.bhava_system import BhavaSystem

router = APIRouter()

class BhavaAnalysisRequest(BaseModel):
    """Request model for Bhava analysis"""
    planet_positions: Dict[str, float] = Field(
        ..., 
        description="Dictionary of planet positions in degrees (0-360)"
    )
    aspects: Dict[str, List[int]] = Field(
        ..., 
        description="Dictionary of planet aspects to houses"
    )
    
    @validator('planet_positions')
    def validate_positions(cls, v):
        valid_planets = {
            'Sun', 'Moon', 'Mars', 'Mercury', 
            'Jupiter', 'Venus', 'Saturn'
        }
        for planet, position in v.items():
            if planet not in valid_planets:
                raise ValueError(f"Invalid planet: {planet}")
            if not 0 <= position < 360:
                raise ValueError(f"Invalid position for {planet}: {position}")
        return v
    
    @validator('aspects')
    def validate_aspects(cls, v):
        valid_planets = {
            'Sun', 'Moon', 'Mars', 'Mercury', 
            'Jupiter', 'Venus', 'Saturn'
        }
        for planet, houses in v.items():
            if planet not in valid_planets:
                raise ValueError(f"Invalid planet: {planet}")
            if not all(1 <= h <= 12 for h in houses):
                raise ValueError(f"Invalid house numbers for {planet}")
        return v

@router.post("/analyze", response_model=Dict[str, Any], tags=["Bhava"])
async def analyze_bhava_chart(request: BhavaAnalysisRequest) -> Dict[str, Any]:
    """
    Analyze full Bhava chart including house strengths and relationships
    
    Args:
        request: BhavaAnalysisRequest containing planet positions and aspects
        
    Returns:
        Dictionary containing comprehensive Bhava analysis
        
    Raises:
        HTTPException: If analysis fails
    """
    try:
        result = BhavaSystem.analyze_bhava_chart(
            request.planet_positions,
            request.aspects
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/house/{house_number}", response_model=Dict[str, Any], tags=["Bhava"])
async def analyze_house(
    house_number: int,
    request: BhavaAnalysisRequest
) -> Dict[str, Any]:
    """
    Analyze specific house in detail
    
    Args:
        house_number: House number to analyze (1-12)
        request: BhavaAnalysisRequest containing planet positions and aspects
        
    Returns:
        Dictionary containing detailed analysis of specified house
        
    Raises:
        HTTPException: If house number is invalid or analysis fails
    """
    try:
        if not 1 <= house_number <= 12:
            raise ValueError(f"Invalid house number: {house_number}")
            
        result = BhavaSystem.calculate_house_strength(
            house_number,
            request.planet_positions,
            request.aspects
        )
        
        # Add house relationships
        result['relationships'] = BhavaSystem.get_house_relationships(house_number)
        
        return {
            'house_number': house_number,
            'analysis': result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
