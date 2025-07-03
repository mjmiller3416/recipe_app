"""conftest.py

Provides reusable fixtures for test database setup.
"""

# ── Imports ─────────────────────────────────────────────────────────
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database.base import Base
from app.core.database.db import get_test_database_url
from app.core.repos.ingredient_repo import IngredientRepo


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
    """Provide a new Session for each test function."""
    # Ensure a clean database state for every test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()
