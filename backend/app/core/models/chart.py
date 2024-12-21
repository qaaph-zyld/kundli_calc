from datetime import datetime
from typing import Dict, List, Optional
from decimal import Decimal
from pydantic import BaseModel, validator

class Location(BaseModel):
    latitude: Decimal
    longitude: Decimal
    altitude: Decimal = Decimal('0')
    
    @validator('latitude')
    def validate_latitude(cls, v):
        if v < -90 or v > 90:
            raise ValueError('Latitude must be between -90 and 90 degrees')
        return v
    
    @validator('longitude')
    def validate_longitude(cls, v):
        if v < -180 or v > 180:
            raise ValueError('Longitude must be between -180 and 180 degrees')
        return v

class PlanetaryPosition(BaseModel):
    longitude: Decimal
    latitude: Optional[Decimal]
    distance: Optional[Decimal]
    speed: Optional[Decimal]

class HouseData(BaseModel):
    cusps: List[Decimal]
    ascendant: Decimal
    midheaven: Decimal
    armc: Decimal
    vertex: Decimal

class Aspect(BaseModel):
    planet1: str
    planet2: str
    aspect: str
    angle: Decimal
    orb: Decimal
    is_major: bool
    is_applying: bool

class NakshatraData(BaseModel):
    number: int
    name: str
    lord: str
    pada: int
    degrees_traversed: Decimal
    total_degrees: Decimal

class BirthChart(BaseModel):
    date_time: datetime
    location: Location
    ayanamsa: int = 1
    house_system: str = 'P'
    planetary_positions: Dict[str, PlanetaryPosition]
    houses: HouseData
    aspects: List[Aspect]
    nakshatras: Dict[str, NakshatraData]
