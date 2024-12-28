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

class PlanetaryStrength(BaseModel):
    """Model for planetary strength calculations."""
    shadbala: Decimal = Field(..., description="Shadbala strength")
    dignity_score: Decimal = Field(..., description="Dignity-based strength")
    positional_strength: Decimal = Field(..., description="Positional strength")
    temporal_strength: Decimal = Field(..., description="Temporal strength")
    aspect_strength: Decimal = Field(..., description="Aspect-based strength")
    total_strength: Decimal = Field(..., description="Total calculated strength")

class AspectInfluence(BaseModel):
    """Model for detailed aspect analysis."""
    aspect_type: str = Field(..., description="Type of aspect (e.g., conjunction, trine)")
    strength: Decimal = Field(..., description="Strength of the aspect")
    is_beneficial: bool = Field(..., description="Whether the aspect is beneficial")
    special_effects: Optional[List[str]] = Field(default=None, description="Special effects of the aspect")

class DivisionalChart(BaseModel):
    """Model for divisional chart data."""
    division: int = Field(..., description="Chart division (1 for D1, 9 for D9, etc.)")
    planetary_positions: Dict[str, PlanetaryPosition] = Field(..., description="Planetary positions in this division")
    house_cusps: List[Decimal] = Field(..., description="House cusps in this division")
    special_points: Dict[str, Decimal] = Field(..., description="Special points in this division")

class ChartResponse(BaseModel):
    """Response model for birth chart calculation."""
    model_config = ConfigDict(from_attributes=True)

    planetary_positions: Dict[str, PlanetaryPosition] = Field(
        ...,
        description="Positions of all planets"
    )
    houses: House = Field(..., description="House system data")
    aspects: List[AspectInfluence] = Field(
        default_factory=list,
        description="Detailed planetary aspects"
    )
    ayanamsa_value: Decimal = Field(
        ...,
        description="Calculated ayanamsa value"
    )
    planetary_strengths: Dict[str, PlanetaryStrength] = Field(
        ...,
        description="Detailed strength calculations for each planet"
    )
    divisional_charts: Dict[str, DivisionalChart] = Field(
        ...,
        description="Calculated divisional charts"
    )
