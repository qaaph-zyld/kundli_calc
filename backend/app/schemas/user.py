"""User schema module."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False


class UserCreate(UserBase):
    """User creation schema."""
    password: str


class UserUpdate(UserBase):
    """User update schema."""
    password: Optional[str] = None


class UserInDBBase(UserBase):
    """Base user in DB schema."""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True


class User(UserInDBBase):
    """User schema."""
    pass


class UserInDB(UserInDBBase):
    """User in DB schema."""
    hashed_password: str
