# ── Imports ─────────────────────────────────────────────────────────────────────
import sqlite3
from pathlib import Path

# ── Constants ───────────────────────────────────────────────────────────────────
DB_PATH = Path(__file__).parent / "app_data.db"

# ── Public Methods ──────────────────────────────────────────────────────────────
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
