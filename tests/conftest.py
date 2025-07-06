"""conftest.py

Provides reusable fixtures for test database setup.
"""

# ── Imports ─────────────────────────────────────────────────────────
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database.base import Base

# ── Test Database URL ───────────────────────────────────────────────
TEST_DB_URL = "sqlite+pysqlite:///:memory:"  # fast and isolated


# ── Pytest Fixture: Engine + Session ────────────────────────────────
@pytest.fixture(scope="session")
def engine():
    """Create test engine + schema once per test session."""
    engine = create_engine(TEST_DB_URL, echo=False, future=True)
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def session(engine):
    """Provide a clean test database session for each test function."""
    # reset schema to ensure isolation between tests
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
