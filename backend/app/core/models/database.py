from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BirthChart(Base):
    __tablename__ = "birth_charts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Birth Details
    name = Column(String, nullable=True)
    date_time = Column(DateTime, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, default=0)
    timezone = Column(String, nullable=False)
    
    # Calculation Settings
    ayanamsa = Column(Integer, default=1)
    house_system = Column(String, default='P')
    
    # Calculated Data
    planetary_positions = Column(JSON, nullable=False)
    houses = Column(JSON, nullable=False)
    aspects = Column(JSON, nullable=False)
    nakshatras = Column(JSON, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
