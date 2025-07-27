"""
app/core/services/session_manager.py

Provides a context manager for SQLAlchemy sessions,
ensuring commit, rollback, and closure are handled.
"""
from contextlib import contextmanager

from app.core.database.db import create_session
from dev_tools import DebugLogger


@contextmanager
def session_scope():
    """
    Provide a transactional scope around a series of operations.
    Commits on success, rolls back on exception, and always closes the session.
    """
    session = create_session()
    operation_count = getattr(session_scope, '_operation_count', 0) + 1
    setattr(session_scope, '_operation_count', operation_count)
    
    try:
        yield session
        session.commit()
        # Only log successful transactions periodically or for slow operations
        if operation_count % 50 == 0:  # Log every 50th transaction
            DebugLogger.log(f"Database operations: {operation_count} transactions completed", "debug")
    except Exception as e:
        session.rollback()
        DebugLogger.log("Database transaction failed, rolling back: {e}", "error")
        raise
    finally:
        session.close()