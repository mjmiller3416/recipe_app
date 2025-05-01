# database/services/recipe_service.py

from typing import List
from database.db import get_connection
from database.models.recipe import Recipe
from database.models.ingredient import Ingredient
from database.models.recipe_ingredient import RecipeIngredient

def create_recipe_with_ingredients(
    recipe_data: dict,
    ingredients: List[dict]  # each dict: {"ingredient_name", "ingredient_category", "quantity", "unit"}
) -> Recipe:
    """
    Atomically create a Recipe, its Ingredients (or get existing),
    and the RecipeIngredient join rows.
    """
    # Use a single connection/transaction
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 1) Save the recipe core
        recipe = Recipe.model_validate(recipe_data).save()

        # 2) For each ingredient, get_or_create then join
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

            # 3) Create join
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
