"""Common service utilities."""

from contextlib import contextmanager
from typing import Iterator, Optional
import sqlite3

from app.core.database.db import get_connection


class BaseService:
    """Provides shared DB connection context handling."""

    @staticmethod
    @contextmanager
    def connection_ctx(conn: Optional[sqlite3.Connection] = None) -> Iterator[sqlite3.Connection]:
        """Yield a database connection, opening one if necessary."""
        if conn is not None:
            yield conn
        else:
            with get_connection() as new_conn:
                yield new_conn

