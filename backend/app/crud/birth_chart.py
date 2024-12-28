"""Birth chart CRUD operations."""
from typing import List, Optional
from sqlalchemy.orm import Session
import uuid

from app.models.birth_charts import BirthChart
from app.models.planetary_positions import PlanetaryPosition
from app.schemas.birth_chart import BirthChartCreate, BirthChartUpdate


def get_birth_chart(db: Session, birth_chart_id: str) -> Optional[BirthChart]:
    """Get birth chart by ID."""
    return db.query(BirthChart).filter(BirthChart.id == birth_chart_id).first()


def get_birth_charts_by_user(
    db: Session, user_id: str, skip: int = 0, limit: int = 100
) -> List[BirthChart]:
    """Get birth charts by user ID."""
    return (
        db.query(BirthChart)
        .filter(BirthChart.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_birth_chart(
    db: Session, birth_chart: BirthChartCreate, user_id: str
) -> BirthChart:
    """Create new birth chart."""
    db_birth_chart = BirthChart(
        id=str(uuid.uuid4()),
        user_id=user_id,
        **birth_chart.model_dump()
    )
    db.add(db_birth_chart)
    db.commit()
    db.refresh(db_birth_chart)
    return db_birth_chart


def update_birth_chart(
    db: Session, birth_chart_id: str, birth_chart: BirthChartUpdate
) -> Optional[BirthChart]:
    """Update birth chart."""
    db_birth_chart = get_birth_chart(db, birth_chart_id=birth_chart_id)
    if not db_birth_chart:
        return None
    
    update_data = birth_chart.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_birth_chart, field, value)
    
    db.add(db_birth_chart)
    db.commit()
    db.refresh(db_birth_chart)
    return db_birth_chart


def delete_birth_chart(db: Session, birth_chart_id: str) -> Optional[BirthChart]:
    """Delete birth chart."""
    db_birth_chart = get_birth_chart(db, birth_chart_id=birth_chart_id)
    if db_birth_chart:
        db.delete(db_birth_chart)
        db.commit()
    return db_birth_chart


def create_planetary_position(
    db: Session, 
    birth_chart_id: str, 
    planet_name: str,
    longitude: float,
    latitude: Optional[float] = None,
    speed: Optional[float] = None,
    house: Optional[int] = None,
    zodiac_sign: Optional[str] = None,
    nakshatra: Optional[str] = None,
    nakshatra_pada: Optional[int] = None
) -> PlanetaryPosition:
    """Create new planetary position."""
    db_position = PlanetaryPosition(
        id=str(uuid.uuid4()),
        birth_chart_id=birth_chart_id,
        planet_name=planet_name,
        longitude=longitude,
        latitude=latitude,
        speed=speed,
        house=house,
        zodiac_sign=zodiac_sign,
        nakshatra=nakshatra,
        nakshatra_pada=nakshatra_pada
    )
    db.add(db_position)
    db.commit()
    db.refresh(db_position)
    return db_position
