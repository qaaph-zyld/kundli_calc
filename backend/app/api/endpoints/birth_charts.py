from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ...core.database import get_db
from ...crud import birth_charts
from ...schemas.chart import BirthChart, BirthChartCreate, BirthChartUpdate

router = APIRouter()

@router.post("/", response_model=BirthChart)
def create_birth_chart(
    chart: BirthChartCreate,
    db: Session = Depends(get_db)
):
    """Create a new birth chart."""
    return birth_charts.create_birth_chart(db=db, chart=chart)

@router.get("/{chart_id}", response_model=BirthChart)
def read_birth_chart(
    chart_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific birth chart by ID."""
    db_chart = birth_charts.get_birth_chart(db, chart_id=chart_id)
    if db_chart is None:
        raise HTTPException(status_code=404, detail="Birth chart not found")
    return db_chart

@router.get("/user/{user_id}", response_model=List[BirthChart])
def read_user_birth_charts(
    user_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all birth charts for a specific user."""
    return birth_charts.get_user_birth_charts(
        db, user_id=user_id, skip=skip, limit=limit
    )

@router.put("/{chart_id}", response_model=BirthChart)
def update_birth_chart(
    chart_id: UUID,
    chart: BirthChartUpdate,
    db: Session = Depends(get_db)
):
    """Update a birth chart."""
    db_chart = birth_charts.update_birth_chart(db, chart_id=chart_id, chart=chart)
    if db_chart is None:
        raise HTTPException(status_code=404, detail="Birth chart not found")
    return db_chart

@router.delete("/{chart_id}")
def delete_birth_chart(
    chart_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a birth chart."""
    success = birth_charts.delete_birth_chart(db, chart_id=chart_id)
    if not success:
        raise HTTPException(status_code=404, detail="Birth chart not found")
    return {"status": "success"}
