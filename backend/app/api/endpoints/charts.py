from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Optional

from ...core.calculations.astronomical import AstronomicalCalculator, Location
from ...core.calculations.houses import HouseCalculator
from ...core.models.chart import BirthChart, Location as LocationModel

router = APIRouter()

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
        
        # Create and return birth chart
        return BirthChart(
            date_time=date_time,
            location=location_model,
            ayanamsa=ayanamsa,
            house_system=house_system,
            planetary_positions=planetary_positions,
            houses=houses
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error calculating birth chart: {str(e)}"
        )
