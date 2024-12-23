from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime, timedelta
from typing import Optional

from ..models import ChartRequest, ChartResponse, Location as LocationModel
from ...core.calculations.astronomical import AstronomicalCalculator, Location
from ...core.calculations.houses import HouseCalculator
from ...core.calculations.aspects import EnhancedAspectCalculator as AspectCalculator
from ...core.calculations.nakshatra import NakshatraCalculator
from ...core.cache import RedisCache
from ...core.config import settings

router = APIRouter()
cache = RedisCache()

@router.post(
    "/calculate",
    response_model=ChartResponse,
    summary="Calculate birth chart",
    description="""
    Calculate a Vedic birth chart based on date, time, and location.
    
    This endpoint performs the following calculations:
    - Planetary positions using Swiss Ephemeris
    - House cusps and angles
    - Planetary aspects
    - Nakshatras for all planets
    
    The response includes:
    - Planetary positions (longitude, latitude, distance, speed)
    - House system data (cusps, ascendant, midheaven, vertex)
    - Planetary aspects
    - Ayanamsa value used in calculations
    """,
    response_description="Complete birth chart data"
)
async def calculate_chart(
    request: ChartRequest = Depends()
) -> ChartResponse:
    """Calculate a Vedic birth chart."""
    try:
        # Generate cache key
        cache_key = cache.generate_key(
            "chart",
            request.date_time.isoformat(),
            float(request.latitude),
            float(request.longitude),
            float(request.altitude),
            request.ayanamsa,
            request.house_system
        )
        
        # Try to get from cache
        if cached_result := await cache.get(cache_key):
            return ChartResponse(**cached_result)
        
        # Create location objects
        calc_location = Location(
            float(request.latitude),
            float(request.longitude),
            float(request.altitude)
        )
        
        # Initialize calculators
        astro_calc = AstronomicalCalculator(ayanamsa=request.ayanamsa)
        house_calc = HouseCalculator(house_system=request.house_system)
        
        # Perform calculations
        planetary_positions = astro_calc.calculate_planetary_positions(
            request.date_time,
            calc_location
        )
        
        houses = house_calc.calculate_houses(
            request.date_time,
            calc_location
        )
        
        # Calculate aspects
        aspects = AspectCalculator.calculate_aspects(
            planetary_positions=planetary_positions,
            ayanamsa_value=request.ayanamsa
        )
        
        # Create response
        result = ChartResponse(
            planetary_positions=planetary_positions,
            houses=houses,
            aspects=aspects,
            ayanamsa_value=astro_calc.get_ayanamsa_value(request.date_time)
        )
        
        # Cache the result
        await cache.set(
            cache_key,
            result.model_dump(),
            expire=timedelta(seconds=settings.REDIS_CACHE_EXPIRE)
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error calculating birth chart: {str(e)}"
        )
