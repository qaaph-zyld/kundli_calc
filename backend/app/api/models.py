"""API Models Module

This module contains Pydantic models for API request and response validation.
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

class Location(BaseModel):
    """Location model for birth chart calculations."""
    latitude: Decimal = Field(
        ...,
        description="Latitude of the location",
        ge=-90,
        le=90,
        examples=[13.0827]  # Chennai
    )
    longitude: Decimal = Field(
        ...,
        description="Longitude of the location",
        ge=-180,
        le=180,
        examples=[80.2707]  # Chennai
    )
    altitude: Decimal = Field(
        default=Decimal('0'),
        description="Altitude in meters",
        examples=[0]
    )

class ChartRequest(BaseModel):
    """Request model for birth chart calculation."""
    date_time: datetime = Field(
        ...,
        description="Date and time in UTC",
        examples=["2024-01-01T12:00:00Z"]
    )
    latitude: Decimal = Field(
        ...,
        description="Latitude of birth location",
        ge=-90,
        le=90
    )
    longitude: Decimal = Field(
        ...,
        description="Longitude of birth location",
        ge=-180,
        le=180
    )
    altitude: Decimal = Field(
        default=Decimal('0'),
        description="Altitude in meters"
    )
    ayanamsa: int = Field(
        default=1,
        description="Ayanamsa system (1: Lahiri, 2: Raman, 3: KP)"
    )
    house_system: str = Field(
        default="P",
        description="House system (P: Placidus, K: Koch, R: Regiomontanus)"
    )

class PlanetaryPosition(BaseModel):
    """Model for planetary position data."""
    longitude: Decimal = Field(..., description="Longitude in degrees")
    latitude: Decimal = Field(..., description="Latitude in degrees")
    distance: Decimal = Field(..., description="Distance from Earth")
    speed: Decimal = Field(..., description="Speed in degrees per day")

class House(BaseModel):
    """Model for house data."""
    cusps: List[Decimal] = Field(..., description="House cusp positions")
    ascendant: Decimal = Field(..., description="Ascendant degree")
    midheaven: Decimal = Field(..., description="Midheaven degree")
    vertex: Decimal = Field(..., description="Vertex degree")

class Aspect(BaseModel):
    """Model for planetary aspect data."""
    planet1: str = Field(..., description="First planet")
    planet2: str = Field(..., description="Second planet")
    aspect_type: str = Field(..., description="Type of aspect")
    orb: Decimal = Field(..., description="Orb in degrees")
    exact_degree: Decimal = Field(..., description="Exact aspect degree")

class ChartResponse(BaseModel):
    """Response model for birth chart calculation."""
    model_config = ConfigDict(from_attributes=True)

    planetary_positions: Dict[str, PlanetaryPosition] = Field(
        ...,
        description="Positions of all planets"
    )
    houses: House = Field(..., description="House system data")
    aspects: List[Aspect] = Field(
        default_factory=list,
        description="Planetary aspects"
    )
    ayanamsa_value: Decimal = Field(
        ...,
        description="Ayanamsa value used in calculations"
    )
