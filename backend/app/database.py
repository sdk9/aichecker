"""
SQLAlchemy database setup — SQLite for simplicity (swap DATABASE_URL for Postgres in prod).
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./veritasai.db")

# SQLite needs check_same_thread=False for FastAPI's thread pool
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables."""
    from app.models.user import User  # noqa: F401 — registers the model
    from app.models.page_view import PageView  # noqa: F401 — registers the model
    Base.metadata.create_all(bind=engine)
