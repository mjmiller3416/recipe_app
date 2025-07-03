"""app/core/features/ingredients/ingredient_service.py

Provides services for ingredient management, including creation, searching, and retrieval.
Uses SQLAlchemy repository pattern for database interactions.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from sqlalchemy.orm import Session

from ..dtos.ingredient_dtos import IngredientCreateDTO,IngredientSearchDTO
from ..models.ingredient import Ingredient
from ..repos.ingredient_repo import IngredientRepo


# ── Ingredient Service ───────────────────────────────────────────────────────────────────────
class IngredientService:
    """Provides higher-level ingredient operations and DTO handling."""

    def __init__(self, session: Session):
        """Initialize the IngredientService with a database session and repository."""
        self.session = session
        self.repo = IngredientRepo(session)

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
