import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.data.sqlalchemy_base import Base

engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(scope="function")
def db_session() -> Session:
    """Provide a transactional scope around a series of operations."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
