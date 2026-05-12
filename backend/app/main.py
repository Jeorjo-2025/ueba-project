from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from .database import Base, engine, get_db
from . import models, schemas

# create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="UEBA API", version="0.1.0")


@app.get("/")
def root():
    """
    Health check endpoint.
    """
    return {"message": "UEBA API is running"}


@app.post("/events", response_model=schemas.EventOut)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    """
    Ingest a single UEBA event.
    """
    db_event = models.Event(
    timestamp=event.timestamp,
    user_id=event.user_id,
    entity_id=event.entity_id,
    event_type=event.event_type,
    source_ip=event.source_ip,
    geo_country=event.geo_country,
    resource=event.resource,
    event_metadata=event.event_metadata,
)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


@app.post("/jobs/score/{date}")
def compute_daily_scores(date: str, db: Session = Depends(get_db)):
    """
    Very simple scoring job:
    - For each user on a given date,
      risk_score = min(100, number_of_events * 10)
    - risk_level based on score.
    """
    # get all events for that date
    start = datetime.fromisoformat(date + "T00:00:00")
    end = datetime.fromisoformat(date + "T23:59:59")

    events = (
        db.query(models.Event)
        .filter(models.Event.timestamp >= start, models.Event.timestamp <= end)
        .all()
    )

    # count events per user
    counts = {}
    for e in events:
        counts[e.user_id] = counts.get(e.user_id, 0) + 1

    # create scores
    for user_id, count in counts.items():
        score = min(100, count * 10)
        if score >= 70:
            level = "high"
        elif score >= 40:
            level = "medium"
        else:
            level = "low"

        db_score = models.DailyUserScore(
            date=date, user_id=user_id, risk_score=score, risk_level=level
        )
        db.add(db_score)

    db.commit()
    return {"status": "ok", "scored_users": len(counts)}


@app.get("/score/user/{user_id}", response_model=schemas.DailyUserScoreOut)
def get_user_score(user_id: str, date: str, db: Session = Depends(get_db)):
    """
    Get a user's risk score for a given date.
    """
    score = (
        db.query(models.DailyUserScore)
        .filter(
            models.DailyUserScore.user_id == user_id,
            models.DailyUserScore.date == date,
        )
        .first()
    )
    if not score:
        return {"date": date, "user_id": user_id, "risk_score": 0.0, "risk_level": "low"}
    return score


@app.get("/alerts/high-risk", response_model=List[schemas.HighRiskUser])
def get_high_risk_users(date: str, min_score: float = 70, db: Session = Depends(get_db)):
    """
    List users with risk_score >= min_score for a given date.
    """
    scores = (
        db.query(models.DailyUserScore)
        .filter(
            models.DailyUserScore.date == date,
            models.DailyUserScore.risk_score >= min_score,
        )
        .all()
    )
    return [
        schemas.HighRiskUser(
            user_id=s.user_id, risk_score=s.risk_score, risk_level=s.risk_level
        )
        for s in scores
    ]
