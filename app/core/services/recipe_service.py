""" services/recipe_service.py

This module provides the RecipeService class for transactional recipe operations.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
import sqlite3

from pydantic import ValidationError

from .base_service import BaseService
from app.core.models.ingredient import Ingredient
from app.core.models.recipe import Recipe
from app.core.models.recipe_ingredient import RecipeIngredient
from app.core.dtos import (
    IngredientCreateDTO,
    RecipeCreateDTO,
    RecipeFilterDTO,
    RecipeIngredientInputDTO,
)
from app.core.services.ingredient_service import IngredientService


# ── Exceptions ──────────────────────────────────────────────────────────────────
class RecipeSaveError(Exception):
    """Raised when saving a recipe (and its ingredients) fails."""
    pass

class DuplicateRecipeError(Exception):
    """Raised when trying to save a recipe that already exists."""
    pass

# ── Recipe Service Definition ───────────────────────────────────────────────────
class RecipeService(BaseService):
    """Service class for transactional recipe operations."""
    
    @staticmethod
    def create_recipe_with_ingredients(
        recipe_dto: RecipeCreateDTO,  # Use the DTO instead of raw dict
    ) -> Recipe:
        """
        Atomically create a recipe plus all ingredient links.

        Args:
            recipe_dto (RecipeCreateDTO): DTO containing recipe and ingredient data.
        Returns:
            Recipe: The created recipe object.
        Raises:
            DuplicateRecipeError: if a recipe with the same name+category already exists.
            RecipeSaveError: if any validation or database error occurs.
        """
        # 1) Check for duplicate recipe before opening the transaction
        if Recipe.exists(
            recipe_name=recipe_dto.recipe_name,
            recipe_category=recipe_dto.recipe_category
        ):
            raise DuplicateRecipeError(
                f"Recipe '{recipe_dto.recipe_name}' in category '{recipe_dto.recipe_category}' already exists."
            )

        try:
            # 2) Open a single connection/transaction
            with RecipeService.connection_ctx() as conn:
                # 3) Convert DTO → model, validate & save the recipe itself
                #    model_dump(exclude={"ingredients"}) returns a dict that matches Recipe fields
                recipe_data = recipe_dto.model_dump(exclude={"ingredients"})
                recipe = Recipe.model_validate(recipe_data)
                recipe.save(connection=conn)

                # 4) Loop through each ingredient in the DTO, 
                #    build an IngredientCreateDTO, and get_or_create via IngredientService
                for ing_dto in recipe_dto.ingredients:
                    if getattr(ing_dto, "existing_ingredient_id", None):
                        ingredient = Ingredient.get(ing_dto.existing_ingredient_id)
                    else:
                        try:
                            ing_create_dto = IngredientCreateDTO(
                                ingredient_name=ing_dto.ingredient_name,
                                ingredient_category=ing_dto.ingredient_category,
                                quantity=ing_dto.quantity,
                                unit=ing_dto.unit,
                            )
                        except ValidationError as ve:
                            raise RecipeSaveError(
                                f"Invalid ingredient data for '{ing_dto.ingredient_name}': {ve}"
                            ) from ve

                        ingredient = IngredientService.get_or_create_ingredient(
                            ing_create_dto,
                            conn=conn
                        )

                    RecipeIngredient(
                        recipe_id=recipe.id,
                        ingredient_id=ingredient.id,
                        quantity=ing_dto.quantity,
                        unit=ing_dto.unit,
                    ).save(connection=conn)

                # 6) Return the newly created Recipe model
                return recipe

        except (ValidationError, sqlite3.Error) as err:
            # Wrap both Pydantic validation errors and SQLite errors
            raise RecipeSaveError(
                f"Unable to save recipe '{recipe_dto.recipe_name}': {err}"
            ) from err

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
        filter_dto: RecipeFilterDTO
    ) -> list[Recipe]:
        """
        List all recipes, applying optional filters and sorting.

        Args:
            filter_dto (RecipeFilterDTO): DTO containing filter criteria.
        Returns:
            list[Recipe]: List of filtered and sorted Recipe objects.
        """
        recs = Recipe.list_all()

        # apply recipe category filter
        if filter_dto.recipe_category and filter_dto.recipe_category != "All":
            recs = [r for r in recs if r.recipe_category == filter_dto.recipe_category]

        # apply meal category filter
        if filter_dto.meal_type and filter_dto.meal_type != "All":
            recs = [r for r in recs if r.meal_type == filter_dto.meal_type]
        
        # apply favorites filter
        if filter_dto.favorites_only:
            recs = [r for r in recs if r.is_favorite]

        # apply sorting
        match filter_dto.sort_by:
            case "A-Z":
                recs.sort(key=lambda r: r.recipe_name.lower())
            case "Z-A":
                recs.sort(key=lambda r: r.recipe_name.lower(), reverse=True)

        return recs