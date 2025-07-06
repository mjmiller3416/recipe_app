"""app/core/features/ingredients/ingredient_service.py

Provides services for ingredient management, including creation, searching, and retrieval.
Uses SQLAlchemy repository pattern for database interactions.
"""

from typing import List, Optional

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from sqlalchemy.orm import Session

from ..dtos.ingredient_dtos import (IngredientCreateDTO, IngredientSearchDTO,
                                    IngredientUpdateDTO)
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
    
    # ── Convenience Methods for Tests ─────────────────────────────────────────────────────
    def get_all_ingredients(self) -> List[Ingredient]:
        """Alias for get_all()."""
        return self.get_all()

    def get_ingredient_by_id(self, ingredient_id: int) -> Optional[Ingredient]:
        """Get a single ingredient by ID."""
        return self.repo.get_by_id(ingredient_id)

    def create_ingredient(self, create_dto: IngredientCreateDTO) -> Ingredient:
        """Create a new ingredient or return existing one, then commit."""
        ing = self.get_or_create(create_dto)
        self.session.commit()
        return ing

    def update_ingredient(self, ingredient_id: int, update_dto: IngredientUpdateDTO) -> Optional[Ingredient]:
        """Update an existing ingredient by ID."""
        ing = self.get_ingredient_by_id(ingredient_id)
        if not ing:
            return None
        if update_dto.ingredient_name is not None:
            ing.ingredient_name = update_dto.ingredient_name
        if update_dto.ingredient_category is not None:
            ing.ingredient_category = update_dto.ingredient_category
        self.session.commit()
        return ing

    def delete_ingredient(self, ingredient_id: int) -> bool:
        """Delete an ingredient by ID."""
        ing = self.get_ingredient_by_id(ingredient_id)
        if not ing:
            return False
        self.repo.delete(ing)
        self.session.commit()
        return True

    def search_ingredients(self, term: str, category: Optional[str] = None) -> List[Ingredient]:
        """Search ingredients by name and optional category."""
        return self.repo.search_by_name(term, category)

    def get_ingredients_by_category(self, category: str) -> List[Ingredient]:
        """Get ingredients filtered by category."""
        return self.repo.search_by_name("", category)

    def get_ingredient_categories(self) -> List[str]:
        """Return all unique ingredient categories."""
        cats = {ing.ingredient_category for ing in self.get_all() if ing.ingredient_category}
        return sorted(cats)

    def bulk_create_ingredients(self, create_dtos: List[IngredientCreateDTO]) -> List[Ingredient]:
        """Bulk create ingredients from DTOs."""
        created: List[Ingredient] = []
        for dto in create_dtos:
            created.append(self.create_ingredient(dto))
        return created

    def list_all_ingredient_names(self) -> List[str]:
        """
        Return all unique ingredient names for autocomplete or selection.
        """
        return self.repo.get_distinct_names()

    def find_matching_ingredients(self, dto: IngredientSearchDTO) -> List[Ingredient]:
        """
        Find ingredients matching the search DTO criteria.

        Args:
            dto (IngredientSearchDTO): DTO containing search_term and optional category.

        Returns:
            List[Ingredient]: List of matching Ingredient models.
        """
        return self.search(dto)

    def get_or_create_ingredient(self, name: str, category: str) -> Ingredient:
        """Get or create an ingredient by name and category."""
        dto = IngredientCreateDTO(
            ingredient_name=name,
            ingredient_category=category,
        )
        return self.get_or_create(dto)
