"""House systems model module."""
from sqlalchemy import Column, String, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class HouseSystem(BaseModel):
    """House system model."""

    __tablename__ = "house_systems"

    birth_chart_id = Column(String(36), ForeignKey("birth_charts.id"))
    system_name = Column(String(50), nullable=False)
    house_number = Column(Integer, nullable=False)
    cusp_longitude = Column(Float, nullable=False)
    sign = Column(String(50))
    degree = Column(Float)

    # Relationships
    birth_chart = relationship("BirthChart", back_populates="house_systems")
