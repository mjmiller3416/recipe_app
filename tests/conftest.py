"""tests/conftest

Pytest fixtures for database setup."""

# ── Imports ─────────────────────────────────────────────────────────────────────
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.data.sqlalchemy_base import Base


# ── Fixtures ────────────────────────────────────────────────────────────────────
@pytest.fixture
def db_session() -> Session:
    """Provide a Session bound to an in-memory SQLite database."""
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
