"""Dasha periods model module."""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class DashaPeriod(BaseModel):
    """Dasha period model."""

    __tablename__ = "dasha_periods"

    birth_chart_id = Column(String(36), ForeignKey("birth_charts.id"))
    dasha_type = Column(String(50), nullable=False)  # Maha, Antara, etc.
    planet_name = Column(String(50), nullable=False)
    sub_planet_name = Column(String(50))
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)

    # Relationships
    birth_chart = relationship("BirthChart", back_populates="dasha_periods")
