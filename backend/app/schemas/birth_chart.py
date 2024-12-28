"""Birth chart schemas."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class PlanetaryPositionBase(BaseModel):
    """Base planetary position schema."""
    planet_name: str
    longitude: float
    latitude: Optional[float] = None
    speed: Optional[float] = None
    house: Optional[int] = None
    zodiac_sign: Optional[str] = None
    nakshatra: Optional[str] = None
    nakshatra_pada: Optional[int] = None


class PlanetaryPositionCreate(PlanetaryPositionBase):
    """Planetary position creation schema."""
    pass


class PlanetaryPosition(PlanetaryPositionBase):
    """Planetary position schema."""
    id: str
    birth_chart_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True


class BirthChartBase(BaseModel):
    """Base birth chart schema."""
    name: str
    date_of_birth: datetime
    time_of_birth: datetime
    place_of_birth: str
    latitude: float
    longitude: float
    timezone: str


class BirthChartCreate(BirthChartBase):
    """Birth chart creation schema."""
    pass


class BirthChartUpdate(BirthChartBase):
    """Birth chart update schema."""
    pass


class BirthChart(BirthChartBase):
    """Birth chart schema."""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    planetary_positions: List[PlanetaryPosition] = []

    class Config:
        """Pydantic config."""
        from_attributes = True
