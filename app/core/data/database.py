"""database/db.py

Database connection manager for SQLite.
"""

import contextlib
# ── Imports ─────────────────────────────────────────────────────────────────────
import sqlite3
from pathlib import Path

from app.core.dev_tools import DebugLogger

# ── Constants ───────────────────────────────────────────────────────────────────
DB_PATH = Path(__file__).parent / "app_data.db"

# ── Public Methods ──────────────────────────────────────────────────────────────
@contextlib.contextmanager
def get_connection():
    """
    Context manager for SQLite connections.

    Yields:
        sqlite3.Connection: A DB connection with row_factory set to sqlite3.Row.

    Commits the transaction on success, rolls back on exception, and always closes.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()
