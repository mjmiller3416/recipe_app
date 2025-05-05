"""services/recipe_service.py

This module provides functions to interact with the recipe database.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from typing import List

from database.db import get_connection
from database.models.ingredient import Ingredient
from database.models.recipe import Recipe
from database.models.recipe_ingredient import RecipeIngredient


# ── Query Helpers ───────────────────────────────────────────────────────────────
def list_all() -> list[Recipe]:
    """Return every recipe in creation-date order."""
    return Recipe.all(order_by="created_at DESC")


def get(recipe_id: int) -> Recipe | None:
    """Fetch a single recipe or None."""
    return Recipe.get(recipe_id)


def recent(days: int = 30) -> list[Recipe]:
    """Recipes created in the last *n* days."""
    sql = (
        "SELECT * FROM recipes "
        "WHERE DATE(created_at) >= DATE('now', ? || ' days') "
        "ORDER BY created_at DESC"
    )
    return Recipe.raw_query(sql, params=(-days,))

# ── Transactional Helpers ───────────────────────────────────────────────────────
def create_recipe_with_ingredients(
    recipe_data: dict,
    ingredients: List[dict],
) -> Recipe:
    """
    Atomically create a recipe plus all ingredient links.
    Uses the new context-managed connection so the whole
    operation is one tidy transaction.
    """
    # get connection
    with get_connection() as conn:             
        # save recipe
        recipe = Recipe.model_validate(recipe_data).save(conn)

        # insert ingredients
        for ing in ingredients:
            # try existing first
            row = conn.execute(
                """
                SELECT id FROM ingredients
                WHERE ingredient_name = ? AND ingredient_category = ?
                """,
                (ing["ingredient_name"], ing["ingredient_category"]),
            ).fetchone()

            if row:
                ingredient_id = row["id"]
            else:
                ingredient = Ingredient(
                    ingredient_name=ing["ingredient_name"],
                    ingredient_category=ing["ingredient_category"],
                ).save(conn)
                ingredient_id = ingredient.id

            RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ingredient_id,
                quantity=ing.get("quantity"),
                unit=ing.get("unit"),
            ).save(conn)

        # commit transaction
        return recipe
