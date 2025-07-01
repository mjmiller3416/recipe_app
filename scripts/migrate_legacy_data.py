"""scripts/migrate_legacy_data.py

Migrate legacy MealGenie data to the SQLAlchemy 2.0 schema.
"""

# ── Imports ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import argparse
import sqlite3
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.data.models import Base, Ingredient, Recipe, RecipeIngredient

# ── Helper Functions ───────────────────────────────────────────────────────────

def open_old_db(path: Path) -> sqlite3.Connection:
    """Open a read-only connection to the legacy SQLite DB."""
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def create_session(db_path: Path) -> Session:
    """Create a SQLAlchemy session bound to `db_path`."""
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    return Session(engine)


def migrate_ingredients(old_conn: sqlite3.Connection, session: Session) -> dict[int, Ingredient]:
    """Migrate all ingredients and return a map of old ID to new model."""
    ingredient_map: dict[int, Ingredient] = {}
    rows = old_conn.execute("SELECT id, ingredient_name FROM ingredients").fetchall()

    for row in rows:
        name = row["ingredient_name"].strip()
        ingredient = Ingredient(name=name)
        session.add(ingredient)
        ingredient_map[row["id"]] = ingredient
    session.commit()
    return ingredient_map


def migrate_recipes(old_conn: sqlite3.Connection, session: Session) -> dict[int, Recipe]:
    """Migrate recipes and return a map of old ID to new model."""
    recipe_map: dict[int, Recipe] = {}
    rows = old_conn.execute(
        "SELECT id, recipe_name, directions, created_at FROM recipes"
    ).fetchall()

    for row in rows:
        created_at = None
        if row["created_at"]:
            try:
                created_at = datetime.fromisoformat(row["created_at"])
            except ValueError:
                created_at = datetime.utcnow()
        recipe = Recipe(
            name=row["recipe_name"].strip(),
            instructions=row["directions"],
            created_at=created_at,
        )
        session.add(recipe)
        recipe_map[row["id"]] = recipe
    session.commit()
    return recipe_map


def migrate_recipe_ingredients(
    old_conn: sqlite3.Connection,
    session: Session,
    recipe_map: dict[int, Recipe],
    ingredient_map: dict[int, Ingredient],
    batch_size: int = 100,
) -> None:
    """Migrate join table entries in batches."""
    rows = old_conn.execute(
        "SELECT recipe_id, ingredient_id, quantity, unit FROM recipe_ingredients"
    ).fetchall()

    for idx, row in enumerate(rows, start=1):
        recipe = recipe_map.get(row["recipe_id"])
        ingredient = ingredient_map.get(row["ingredient_id"])
        if not recipe or not ingredient:
            continue
        link = RecipeIngredient(quantity=row["quantity"], unit=row["unit"])
        link.recipe = recipe
        link.ingredient = ingredient
        session.add(link)
        if idx % batch_size == 0:
            session.commit()
    session.commit()


# ── Main Script ────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate legacy database")
    parser.add_argument("--old-db", type=Path, default=Path("app/core/data/app_data.db"))
    parser.add_argument("--new-db", type=Path, default=Path("app/core/data/sa_app_data.db"))
    args = parser.parse_args()

    old_conn = open_old_db(args.old_db)
    session = create_session(args.new_db)

    try:
        ingredient_map = migrate_ingredients(old_conn, session)
        recipe_map = migrate_recipes(old_conn, session)
        migrate_recipe_ingredients(old_conn, session, recipe_map, ingredient_map)
    finally:
        old_conn.close()
        session.close()


if __name__ == "__main__":
    main()
