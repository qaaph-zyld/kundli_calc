from pydantic import BaseModel, UUID4, Field
from datetime import datetime
from typing import Dict, List, Optional

class BirthChartBase(BaseModel):
    name: Optional[str] = None
    date_time: datetime
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    altitude: float = Field(default=0)
    timezone: str
    ayanamsa: int = Field(default=1)
    house_system: str = Field(default='P')

class BirthChartCreate(BirthChartBase):
    planetary_positions: Dict
    houses: Dict
    aspects: List[Dict]
    nakshatras: Dict

class BirthChartUpdate(BirthChartBase):
    pass

class BirthChart(BirthChartBase):
    id: UUID4
    user_id: Optional[UUID4]
    planetary_positions: Dict
    houses: Dict
    aspects: List[Dict]
    nakshatras: Dict
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
