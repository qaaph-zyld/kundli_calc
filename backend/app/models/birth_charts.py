"""Birth chart model module."""
from sqlalchemy import Column, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class BirthChart(BaseModel):
    """Birth chart model."""

    __tablename__ = "birth_charts"

    user_id = Column(String(36), ForeignKey("users.id"))
    name = Column(String(255), nullable=False)
    birth_time = Column(DateTime(timezone=True), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timezone = Column(String(50), nullable=False)
    place_name = Column(String(255))
    notes = Column(String(1000))

    # Relationships
    user = relationship("User", back_populates="birth_charts")
    planetary_positions = relationship("PlanetaryPosition", back_populates="birth_chart")
    house_systems = relationship("HouseSystem", back_populates="birth_chart")
    divisional_charts = relationship("DivisionalChart", back_populates="birth_chart")
    dasha_periods = relationship("DashaPeriod", back_populates="birth_chart")
    yoga_combinations = relationship("YogaCombination", back_populates="birth_chart")
