# ── Imports ─────────────────────────────────────────────────────────────────────
from typing import List

from database.db import get_connection
from database.models.ingredient import Ingredient
from database.models.recipe import Recipe
from database.models.recipe_ingredient import RecipeIngredient


# ── Public Methods ──────────────────────────────────────────────────────────────
def create_recipe_with_ingredients(
    recipe_data: dict,
    ingredients: List[dict]  # each dict: {"ingredient_name", "ingredient_category", "quantity", "unit"}
) -> Recipe:
    """
    Atomically create a Recipe, its Ingredients (or get existing),
    and the RecipeIngredient join rows.
    """
    # use a single connection/transaction
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # ── Save Recipe ──
        recipe = Recipe.model_validate(recipe_data).save()

        # ── Get Each Ingredient ──
        for ing in ingredients:
            # check if ingredient already exists
            existing = conn.execute(
                "SELECT id FROM ingredients WHERE ingredient_name = ? AND ingredient_category = ?",
                (ing["ingredient_name"], ing["ingredient_category"])
            ).fetchone()

            if existing:
                ingredient_id = existing["id"]
            else:
                ingredient = Ingredient(
                    ingredient_name=ing["ingredient_name"],
                    ingredient_category=ing["ingredient_category"]
                ).save()
                ingredient_id = ingredient.id

            # ── Create Join ──
            RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ingredient_id,
                quantity=ing.get("quantity"),
                unit=ing.get("unit")
            ).save()

        conn.commit()
        return recipe

    except Exception:
        conn.rollback()
        raise
