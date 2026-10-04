"""
SQLite connection. The database file (pulselens.db) and its table are created
automatically the first time the server starts.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.utils.paths import DB_PATH

engine = create_engine(
    f"sqlite:///{DB_PATH.as_posix()}",
    connect_args={"check_same_thread": False},  # needed for SQLite + FastAPI
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def init_db():
    """Create all tables if they do not exist yet."""
    from app.models import measurement  # noqa: F401  (registers the table)
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency: gives each request its own DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()