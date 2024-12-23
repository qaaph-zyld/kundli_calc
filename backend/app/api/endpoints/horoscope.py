from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator, ConfigDict
from app.core.calculations.astronomical import AstronomicalCalculator, Location
from app.core.calculations.ayanamsa import EnhancedAyanamsaManager
from app.core.calculations.divisional import EnhancedDivisionalChartEngine
from app.core.calculations.strength import EnhancedPlanetaryStrengthEngine
from app.core.calculations.aspects import EnhancedAspectCalculator
from app.core.calculations.house_analysis import EnhancedHouseAnalysisEngine
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class HoroscopeRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    datetime_utc: str
    latitude: float
    longitude: float
    altitude: float = 0
    ayanamsa_system: str
    divisional_charts: Optional[List[str]] = None

    @field_validator('datetime_utc')
    @classmethod
    def validate_datetime(cls, v):
        try:
            datetime.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError('Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)')

    @field_validator('latitude')
    @classmethod
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('Latitude must be between -90 and 90 degrees')
        return v

    @field_validator('longitude')
    @classmethod
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('Longitude must be between -180 and 180 degrees')
        return v

    @field_validator('altitude')
    @classmethod
    def validate_altitude(cls, v):
        if not -1000 <= v <= 9000:  # Reasonable range for human habitation
            raise ValueError('Altitude must be between -1000 and 9000 meters')
        return v

    @field_validator('ayanamsa_system')
    @classmethod
    def validate_ayanamsa_system(cls, v):
        valid_systems = ['LAHIRI', 'RAMAN', 'KP', 'FAGAN_BRADLEY']
        if v.upper() not in valid_systems:
            raise ValueError(f'Invalid ayanamsa system. Must be one of: {", ".join(valid_systems)}')
        return v.upper()

@router.post("/v1/horoscope/calculate")
async def calculate_horoscope(request: HoroscopeRequest):
    """
    Calculate horoscope based on given parameters.
    
    Parameters:
    - datetime_utc: UTC datetime in ISO format (YYYY-MM-DDTHH:MM:SS)
    - latitude: Geographic latitude (-90 to 90)
    - longitude: Geographic longitude (-180 to 180)
    - altitude: Altitude in meters (optional, default 0)
    - ayanamsa_system: Ayanamsa system to use (LAHIRI, RAMAN, KP, FAGAN_BRADLEY)
    - divisional_charts: List of divisional charts to calculate (optional)
    
    Returns:
    - Horoscope data including planetary positions, ayanamsa value, divisional charts,
      planetary strengths, aspects, and house analysis
    """
    try:
        # Parse datetime
        birth_time = datetime.fromisoformat(request.datetime_utc)
        
        # Create location object
        location = Location(
            latitude=request.latitude,
            longitude=request.longitude,
            altitude=request.altitude
        )
        
        # Initialize calculation engines
        astro_calc = AstronomicalCalculator()
        ayanamsa_calc = EnhancedAyanamsaManager()
        divisional_calc = EnhancedDivisionalChartEngine()
        strength_calc = EnhancedPlanetaryStrengthEngine()
        aspect_calc = EnhancedAspectCalculator()
        house_calc = EnhancedHouseAnalysisEngine()
        
        # Calculate planetary positions
        planetary_positions = astro_calc.calculate_planetary_positions(
            date=birth_time,
            location=location
        )
        
        # Calculate ayanamsa
        ayanamsa_value = ayanamsa_calc.calculate_precise_ayanamsa(
            datetime_utc=birth_time,
            system=request.ayanamsa_system
        )
        
        # Calculate divisional charts if requested
        divisional_charts = {}
        if request.divisional_charts:
            divisional_charts = divisional_calc.calculate_all_divisions(
                planetary_positions=planetary_positions,
                ayanamsa_value=ayanamsa_value,
                charts=request.divisional_charts
            )
        
        # Calculate planetary strengths
        planetary_strengths = strength_calc.calculate_complete_strengths(
            planetary_positions=planetary_positions,
            birth_time=birth_time,
            location=location
        )
        
        # Calculate aspects
        aspects = aspect_calc.calculate_aspects(
            planetary_positions=planetary_positions,
            ayanamsa_value=ayanamsa_value
        )
        
        # Analyze houses
        house_analysis = {}
        for house in range(1, 13):  # 12 houses
            house_analysis[str(house)] = house_calc.analyze_house(
                house_number=house,
                planetary_positions=planetary_positions,
                ayanamsa_value=ayanamsa_value
            )
        
        # Prepare response
        response = {
            "planetary_positions": planetary_positions,
            "ayanamsa_value": ayanamsa_value,
            "divisional_charts": divisional_charts,
            "planetary_strengths": planetary_strengths,
            "aspects": aspects,
            "house_analysis": house_analysis
        }
        
        return response
        
    except ValueError as e:
        # Handle validation errors
        raise HTTPException(
            status_code=422,
            detail=str(e)
        )
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
