from fastapi import APIRouter, HTTPException, status
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, validator
import logging

from app.core.calculations.astronomical import AstronomicalCalculator, Location
from app.core.calculations.ayanamsa import EnhancedAyanamsaManager
from app.core.calculations.divisional import EnhancedDivisionalChartEngine
from app.core.calculations.strength import EnhancedPlanetaryStrengthEngine
from app.core.calculations.aspects import EnhancedAspectCalculator
from app.core.calculations.house_analysis import EnhancedHouseAnalysisEngine

router = APIRouter()
logger = logging.getLogger(__name__)

class HoroscopeRequest(BaseModel):
    datetime_utc: datetime
    latitude: float
    longitude: float
    altitude: float = 0
    ayanamsa_system: str = "Lahiri"
    divisional_charts: Optional[List[str]] = None

    @validator('latitude')
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError("Latitude must be between -90 and 90 degrees")
        return v

    @validator('longitude')
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError("Longitude must be between -180 and 180 degrees")
        return v

    @validator('altitude')
    def validate_altitude(cls, v):
        if v < -1000 or v > 20000:  # Reasonable altitude range in meters
            raise ValueError("Altitude must be between -1000 and 20000 meters")
        return v

    @validator('ayanamsa_system')
    def validate_ayanamsa(cls, v):
        valid_systems = ["Lahiri", "Raman", "KP", "Krishnamurti", "Yukteshwar"]
        if v not in valid_systems:
            raise ValueError(f"Ayanamsa system must be one of: {', '.join(valid_systems)}")
        return v

class HoroscopeResponse(BaseModel):
    planetary_positions: Dict
    divisional_charts: Dict
    planetary_strengths: Dict
    aspects: List
    house_analysis: Dict
    ayanamsa_value: float

class ErrorResponse(BaseModel):
    detail: str
    error_code: str
    timestamp: datetime

@router.post("/calculate", 
            response_model=HoroscopeResponse,
            responses={
                status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
                status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse}
            })
async def calculate_horoscope(request: HoroscopeRequest):
    try:
        logger.info(f"Processing horoscope calculation request for datetime: {request.datetime_utc}")
        
        # Initialize components
        location = Location(
            latitude=request.latitude,
            longitude=request.longitude,
            altitude=request.altitude
        )
        
        # Initialize calculation engines
        try:
            astro_calc = AstronomicalCalculator()
            ayanamsa_manager = EnhancedAyanamsaManager()
            divisional_engine = EnhancedDivisionalChartEngine()
            strength_engine = EnhancedPlanetaryStrengthEngine()
            aspect_calculator = EnhancedAspectCalculator()
            house_analyzer = EnhancedHouseAnalysisEngine()
        except Exception as e:
            logger.error(f"Failed to initialize calculation engines: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "detail": "Failed to initialize calculation engines",
                    "error_code": "INIT_ERROR",
                    "timestamp": datetime.utcnow()
                }
            )
        
        # Calculate ayanamsa
        try:
            ayanamsa = ayanamsa_manager.calculate_precise_ayanamsa(
                request.datetime_utc,
                request.ayanamsa_system
            )
        except Exception as e:
            logger.error(f"Ayanamsa calculation failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "detail": "Ayanamsa calculation failed",
                    "error_code": "AYANAMSA_ERROR",
                    "timestamp": datetime.utcnow()
                }
            )
        
        # Calculate planetary positions
        try:
            planetary_positions = astro_calc.calculate_planetary_positions(
                request.datetime_utc,
                location
            )
        except Exception as e:
            logger.error(f"Planetary position calculation failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "detail": "Planetary position calculation failed",
                    "error_code": "POSITION_ERROR",
                    "timestamp": datetime.utcnow()
                }
            )
        
        # Calculate divisional charts
        divisional_charts = {}
        if request.divisional_charts:
            try:
                for planet, data in planetary_positions.items():
                    divisional_charts[planet] = divisional_engine.calculate_all_divisions(
                        data['longitude'],
                        request.divisional_charts
                    )
            except Exception as e:
                logger.error(f"Divisional chart calculation failed: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "detail": "Divisional chart calculation failed",
                        "error_code": "DIVISION_ERROR",
                        "timestamp": datetime.utcnow()
                    }
                )
        
        # Calculate planetary strengths
        try:
            planetary_strengths = {}
            for planet, data in planetary_positions.items():
                planetary_strengths[planet] = strength_engine.calculate_complete_strengths(
                    planet=data,
                    chart={
                        'ascendant': planetary_positions['Ascendant']['longitude'],
                        'planets': planetary_positions,
                        'houses': {},  
                        'aspects': []  
                    }
                )
        except Exception as e:
            logger.error(f"Planetary strength calculation failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "detail": "Planetary strength calculation failed",
                    "error_code": "STRENGTH_ERROR",
                    "timestamp": datetime.utcnow()
                }
            )
        
        # Calculate aspects
        try:
            aspects = aspect_calculator.calculate_aspects(planetary_positions)
        except Exception as e:
            logger.error(f"Aspect calculation failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "detail": "Aspect calculation failed",
                    "error_code": "ASPECT_ERROR",
                    "timestamp": datetime.utcnow()
                }
            )
        
        # Analyze houses
        try:
            house_analysis = {}
            for house in range(1, 13):
                house_analysis[house] = house_analyzer.analyze_house(
                    house=house,
                    occupants=[p for p, d in planetary_positions.items() 
                              if d.get('house') == house],
                    aspects=[a for a in aspects 
                            if a.planet1 == f'H{house}' or a.planet2 == f'H{house}'],
                    lord=planetary_positions.get(f'L{house}', {})
                )
        except Exception as e:
            logger.error(f"House analysis failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "detail": "House analysis failed",
                    "error_code": "HOUSE_ERROR",
                    "timestamp": datetime.utcnow()
                }
            )
        
        logger.info("Successfully completed horoscope calculation")
        
        return HoroscopeResponse(
            planetary_positions=planetary_positions,
            divisional_charts=divisional_charts,
            planetary_strengths=planetary_strengths,
            aspects=aspects,
            house_analysis=house_analysis,
            ayanamsa_value=ayanamsa
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in horoscope calculation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "detail": "An unexpected error occurred",
                "error_code": "UNKNOWN_ERROR",
                "timestamp": datetime.utcnow()
            }
        )
