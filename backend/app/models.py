from sqlalchemy import Column, Integer, String, DateTime, JSON, Float
from datetime import datetime
from .database import Base

class Event(Base):
    """
    Raw UEBA event: login, file access, etc.
    """
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    user_id = Column(String, index=True)
    entity_id = Column(String, nullable=True)
    event_type = Column(String, index=True)
    source_ip = Column(String, nullable=True)
    geo_country = Column(String, nullable=True)
    resource = Column(String, nullable=True)
    event_metadata = Column(JSON, nullable=True)


class DailyUserScore(Base):
    """
    Simple daily risk score per user.
    """
    __tablename__ = "daily_user_scores"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, index=True)  # store as 'YYYY-MM-DD'
    user_id = Column(String, index=True)
    risk_score = Column(Float)  # 0–100
    risk_level = Column(String)  # low / medium / high
