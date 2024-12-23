from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, Field, field_validator

from ...core.calculations.astronomical import AstronomicalCalculator, Location
from ...core.calculations.houses import HouseCalculator
from ...core.calculations.aspects import EnhancedAspectCalculator as AspectCalculator
from ...core.calculations.nakshatra import NakshatraCalculator
from ...core.models.chart import BirthChart, Location as LocationModel
from ...core.cache import RedisCache
from ...core.config import settings

router = APIRouter()
cache = RedisCache()

class ChartRequest(BaseModel):
    date_time: datetime
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    altitude: Optional[float] = Field(0, ge=0)
    ayanamsa: Optional[int] = Field(1, ge=0)
    house_system: Optional[str] = Field('P')

    @field_validator('house_system')
    def validate_house_system(cls, v):
        valid_systems = ['P', 'K', 'C', 'R', 'E', 'V', 'W', 'X', 'H', 'T', 'B', 'M', 'U', 'G']
        if v not in valid_systems:
            raise ValueError(f"Invalid house system. Must be one of: {', '.join(valid_systems)}")
        return v

@router.post("/calculate", response_model=BirthChart)
async def calculate_chart(request: ChartRequest):
    try:
        # Generate cache key
        cache_key = cache.generate_key(
            "chart",
            request.date_time.isoformat(),
            request.latitude,
            request.longitude,
            request.altitude,
            request.ayanamsa,
            request.house_system
        )
        
        # Try to get from cache
        if cached_result := await cache.get(cache_key):
            return cached_result
        
        # Create location objects
        calc_location = Location(request.latitude, request.longitude, request.altitude)
        location_model = LocationModel(
            latitude=request.latitude,
            longitude=request.longitude,
            altitude=request.altitude
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
        
        # Calculate aspects and nakshatras
        aspects = AspectCalculator.calculate_aspects(
            planetary_positions=planetary_positions,
            ayanamsa_value=request.ayanamsa
        )
        nakshatras = NakshatraCalculator.calculate_all_nakshatras(planetary_positions)
        
        # Create response
        result = BirthChart(
            date_time=request.date_time,
            location=location_model,
            ayanamsa=request.ayanamsa,
            house_system=request.house_system,
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
