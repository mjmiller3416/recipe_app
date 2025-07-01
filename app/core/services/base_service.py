"""Common utilities for service classes."""

from contextlib import contextmanager, nullcontext
from typing import Optional
import sqlite3

from app.core.data.database import get_connection


class BaseService:
    """Provide helpers shared by service classes."""

    @staticmethod
    @contextmanager
    def connection_ctx(conn: Optional[sqlite3.Connection] = None):
        """Yield a database connection, opening one if needed."""
        if conn is None:
            with get_connection() as managed:
                yield managed
        else:
            yield conn

