
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
    conn = get_connection()
    cursor = conn.cursor()

    # ensure the schema_version table exists
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_version (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT NOT NULL,
            applied_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.commit()

    # fetch already applied migrations
    cursor.execute("SELECT version FROM schema_version;")
    applied = {row[0] for row in cursor.fetchall()}

    # collect and sort all migration files
    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))

    for migration_file in migration_files:
        version = migration_file.name
        if version in applied:
            continue  # Skip already applied migrations

        # read and execute the SQL script
        sql = migration_file.read_text(encoding="utf-8")
        cursor.executescript(sql)
        conn.commit()

        # record the applied migration
        cursor.execute(
            "INSERT INTO schema_version (version) VALUES (?);",
            (version,)
        )
        conn.commit()
        print(f"Applied migration: {version}")

    cursor.close()
    conn.close() # close the connection


if __name__ == "__main__":
    init_db()
