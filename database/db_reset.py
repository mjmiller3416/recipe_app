"""database/db_reset.py

Handles database reset operations for MealGenie.
"""

import os
import sys
from pathlib import Path

from database.db import DB_PATH
from database.init_db import init_db
from core.helpers import DebugLogger


def reset_database():
    """Reset the SQLite database using migration files."""
    DebugLogger().log("Resetting database...", "warning")

    # 1. Delete existing DB
    if DB_PATH.exists():
        DB_PATH.unlink()
        DebugLogger().log(f"Deleted old database at {DB_PATH}", "info")
    else:
        DebugLogger().log("No existing database found to delete.", "info")

    # 2. Run migrations
    init_db()

    DebugLogger().log("Database reset complete. 💾\n", "success")
    sys.exit(0)
