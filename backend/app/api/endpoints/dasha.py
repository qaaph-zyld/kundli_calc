"""
API endpoints for Dasha calculations
"""
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.core.calculations.dasha_system import VimshottariDasha
from app.core.interpretations.dasha_effects import DashaEffects
from app.core.calculations.dasha_yoga import DashaYoga

router = APIRouter()
dasha_calculator = VimshottariDasha()

class DashaRequest(BaseModel):
    """Request model for Dasha calculations"""
    birth_date: datetime = Field(..., description="Birth date and time in ISO format")
    moon_longitude: float = Field(..., description="Moon's longitude at birth (0-360 degrees)")

class DashaInterpretationRequest(BaseModel):
    """Request model for Dasha interpretation"""
    main_planet: str = Field(..., description="Main dasha lord (mahadasha)")
    sub_planet: Optional[str] = Field(None, description="Sub-period lord (antardasha)")
    prat_planet: Optional[str] = Field(None, description="Sub-sub period lord (pratyantardasha)")

class YogaCalculationRequest(BaseModel):
    """Request model for Yoga calculations"""
    main_planet: str = Field(..., description="Main dasha lord (mahadasha)")
    sub_planet: str = Field(..., description="Sub-period lord (antardasha)")
    prat_planet: Optional[str] = Field(None, description="Sub-sub period lord (pratyantardasha)")
    planet_positions: Dict[str, float] = Field(
        ..., 
        description="Dictionary of planet longitudes (0-360)"
    )

@router.post("/dasha/vimshottari", response_model=Dict[str, Any], tags=["Dasha"])
async def calculate_vimshottari_dasha(request: DashaRequest) -> Dict[str, Any]:
    """
    Calculate Vimshottari Dasha periods for a given birth time and Moon position
    
    Args:
        request: DashaRequest containing birth_date and moon_longitude
        
    Returns:
        Dictionary containing all dasha period details including Mahadasha,
        Antardasha, and Pratyantardasha periods
        
    Raises:
        HTTPException: If moon_longitude is invalid or calculation fails
    """
    try:
        result = dasha_calculator.calculate_all_dasha_levels(
            request.birth_date,
            request.moon_longitude
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation failed: {str(e)}")

@router.get("/dasha/current", response_model=Dict[str, Any], tags=["Dasha"])
async def get_current_dasha(birth_date: datetime, moon_longitude: float) -> Dict[str, Any]:
    """
    Get the currently active Dasha periods for a given birth time and Moon position
    
    Args:
        birth_date: Birth date and time in ISO format
        moon_longitude: Moon's longitude at birth (0-360 degrees)
        
    Returns:
        Dictionary containing currently active Mahadasha, Antardasha,
        and Pratyantardasha periods
        
    Raises:
        HTTPException: If moon_longitude is invalid or calculation fails
    """
    try:
        # Calculate all dasha periods
        all_periods = dasha_calculator.calculate_all_dasha_levels(birth_date, moon_longitude)
        
        # Get current time
        current_time = datetime(2024, 12, 27, 4, 40, 19)  # Using provided time
        
        # Find current periods
        current_periods = {
            'mahadasha': None,
            'antardasha': None,
            'pratyantardasha': None
        }
        
        # Find current mahadasha
        for period in all_periods['periods']:
            if period['start_date'] <= current_time <= period['end_date']:
                current_periods['mahadasha'] = period
                
                # Find current antardasha
                for antardasha in period['antardasha']:
                    if antardasha['start_date'] <= current_time <= antardasha['end_date']:
                        current_periods['antardasha'] = antardasha
                        
                        # Find current pratyantardasha
                        for pratyantardasha in antardasha['pratyantardasha']:
                            if pratyantardasha['start_date'] <= current_time <= pratyantardasha['end_date']:
                                current_periods['pratyantardasha'] = pratyantardasha
                                break
                        break
                break
        
        if not current_periods['mahadasha']:
            raise ValueError("No active dasha period found for the given birth details")
            
        return current_periods
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation failed: {str(e)}")

@router.post("/interpret", response_model=Dict[str, Any], tags=["Dasha"])
async def interpret_dasha_period(request: DashaInterpretationRequest) -> Dict[str, Any]:
    """
    Get interpretation for a specific Dasha period combination
    
    Args:
        request: DashaInterpretationRequest containing planet combinations
        
    Returns:
        Dictionary containing interpretations and effects for the period
        
    Raises:
        HTTPException: If planet names are invalid
    """
    try:
        result = DashaEffects.interpret_dasha_period(
            request.main_planet,
            request.sub_planet,
            request.prat_planet
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/yoga", response_model=Dict[str, Any], tags=["Dasha"])
async def calculate_dasha_yogas(request: YogaCalculationRequest) -> Dict[str, Any]:
    """
    Calculate active Yogas and their predictions for current Dasha period
    
    Args:
        request: YogaCalculationRequest containing planet details
        
    Returns:
        Dictionary containing active yogas and their predictions
        
    Raises:
        HTTPException: If calculation fails
    """
    try:
        # Find active yogas
        active_yogas = DashaYoga.find_active_yogas(
            request.main_planet,
            request.sub_planet,
            request.prat_planet
        )
        
        # Generate predictions
        predictions = DashaYoga.get_yoga_predictions(
            active_yogas,
            request.planet_positions
        )
        
        return {
            'active_yogas': active_yogas,
            'predictions': predictions
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
