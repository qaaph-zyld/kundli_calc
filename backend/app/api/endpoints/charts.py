from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timedelta
from typing import Optional

from ...core.calculations.astronomical import AstronomicalCalculator, Location
from ...core.calculations.houses import HouseCalculator
from ...core.calculations.aspects import EnhancedAspectCalculator as AspectCalculator
from ...core.calculations.nakshatra import NakshatraCalculator
from ...core.models.chart import BirthChart, Location as LocationModel
from ...core.cache import RedisCache
from ...core.config import settings

router = APIRouter()
cache = RedisCache()

@router.post("/calculate", response_model=BirthChart)
async def calculate_chart(
    date_time: datetime,
    latitude: float,
    longitude: float,
    altitude: Optional[float] = 0,
    ayanamsa: Optional[int] = 1,
    house_system: Optional[str] = 'P'
):
    try:
        # Generate cache key
        cache_key = cache.generate_key(
            "chart",
            date_time.isoformat(),
            latitude,
            longitude,
            altitude,
            ayanamsa,
            house_system
        )
        
        # Try to get from cache
        if cached_result := await cache.get(cache_key):
            return cached_result
        
        # Create location objects
        calc_location = Location(latitude, longitude, altitude)
        location_model = LocationModel(
            latitude=latitude,
            longitude=longitude,
            altitude=altitude
        )
        
        # Initialize calculators
        astro_calc = AstronomicalCalculator(ayanamsa=ayanamsa)
        house_calc = HouseCalculator(house_system=house_system)
        
        # Perform calculations
        planetary_positions = astro_calc.calculate_planetary_positions(
            date_time,
            calc_location
        )
        
        houses = house_calc.calculate_houses(
            date_time,
            calc_location
        )
        
        # Calculate aspects and nakshatras
        aspects = AspectCalculator.calculate_aspects(planetary_positions)
        nakshatras = NakshatraCalculator.calculate_all_nakshatras(planetary_positions)
        
        # Create response
        result = BirthChart(
            date_time=date_time,
            location=location_model,
            ayanamsa=ayanamsa,
            house_system=house_system,
            planetary_positions=planetary_positions,
            houses=houses,
            aspects=aspects,
            nakshatras=nakshatras
        )
        
        # Cache the result
        await cache.set(
            cache_key,
            result.dict(),
            expire=timedelta(seconds=settings.REDIS_CACHE_EXPIRE)
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error calculating birth chart: {str(e)}"
        )
