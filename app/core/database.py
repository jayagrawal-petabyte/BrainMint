from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.models.base import Base  # single shared Base for models, Alembic and tests

connect_args = {}
engine_kwargs = {"pool_pre_ping": True}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    # Keep the pool small: Supabase poolers have a connection cap.
    engine_kwargs.update(pool_size=5, max_overflow=5, pool_recycle=1800)

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

__all__ = ["Base", "engine", "SessionLocal", "get_db"]

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()