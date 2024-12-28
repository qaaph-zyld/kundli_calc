"""Divisional charts model module."""
from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class DivisionalChart(BaseModel):
    """Divisional chart model."""

    __tablename__ = "divisional_charts"

    birth_chart_id = Column(String(36), ForeignKey("birth_charts.id"))
    division_type = Column(String(50), nullable=False)  # D1, D2, D3, etc.
    planet_name = Column(String(50), nullable=False)
    house = Column(Integer)
    longitude = Column(Float)
    zodiac_sign = Column(String(50))

    # Relationships
    birth_chart = relationship("BirthChart", back_populates="divisional_charts")
