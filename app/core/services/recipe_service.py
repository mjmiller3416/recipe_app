"""app/core/services/recipe_service.py

RecipeService using SQLAlchemy repository pattern.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..dtos.recipe_dtos import RecipeCreateDTO, RecipeFilterDTO, RecipeIngredientDTO
from ..dtos.ingredient_dtos import IngredientCreateDTO
from ..models.recipe import Recipe
from ..models.ingredient import Ingredient
from ..repos.recipe_repo import RecipeRepo
from ..repos.ingredient_repo import IngredientRepo


# ── Exceptions ───────────────────────────────────────────────────────────────────────────────
class RecipeSaveError(Exception):
    pass

class DuplicateRecipeError(Exception):
    pass


# ── Recipe Service ───────────────────────────────────────────────────────────────────────────
class RecipeService:
    """Service layer for managing recipes and their ingredients."""

    def __init__(self, session: Session):
        """Initialize the RecipeService with database session and repositories."""
        self.session = session
        # ensure ingredient repository is created before passing into recipe repository
        self.ingredient_repo = IngredientRepo(session)
        self.recipe_repo = RecipeRepo(session, self.ingredient_repo)

    def create_recipe_with_ingredients(self, recipe_dto: RecipeCreateDTO) -> Recipe:
        if self.recipe_repo.recipe_exists(
            name=recipe_dto.recipe_name,
            category=recipe_dto.recipe_category
        ):
            raise DuplicateRecipeError(
                f"Recipe '{recipe_dto.recipe_name}' "
                f"in category '{recipe_dto.recipe_category}' already exists."
            )

        try:
            return self.recipe_repo.persist_recipe_and_links(recipe_dto)

        except SQLAlchemyError as err:
            self.recipe_repo.rollback()
            raise RecipeSaveError(
                f"Unable to save recipe '{recipe_dto.recipe_name}': {err}"
            ) from err

    def resolve_ingredient(
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
        """
        List recipes based on filter criteria.

        Args:
            filter_dto (RecipeFilterDTO): Filter criteria for recipes.

        Returns:
            list[Recipe]: List of recipes matching the filter.
        """
        return self.recipe_repo.filter_recipes(filter_dto)

    def toggle_favorite(self, recipe_id: int) -> Recipe:
        """
        Toggle the favorite status of a recipe.

        Args:
            recipe_id (int): ID of the recipe to toggle.

        Returns:
            Recipe: The updated recipe with new favorite status.
        """
        recipe = self.recipe_repo.toggle_favorite(recipe_id)
        return recipe
