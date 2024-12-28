"""Database models module."""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Integer, Float, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel
import uuid


class User(BaseModel):
    """User model."""

    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    last_login = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    birth_charts = relationship("BirthChart", back_populates="user", cascade="all, delete-orphan")


class BirthChart(BaseModel):
    """Birth chart model."""

    __tablename__ = "birth_charts"
    __table_args__ = {'extend_existing': True}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    birth_time = Column(DateTime(timezone=True), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timezone = Column(String(50), nullable=False)
    description = Column(String(1000))
    altitude = Column(Float, default=0)
    
    # Calculation settings
    ayanamsa = Column(Integer, default=1)
    house_system = Column(String(10), default='P')
    
    # Calculated data
    planetary_positions = Column(JSON, nullable=False)
    houses = Column(JSON, nullable=False)
    aspects = Column(JSON, nullable=False)
    dashas = Column(JSON, nullable=False)
    divisional_charts = Column(JSON, nullable=False)
    ashtakavarga = Column(JSON, nullable=False)
    shadbala = Column(JSON, nullable=False)
    nakshatras = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign keys
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="birth_charts")
    house_systems = relationship("HouseSystem", back_populates="birth_chart", cascade="all, delete-orphan")
    planetary_positions = relationship("PlanetaryPosition", back_populates="birth_chart", cascade="all, delete-orphan")


class HouseSystem(BaseModel):
    """House system model."""

    __tablename__ = "house_systems"
    __table_args__ = {'extend_existing': True}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    system_name = Column(String(50), nullable=False)
    house_number = Column(Integer, nullable=False)
    degree = Column(Float, nullable=False)
    sign = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign keys
    birth_chart_id = Column(String(36), ForeignKey("birth_charts.id"), nullable=False)

    # Relationships
    birth_chart = relationship("BirthChart", back_populates="house_systems")


class PlanetaryPosition(BaseModel):
    """Planetary position model."""

    __tablename__ = "planetary_positions"
    __table_args__ = {'extend_existing': True}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    planet = Column(String(20), nullable=False)
    degree = Column(Float, nullable=False)
    sign = Column(String(20), nullable=False)
    house = Column(Integer, nullable=False)
    retrograde = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign keys
    birth_chart_id = Column(String(36), ForeignKey("birth_charts.id"), nullable=False)

    # Relationships
    birth_chart = relationship("BirthChart", back_populates="planetary_positions")
