"""Base model module."""
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, String
from app.core.database import Base


class BaseModel(Base):
    """Base model class for all models."""
    __abstract__ = True

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
