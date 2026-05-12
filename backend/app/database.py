from sqlalchemy import create_engine  # creates DB engine
from sqlalchemy.orm import sessionmaker, declarative_base  # session + base class

# SQLite DB file in local folder
SQLALCHEMY_DATABASE_URL = "sqlite:///./ueba.db"

# connect_args needed for SQLite when using relative path
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# each request will use a DB session from this factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


def get_db():
    """
    Dependency for FastAPI routes:
    yields a DB session and closes it after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
