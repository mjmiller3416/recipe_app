""" services/recipe_service.py

This module provides the RecipeService class for transactional recipe operations.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
import sqlite3
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from database.db import get_connection
from database.models.ingredient import Ingredient
from database.models.recipe import Recipe
from database.models.recipe_ingredient import RecipeIngredient
from database.models.recipe_ingredient_detail import RecipeIngredientDetail

# ── Exceptions ──────────────────────────────────────────────────────────────────
class RecipeSaveError(Exception):
    """Raised when saving a recipe (and its ingredients) fails."""
    pass

class DuplicateRecipeError(Exception):
    """Raised when trying to save a recipe that already exists."""
    pass

# ── DTO for Ingredient Input ─────────────────────────────────────────────────────
class RecipeIngredientInputDTO(BaseModel):
    ingredient_name: str = Field(..., min_length=1)
    ingredient_category: str = Field(..., min_length=1)
    quantity: Optional[float] = None
    unit: Optional[str] = None

    @field_validator("ingredient_name", "ingredient_category", mode="before")
    def strip_strings(cls, v: str) -> str:
        return v.strip()

# ── Recipe Service Definition ───────────────────────────────────────────────────
class RecipeService:
    @staticmethod
    def list_all() -> List[Recipe]:
        """Return every recipe in creation-date order."""
        sql = "SELECT * FROM recipes ORDER BY created_at DESC"
        return Recipe.raw_query(sql)

    @staticmethod
    def get(recipe_id: int) -> Optional[Recipe]:
        """Fetch a single recipe or None by ID."""
        return Recipe.get(recipe_id)

    @staticmethod
    def recent(days: int = 30) -> List[Recipe]:
        """Recipes created in the last *n* days."""
        sql = (
            "SELECT * FROM recipes "
            "WHERE DATE(created_at) >= DATE('now', ? || ' days') "
            "ORDER BY created_at DESC"
        )
        return Recipe.raw_query(sql, params=(-days,))

    @staticmethod
    def create_recipe_with_ingredients(
        recipe_data: dict,
        ingredients: List[RecipeIngredientInputDTO],
    ) -> Recipe:
        """
        Atomically create a recipe plus all ingredient links.
        """
        # Check for duplicate recipe name
        if Recipe.exists(
        recipe_name=recipe_data["recipe_name"],
        recipe_category=recipe_data["recipe_category"]
        ):
            raise DuplicateRecipeError(f"Recipe '{recipe_data['recipe_name']}' already exists.")

        try:
            with get_connection() as conn:
                # Validate and save recipe
                recipe = Recipe.model_validate(recipe_data)
                recipe.save(connection=conn)

                # Process each ingredient DTO
                for ing in ingredients:
                    # Try to find existing ingredient
                    existing = Ingredient.get_by_field(
                        ingredient_name=ing.ingredient_name,
                        ingredient_category=ing.ingredient_category,
                    )
                    if existing:
                        ingredient = existing
                    else:
                        ingredient = Ingredient(
                            ingredient_name=ing.ingredient_name,
                            ingredient_category=ing.ingredient_category,
                        ).save(connection=conn)

                    # Link ingredient to recipe
                    RecipeIngredient(
                        recipe_id=recipe.id,
                        ingredient_id=ingredient.id,
                        quantity=ing.quantity,
                        unit=ing.unit,
                    ).save(connection=conn)

                return recipe
            
        except sqlite3.Error as db_err:
            # any constraint violation, disk full, etc. bubbles in here
            raise RecipeSaveError(
                f"Unable to save recipe '{recipe_data.get('recipe_name')}'"
            ) from db_err
        
    @staticmethod
    def get_ingredient_details(recipe_id: int) -> List[RecipeIngredientDetail]:
        """
        Return flattened ingredient details for a recipe.
        """
        sql = """
        SELECT
          i.ingredient_name,
          i.ingredient_category,
          ri.quantity,
          ri.unit
        FROM recipe_ingredients ri
        JOIN ingredients i ON ri.ingredient_id = i.id
        WHERE ri.recipe_id = ?
        """
        return RecipeIngredientDetail.raw_query(sql, (recipe_id,))

    @staticmethod
    def toggle_favorite(recipe_id: int) -> Recipe:
        """Flip the is_favorite flag and persist."""
        recipe = Recipe.get(recipe_id)
        if not recipe:
            raise ValueError(f"No recipe with id={recipe_id}")
        recipe.is_favorite = not recipe.is_favorite
        recipe.save()
        return recipe

    @staticmethod
    def list_filtered(
        category: str | None = None,
        sort_by: str | None = None
    ) -> list[Recipe]:
        # 1) filter via SQL if category is truthy & not “All”
        if category and category != "All":
            recs = Recipe.filter(recipe_category=category)
        else:
            recs = RecipeService.list_all()

        # 2) then sort in‐memory, based on your sort keys
        match sort_by:
            case "Name ↑":
                recs.sort(key=lambda r: r.recipe_name.lower())
            case "Name ↓":
                recs.sort(key=lambda r: r.recipe_name.lower(), reverse=True)
            case "Newest":
                recs.sort(key=lambda r: r.created_at, reverse=True)
            case "Oldest":
                recs.sort(key=lambda r: r.created_at)
            # …etc.

        return recs