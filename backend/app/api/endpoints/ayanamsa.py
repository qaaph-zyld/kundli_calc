"""Ayanamsa calculation endpoints."""
from typing import Dict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime

router = APIRouter()


class AyanamsaRequest(BaseModel):
    """Request model for ayanamsa calculation."""

    date: datetime = Field(..., description="Date for ayanamsa calculation")
    ayanamsa_type: str = Field(
        "lahiri",
        description="Type of ayanamsa (lahiri, raman, krishnamurti, etc.)"
    )


@router.post("/calculate", response_model=Dict[str, float])
async def calculate_ayanamsa(request: AyanamsaRequest):
    """
    Calculate ayanamsa value for a given date.

    Args:
        request: AyanamsaRequest containing date and ayanamsa type

    Returns:
        Dictionary containing ayanamsa value
    """
    try:
        # For now, return a mock value
        # TODO: Implement actual calculation using Swiss Ephemeris
        return {"ayanamsa": 24.5}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating ayanamsa: {str(e)}"
        )