import os
import sqlite3

from core.helpers.qt_imports import QSettings

SCHEMA_VERSION = "1.0"  # Update this whenever you make changes to the schema

def reset_to_version(db_path, sql_file):
    try:
        print(f"Resetting database at {db_path} with schema {sql_file}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Drop all existing tables, including meal_selection
        print("Dropping all tables...")
        cursor.executescript("""
            DROP TABLE IF EXISTS recipes;
            DROP TABLE IF EXISTS ingredients;
            DROP TABLE IF EXISTS meal_selection;
            DROP TABLE IF EXISTS shopping_list;
            DROP TABLE IF EXISTS weekly_menu;
            DROP TABLE IF EXISTS recipe_ingredients;
            DROP TABLE IF EXISTS schema_version;
        """)
        conn.commit()
        print("All tables dropped.")

        # Reinitialize the database
        print("Reinitializing database...")
        initialize_database(db_path, sql_file)
        print(f"Database reset to version {SCHEMA_VERSION}.")
    except Exception as e:
        print(f"Error resetting database: {e}")
    finally:
        conn.close()

def reset_qsettings():
    settings = QSettings("MyCompany", "MealGenie")
    settings.clear()
    print("QSettings cleared.")

def initialize_database(db_path, sql_file):
    print("Initializing database...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print(f"Updating schema version to: {SCHEMA_VERSION}")
        print(f"Schema version updated to: {SCHEMA_VERSION}")

        # Create schema_version table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT NOT NULL,
                applied_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Check if the recipes table exists; if not, run the full script.
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='recipes'")
        table_exists = cursor.fetchone()

        if not table_exists:
            print("Recipes table missing. Reinitializing schema.")
            with open(sql_file, 'r') as file:
                sql_script = file.read()
            cursor.executescript(sql_script)
            conn.commit()

        # Check current schema version
        cursor.execute("SELECT version FROM schema_version ORDER BY applied_on DESC LIMIT 1")
        current_version = cursor.fetchone()
        print(f"Current schema version in database: {current_version}")

        if current_version and current_version[0] == SCHEMA_VERSION:
            print(f"Database is already at the latest schema version: {SCHEMA_VERSION}")
            return False  # No changes applied

        with open(sql_file, 'r') as file:
            sql_script = file.read()

        cursor.executescript(sql_script)
        conn.commit()

        if current_version:
            print(f"Upgrading database schema from version {current_version[0]} to {SCHEMA_VERSION}")
        else:
            print(f"Initializing database schema to version {SCHEMA_VERSION}")

        cursor.execute("INSERT INTO schema_version (version) VALUES (?)", (SCHEMA_VERSION,))
        conn.commit()

        print(f"Database updated to schema version: {SCHEMA_VERSION}")
        return True  # Changes applied

    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

    finally:
        conn.close()


if __name__ == "__main__":
    db_path = "app/database/app_data.db"
    sql_file = "app/database/db_tables.sql"
  
    # To reset the database (which now resets meal_selection as well)
    reset_to_version(db_path, sql_file)
    reset_qsettings()
