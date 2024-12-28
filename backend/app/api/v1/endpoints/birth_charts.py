"""Birth chart endpoints."""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.core.cache import cache_response, invalidate_cache
from app.core.config.settings import settings
from app.crud import birth_chart as crud
from app.models.users import User
from app.schemas.birth_chart import BirthChart, BirthChartCreate, BirthChartUpdate

router = APIRouter()


@router.get("/", response_model=List[BirthChart])
@cache_response(prefix="user_birth_charts")
async def read_birth_charts(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Retrieve birth charts."""
    birth_charts = crud.get_birth_charts_by_user(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )
    return birth_charts


@router.post("/", response_model=BirthChart)
async def create_birth_chart(
    *,
    db: Session = Depends(get_db),
    birth_chart_in: BirthChartCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Create new birth chart."""
    birth_chart = crud.create_birth_chart(
        db=db, birth_chart=birth_chart_in, user_id=current_user.id
    )
    # Invalidate user's birth charts cache
    invalidate_cache("user_birth_charts", current_user.id)
    return birth_chart


@router.get("/{birth_chart_id}", response_model=BirthChart)
@cache_response(prefix="birth_chart")
async def read_birth_chart(
    *,
    db: Session = Depends(get_db),
    birth_chart_id: str,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get birth chart by ID."""
    birth_chart = crud.get_birth_chart(db=db, birth_chart_id=birth_chart_id)
    if not birth_chart:
        raise HTTPException(status_code=404, detail="Birth chart not found")
    if birth_chart.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return birth_chart


@router.put("/{birth_chart_id}", response_model=BirthChart)
async def update_birth_chart(
    *,
    db: Session = Depends(get_db),
    birth_chart_id: str,
    birth_chart_in: BirthChartUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Update birth chart."""
    birth_chart = crud.get_birth_chart(db=db, birth_chart_id=birth_chart_id)
    if not birth_chart:
        raise HTTPException(status_code=404, detail="Birth chart not found")
    if birth_chart.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    birth_chart = crud.update_birth_chart(
        db=db, birth_chart_id=birth_chart_id, birth_chart=birth_chart_in
    )
    # Invalidate caches
    invalidate_cache("birth_chart", birth_chart_id)
    invalidate_cache("user_birth_charts", current_user.id)
    return birth_chart


@router.delete("/{birth_chart_id}", response_model=BirthChart)
async def delete_birth_chart(
    *,
    db: Session = Depends(get_db),
    birth_chart_id: str,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Delete birth chart."""
    birth_chart = crud.get_birth_chart(db=db, birth_chart_id=birth_chart_id)
    if not birth_chart:
        raise HTTPException(status_code=404, detail="Birth chart not found")
    if birth_chart.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    birth_chart = crud.delete_birth_chart(db=db, birth_chart_id=birth_chart_id)
    # Invalidate caches
    invalidate_cache("birth_chart", birth_chart_id)
    invalidate_cache("user_birth_charts", current_user.id)
    return birth_chart
