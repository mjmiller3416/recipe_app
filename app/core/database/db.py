"""app/core/database/db.py

Database connection and session management.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path
from typing import Generator

DB_PATH = Path(__file__).parent / "app_data.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine
)

def get_test_database_url() -> str:
    return "sqlite+pysqlite:///:memory:"


def get_session() -> Generator[Session, None, None]:
    """
    Dependency function to get a database session.
    
    Yields:
        Session: SQLAlchemy database session.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def create_session() -> Session:
    """
    Create a new database session.
    
    Returns:
        Session: New SQLAlchemy database session.
        
    Note:
        Remember to close the session when done:
        session = create_session()
        try:
            # use session
        finally:
            session.close()
    """
    return SessionLocal()