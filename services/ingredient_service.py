"""service/ingredient_service.py

Service class for managing ingredients.
Provides methods to retrieve, create, and validate ingredients.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
import sqlite3
from typing import Optional

from database.db import get_connection
from database.models.ingredient import Ingredient

# ── Class Definition ────────────────────────────────────────────────────────────
class IngredientService:
    """
    Service class for managing ingredients.
    Provides methods to retrieve, create, and validate ingredients with transactional support.
    """

    @staticmethod
    def list_all_ingredient_names(
        connection: Optional[sqlite3.Connection] = None
    ) -> list[str]:
        """Returns a list of all distinct ingredient names."""
        sql = "SELECT DISTINCT ingredient_name FROM ingredients"
        results = Ingredient.raw_query(sql, (), connection=connection)
        return [r.ingredient_name for r in results]

    @staticmethod
    def find_matching_ingredients(
        query: str,
        connection: Optional[sqlite3.Connection] = None
    ) -> list[Ingredient]:
        """Returns a list of Ingredient objects matching the query."""
        sql = "SELECT * FROM ingredients WHERE ingredient_name LIKE ?"
        param = f"%{query}%"
        return Ingredient.raw_query(sql, (param,), connection=connection)

    @staticmethod
    def get_or_create_ingredient(
        name: str,
        category: str,
        connection: Optional[sqlite3.Connection] = None
    ) -> Ingredient:
        """Returns an existing ingredient or creates a new one within a transaction."""
        if connection is None:
            with get_connection() as conn:
                return IngredientService.get_or_create_ingredient(name, category, connection=conn)

        # Look for existing ingredient in same transaction
        sql = (
            "SELECT * FROM ingredients "
            "WHERE ingredient_name = ? AND ingredient_category = ?"
        )
        existing = Ingredient.raw_query(sql, (name, category), connection=connection)
        if existing:
            return existing[0]

        # Create new ingredient record
        return Ingredient(
            ingredient_name=name,
            ingredient_category=category
        ).save(connection=connection)

    @staticmethod
    def build_payload_from_widget(widget) -> dict:
        """
        Extracts and formats data from an IngredientWidget instance
        into a payload compatible with create_recipe_with_ingredients().
        """
        return {
            "ingredient_name": widget.le_ingredient_name.text().strip(),
            "ingredient_category": widget.cb_ingredient_category.currentText().strip(),
            "unit": widget.cb_unit.currentText().strip(),
            "quantity": float(widget.le_quantity.text().strip() or 0)
        }
