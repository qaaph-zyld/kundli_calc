from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from ..models.database_models import BirthChart
from ..schemas.chart import BirthChartCreate, BirthChartUpdate

def create_birth_chart(db: Session, chart: BirthChartCreate, user_id: Optional[UUID] = None) -> BirthChart:
    """Create a new birth chart."""
    db_chart = BirthChart(
        user_id=user_id,
        **chart.dict()
    )
    db.add(db_chart)
    db.commit()
    db.refresh(db_chart)
    return db_chart

def get_birth_chart(db: Session, chart_id: UUID) -> Optional[BirthChart]:
    """Get a birth chart by ID."""
    return db.query(BirthChart).filter(BirthChart.id == chart_id).first()

def get_user_birth_charts(db: Session, user_id: UUID, skip: int = 0, limit: int = 100) -> List[BirthChart]:
    """Get all birth charts for a user."""
    return db.query(BirthChart)\
        .filter(BirthChart.user_id == user_id)\
        .offset(skip)\
        .limit(limit)\
        .all()

def update_birth_chart(db: Session, chart_id: UUID, chart: BirthChartUpdate) -> Optional[BirthChart]:
    """Update a birth chart."""
    db_chart = get_birth_chart(db, chart_id)
    if db_chart:
        update_data = chart.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_chart, field, value)
        db_chart.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_chart)
    return db_chart

def delete_birth_chart(db: Session, chart_id: UUID) -> bool:
    """Delete a birth chart."""
    db_chart = get_birth_chart(db, chart_id)
    if db_chart:
        db.delete(db_chart)
        db.commit()
        return True
    return False
