""" database/init_db.py

This module initializes or migrates the SQLite database by applying any pending SQL
"""


# ── Imports ─────────────────────────────────────────────────────────────────────
from pathlib import Path

from .db import get_connection

# ── Constants ───────────────────────────────────────────────────────────────────
MIGRATIONS_DIR = Path(__file__).parent / "migrations" # directory containing SQL migration files

# ── Private Methods ─────────────────────────────────────────────────────────────
def init_db():
    """
    Initialize or migrate the SQLite database by applying any pending SQL scripts
    in the migrations directory and recording them in the schema_version table.
    """
    # open one connection for the whole migration run
    with get_connection() as conn:
        # ensure the schema_version table exists
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_version (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT NOT NULL,
                applied_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        # fetch already applied migrations
        applied = {
            row["version"]
            for row in conn.execute("SELECT version FROM schema_version;").fetchall()
        }

        # collect and sort all migration files
        migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))

        for migration_file in migration_files:
            version = migration_file.name
            if version in applied:
                continue  # Skip already applied migrations

            # read and execute the SQL script
            sql = migration_file.read_text(encoding="utf-8")
            conn.executescript(sql)

            # record the applied migration
            conn.execute(
                "INSERT INTO schema_version (version) VALUES (?);",
                (version,),
            )
            print(f"Applied migration: {version}")

if __name__ == "__main__":
    init_db()
