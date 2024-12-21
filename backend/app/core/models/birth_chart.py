from sqlalchemy import Column, String, DateTime, Float, Integer, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from ..database import Base

class BirthChart(Base):
    __tablename__ = "birth_charts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Birth Details
    name = Column(String, nullable=True)
    date_time = Column(DateTime, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, default=0)
    time_zone = Column(String, nullable=False)
    
    # Calculation Settings
    ayanamsa = Column(Integer, default=1)  # Default to Lahiri
    house_system = Column(String, default='P')  # Default to Placidus
    
    # Calculated Data
    planetary_positions = Column(JSON)
    house_cusps = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
