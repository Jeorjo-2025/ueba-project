from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List


class EventCreate(BaseModel):
    timestamp: datetime
    user_id: str
    entity_id: Optional[str] = None
    event_type: str
    source_ip: Optional[str] = None
    geo_country: Optional[str] = None
    resource: Optional[str] = None
    event_metadata: Optional[dict] = None


class EventOut(EventCreate):
    id: int

    class Config:
        orm_mode = True


class DailyUserScoreOut(BaseModel):
    date: str
    user_id: str
    risk_score: float
    risk_level: str

    class Config:
        orm_mode = True


class HighRiskUser(BaseModel):
    user_id: str
    risk_score: float
    risk_level: str

    class Config:
        orm_mode = True
