""" services/recipe_service.py

This module provides the RecipeService class for transactional recipe operations.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
import sqlite3

from database.db import get_connection
from database.models.ingredient import Ingredient
from database.models.recipe import Recipe
from database.models.recipe_ingredient import RecipeIngredient
from services.dtos.recipe_dtos import RecipeCreateDTO


# ── Exceptions ──────────────────────────────────────────────────────────────────
class RecipeSaveError(Exception):
    """Raised when saving a recipe (and its ingredients) fails."""
    pass

class DuplicateRecipeError(Exception):
    """Raised when trying to save a recipe that already exists."""
    pass

# ── Recipe Service Definition ───────────────────────────────────────────────────
class RecipeService:
    """Service class for transactional recipe operations."""
    @staticmethod
    def create_recipe_with_ingredients(
        recipe_dto: RecipeCreateDTO,  # Use the DTO instead of dict
    ) -> Recipe:
        """
        Atomically create a recipe plus all ingredient links.

        Args:
            recipe_dto (RecipeCreateDTO): DTO containing recipe and ingredient data.
        Returns:
            Recipe: The created recipe object.
        """
        # check if recipe already exists
        if Recipe.exists(
            recipe_name=recipe_dto.recipe_name,
            recipe_category=recipe_dto.recipe_category
        ):
            raise DuplicateRecipeError(f"Recipe '{recipe_dto.recipe_name}' already exists.")

        try:
            with get_connection() as conn:
                # convert DTO to model and save recipe
                recipe_data = recipe_dto.model_dump(exclude={'ingredients'})
                recipe = Recipe.model_validate(recipe_data)
                recipe.save(connection=conn)

                # process each ingredient
                for ing in recipe_dto.ingredients:
                    # check if ingredient already exists
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

                    # link ingredient to recipe
                    RecipeIngredient(
                        recipe_id=recipe.id,
                        ingredient_id=ingredient.id,
                        quantity=ing.quantity,
                        unit=ing.unit,
                    ).save(connection=conn)

                return recipe
                
        except sqlite3.Error as db_err:
            # raise custom error with context
            raise RecipeSaveError(
                f"Unable to save recipe '{recipe_dto.recipe_name}'" 
            ) from db_err

    @staticmethod
    def toggle_favorite(recipe_id: int) -> Recipe:
        """
        Flip the is_favorite flag and persist.
        
        Args:
            recipe_id (int): The ID of the recipe to toggle.
        Returns:
            Recipe: The updated recipe object.
        Raises:
            ValueError: If no recipe with the given ID exists.
        """
        recipe = Recipe.get(recipe_id)
        if not recipe:
            raise ValueError(f"No recipe with id={recipe_id}")
        recipe.is_favorite = not recipe.is_favorite
        recipe.save()
        return recipe

    @staticmethod
    def list_filtered(
        recipe_category: str | None = None,
        meal_type: str | None = None,
        sort_by: str | None = None,
        favorites_only: bool = False
    ) -> list[Recipe]:
        """
        List recipes filtered by category, sorted, and optionally favorited.
        Args:
            category (str | None): Category to filter by, or None for all.
            sort_by (str | None): Sort order, e.g. "A-Z", "Z-A".
            favorites_only (bool): If True, only return favorite recipes.
        Returns:
            list[Recipe]: List of filtered and sorted recipes.
        """
        recs = Recipe.list_all()

        # apply recipe category filter
        if recipe_category and recipe_category != "All":
            recs = [r for r in recs if r.recipe_category == recipe_category]

        # apply meal category filter
        if meal_type and meal_type != "All":
            recs = [r for r in recs if r.meal_type == meal_type]
        
        # apply favorites filter
        if favorites_only:
            recs = [r for r in recs if r.is_favorite]

        # apply sorting
        match sort_by:
            case "A-Z":
                recs.sort(key=lambda r: r.recipe_name.lower())
            case "Z-A":
                recs.sort(key=lambda r: r.recipe_name.lower(), reverse=True)

        return recs