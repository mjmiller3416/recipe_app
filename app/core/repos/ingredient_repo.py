"""app/core/repos/ingredient_repo.py

Provides database operations for Ingredient entities.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.ingredient import Ingredient


# ── Class Definition ────────────────────────────────────────────────────────────
class IngredientRepo:
    """Handles ingredient-specific database operations."""

    def __init__(self, session: Session):
        """Initialize with a SQLAlchemy session."""
        self.session = session

    # ── Basic CRUD ──────────────────────────────────────────────────────────────
    def get_all(self) -> list[Ingredient]:
        """Return all ingredients."""
        return self.session.execute(select(Ingredient)).scalars().unique().all()

    def get_by_id(self, ingredient_id: int) -> Ingredient | None:
        """Fetch a single ingredient by ID."""
        return self.session.get(Ingredient, ingredient_id)

    def delete(self, ingredient: Ingredient) -> None:
        """Delete the provided ingredient."""
        self.session.delete(ingredient)

    def add(self, ingredient: Ingredient) -> None:
        """Add a new ingredient to the session."""
        self.session.add(ingredient)

    # ── Custom Methods ──────────────────────────────────────────────────────────
    def find_by_name_category(self, name: str, category: str) -> Ingredient | None:
        """Return a single matching ingredient by name+category (case-insensitive)."""
        stmt = (
            select(Ingredient)
            .where(Ingredient.ingredient_name.ilike(name.strip()))
            .where(Ingredient.ingredient_category.ilike(category.strip()))
        )
        return self.session.execute(stmt).scalars().unique().first()

    def search_by_name(self, term: str, category: str | None = None) -> list[Ingredient]:
        """Search for ingredients with name containing a term (optionally filtered by category)."""
        stmt = select(Ingredient).where(Ingredient.ingredient_name.ilike(f"%{term.strip()}%"))
        if category:
            stmt = stmt.where(Ingredient.ingredient_category.ilike(category.strip()))
        return self.session.execute(stmt).scalars().unique().all()

    def get_distinct_names(self) -> list[str]:
        """Return a list of all unique ingredient names."""
        stmt = select(Ingredient.ingredient_name).distinct()
        results = self.session.execute(stmt).scalars().all()
        return results

    def get_or_create(self, dto) -> Ingredient:
        """Get existing ingredient or create new one based on name and category."""
        existing = self.find_by_name_category(dto.ingredient_name, dto.ingredient_category)
        if existing:
            return existing
        
        new_ingredient = Ingredient(
            ingredient_name=dto.ingredient_name,
            ingredient_category=dto.ingredient_category
        )
        self.add(new_ingredient)
        self.session.flush()  # Flush to get the ID
        return new_ingredient
