"""app/core/features/ingredients/ingredient_service.py

Provides services for ingredient management, including creation, searching, and retrieval.
Uses SQLAlchemy repository pattern for database interactions.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..dtos.ingredient_dtos import (
    IngredientCreateDTO,
    IngredientUpdateDTO,
    IngredientSearchDTO,
)
from ..models.ingredient import Ingredient
from ..repos.ingredient_repo import IngredientRepo


# ── Ingredient Service ───────────────────────────────────────────────────────────────────────
class IngredientService:
    """Provides higher-level ingredient operations and DTO handling."""

    def __init__(self, session: Session):
        """Initialize the IngredientService with a database session and repository."""
        self.session = session
        self.repo = IngredientRepo(session)

    # ------------------------------------------------------------------
    # Additional helper methods used in tests
    # ------------------------------------------------------------------

    def get_all_ingredients(self) -> list[Ingredient]:
        return self.repo.get_all()

    def get_ingredient_by_id(self, ingredient_id: int) -> Ingredient | None:
        return self.repo.get_by_id(ingredient_id)

    def create_ingredient(self, dto: IngredientCreateDTO) -> Ingredient:
        return self.repo.get_or_create(dto)

    def update_ingredient(self, ingredient_id: int, dto) -> Ingredient | None:
        ingredient = self.repo.get_by_id(ingredient_id)
        if not ingredient:
            return None
        if getattr(dto, "ingredient_name", None):
            ingredient.ingredient_name = dto.ingredient_name
        if getattr(dto, "ingredient_category", None):
            ingredient.ingredient_category = dto.ingredient_category
        self.session.commit()
        self.session.refresh(ingredient)
        return ingredient

    def delete_ingredient(self, ingredient_id: int) -> bool:
        ingredient = self.repo.get_by_id(ingredient_id)
        if not ingredient:
            return False
        self.repo.delete(ingredient)
        self.session.commit()
        return True

    def search_ingredients(self, term: str, category: str | None = None) -> list[Ingredient]:
        return self.repo.search_by_name(term, category)

    def get_or_create_ingredient(self, name: str, category: str) -> Ingredient:
        dto = IngredientCreateDTO(ingredient_name=name, ingredient_category=category)
        return self.repo.get_or_create(dto)

    def get_ingredients_by_category(self, category: str) -> list[Ingredient]:
        return self.repo.search_by_name("", category)

    def get_ingredient_categories(self) -> list[str]:
        stmt = select(Ingredient.ingredient_category).distinct()
        return [row[0] for row in self.session.execute(stmt).all()]

    def bulk_create_ingredients(self, dtos: list[IngredientCreateDTO]) -> list[Ingredient]:
        created = [self.repo.get_or_create(dto) for dto in dtos]
        self.session.commit()
        return created

    def get_or_create(self, dto: IngredientCreateDTO) -> Ingredient:
        """
        Retrieve an existing ingredient or create one if it doesn't exist.

        Args:
            dto (IngredientCreateDTO): Ingredient data

        Returns:
            Ingredient: The existing or newly created instance
        """
        existing = self.repo.find_by_name_category(
            name=dto.ingredient_name,
            category=dto.ingredient_category,
        )
        if existing:
            return existing

        new_ingredient = Ingredient(
            ingredient_name=dto.ingredient_name.strip(),
            ingredient_category=dto.ingredient_category.strip(),
        )
        self.repo.add(new_ingredient)
        self.session.flush()  # ensure ID is assigned if needed immediately
        return new_ingredient

    def search(self, dto: IngredientSearchDTO) -> list[Ingredient]:
        """
        Search for ingredients using DTO input.

        Args:
            dto (IngredientSearchDTO): Search criteria including term and category.

        Returns:
            list[Ingredient]: List of matching ingredients.
        """
        return self.repo.search_by_name(
            term=dto.search_term,
            category=dto.category,
        )

    def list_distinct_names(self) -> list[str]:
        """
        Return all unique ingredient names (for search/autocomplete).

        Returns:
            list[str]: List of distinct ingredient names.
        """
        return self.repo.get_distinct_names()

    def get_all(self) -> list[Ingredient]:
        """
        Return all ingredients in the database.

        Returns:
            list[Ingredient]: List of all ingredients.
        """
        return self.repo.get_all()
