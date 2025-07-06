"""
Refactored RecipeService using SQLAlchemy repository pattern.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.dtos.ingredient_dtos import IngredientCreateDTO
from app.core.dtos.recipe_dtos import (RecipeCreateDTO, RecipeFilterDTO,
                                       RecipeIngredientDTO)
from app.core.models.ingredient import Ingredient
from app.core.models.recipe import Recipe
from app.core.models.recipe_ingredient import RecipeIngredient
from app.core.repos.ingredient_repo import IngredientRepo
from app.core.repos.recipe_repo import RecipeRepo


# ── Exceptions ──────────────────────────────────────────────────────────────────
class RecipeSaveError(Exception):
    pass


class DuplicateRecipeError(Exception):
    pass


# ── Recipe Service Definition ───────────────────────────────────────────────────
class RecipeService:
    """Service layer for managing recipes and their ingredients."""

    def __init__(self, session: Session):
        self.session = session
        self.recipe_repo = RecipeRepo(session)
        self.ingredient_repo = IngredientRepo(session)

    def create_recipe_with_ingredients(self, recipe_dto: RecipeCreateDTO) -> Recipe:
        """
        Create a new recipe and its associated ingredients atomically.

        Args:
            recipe_dto (RecipeCreateDTO): Recipe input with ingredient data.

        Raises:
            DuplicateRecipeError: If recipe already exists.
            RecipeSaveError: If validation or database errors occur.

        Returns:
            Recipe: The newly created recipe.
        """
        if self.recipe_repo.recipe_exists(
            name=recipe_dto.recipe_name,
            category=recipe_dto.recipe_category
        ):
            raise DuplicateRecipeError(
                f"Recipe '{recipe_dto.recipe_name}' in category '{recipe_dto.recipe_category}' already exists."
            )

        try:
            recipe = Recipe(
                recipe_name=recipe_dto.recipe_name,
                recipe_category=recipe_dto.recipe_category,
                meal_type=recipe_dto.meal_type,
                total_time=recipe_dto.total_time,
                servings=recipe_dto.servings,
                directions=recipe_dto.directions,
                image_path=recipe_dto.image_path
            )
            self.session.add(recipe)
            self.session.flush()  # to assign recipe.id before linking ingredients

            for ing in recipe_dto.ingredients:
                ingredient = self._get_or_create_ingredient(ing)
                link = RecipeIngredient(
                    recipe_id=recipe.id,
                    ingredient_id=ingredient.id,
                    quantity=ing.quantity,
                    unit=ing.unit
                )
                self.session.add(link)

            self.session.commit()
            return recipe

        except SQLAlchemyError as err:
            self.session.rollback()
            raise RecipeSaveError(
                f"Unable to save recipe '{recipe_dto.recipe_name}': {err}"
            ) from err

    def _get_or_create_ingredient(
        self, ing_dto: RecipeIngredientDTO
    ) -> Ingredient:
        """
        Resolve or create an Ingredient from an ingredient DTO.

        Args:
            ing_dto (RecipeIngredientDTO)

        Returns:
            Ingredient
        """
        if ing_dto.existing_ingredient_id:
            return self.ingredient_repo.get_by_id(ing_dto.existing_ingredient_id)

        dto = IngredientCreateDTO(
            ingredient_name=ing_dto.ingredient_name,
            ingredient_category=ing_dto.ingredient_category,
            quantity=ing_dto.quantity,
            unit=ing_dto.unit,
        )
        return self.ingredient_repo.get_or_create(dto)

    def list_filtered(self, filter_dto: RecipeFilterDTO) -> list[Recipe]:
        return self.recipe_repo.filter_recipes(filter_dto)

    def toggle_favorite(self, recipe_id: int) -> Recipe:
        recipe = self.recipe_repo.get_by_id(recipe_id)
        recipe.is_favorite = not recipe.is_favorite
        self.session.commit()
        return recipe
