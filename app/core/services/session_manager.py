"""
app/core/services/session_manager.py

Provides a context manager for SQLAlchemy sessions,
ensuring commit, rollback, and closure are handled.
"""
from contextlib import contextmanager
from app.core.database.db import create_session

@contextmanager
def session_scope():
    """
    Provide a transactional scope around a series of operations.
    Commits on success, rolls back on exception, and always closes the session.
    """
    session = create_session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()