""" services/recipe_service.py

This module provides the RecipeService class for transactional recipe operations.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from sqlalchemy.orm import Session

from app.core.models.recipe import Recipe as LegacyRecipe

from app.core.data.models.recipe import Recipe as SARecipe
from app.core.data.models.ingredient import Ingredient as SAIngredient
from app.core.data.models.recipe_ingredient import RecipeIngredient as SARecipeIngredient
from app.core.dtos import (
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
class RecipeService:
    """Service class for transactional recipe operations."""
    
    @staticmethod
    def create_recipe_with_ingredients(
        session: Session,
        recipe_dto: RecipeCreateDTO,
    ) -> SARecipe:
        """Create a recipe and related ingredient links using ORM sessions."""

        # check for duplicates by name
        existing = session.query(SARecipe).filter_by(name=recipe_dto.recipe_name).first()
        if existing:
            raise DuplicateRecipeError(
                f"Recipe '{recipe_dto.recipe_name}' already exists."
            )

        recipe = SARecipe(
            name=recipe_dto.recipe_name,
            instructions=recipe_dto.directions,
        )

        for ing_dto in recipe_dto.ingredients:
            ingredient = None
            if getattr(ing_dto, "existing_ingredient_id", None):
                ingredient = session.get(SAIngredient, ing_dto.existing_ingredient_id)

            if ingredient is None:
                ingredient = IngredientService.get_or_create(session, ing_dto.ingredient_name)

            link = SARecipeIngredient(
                quantity=ing_dto.quantity,
                unit=ing_dto.unit,
            )
            link.ingredient = ingredient
            recipe.ingredients.append(link)

        session.add(recipe)
        session.commit()
        session.refresh(recipe)

        return recipe

    @staticmethod
    def toggle_favorite(recipe_id: int) -> LegacyRecipe:
        """
        Flip the is_favorite flag and persist.
        
        Args:
            recipe_id (int): The ID of the recipe to toggle.
        Returns:
            Recipe: The updated recipe object.
        Raises:
            ValueError: If no recipe with the given ID exists.
        """
        recipe = LegacyRecipe.get(recipe_id)
        if not recipe:
            raise ValueError(f"No recipe with id={recipe_id}")
        recipe.is_favorite = not recipe.is_favorite
        recipe.save()
        return recipe

    @staticmethod
    def list_filtered(
        filter_dto: RecipeFilterDTO
    ) -> list[LegacyRecipe]:
        """
        List all recipes, applying optional filters and sorting.

        Args:
            filter_dto (RecipeFilterDTO): DTO containing filter criteria.
        Returns:
            list[Recipe]: List of filtered and sorted Recipe objects.
        """
        recs = LegacyRecipe.list_all()

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