"""app/core/features/recipes/repository.py

Repository layer for Recipe model. Handles all direct database interactions
related to recipes, including related ingredients and history.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from datetime import datetime
from typing import List, Optional
from sqlalchemy import func

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select

from ..models.recipe import Recipe
from ..models.recipe_history import RecipeHistory


# ── RecipeRepository ────────────────────────────────────────────────────────────
class RecipeRepository:
    """Handles direct DB queries for the Recipe model."""

    def __init__(self, session: Session):
        self.session = session

    def get_all_recipes(self) -> List[Recipe]:
        """Returns all recipes with their ingredients (eager loaded)."""
        stmt = select(Recipe).options(joinedload(Recipe.ingredients))
        return self.session.scalars(stmt).all()

    def get_recipe_by_id(self, recipe_id: int) -> Optional[Recipe]:
        """Returns a single recipe by ID, with ingredients and history."""
        stmt = (
            select(Recipe)
            .options(
                joinedload(Recipe.ingredients),
                joinedload(Recipe.history),
            )
            .where(Recipe.id == recipe_id)
        )
        return self.session.scalars(stmt).first()

    def get_last_cooked_date(self, recipe_id: int) -> Optional[datetime]:
        """Returns the most recent cooked_at datetime for a recipe."""
        stmt = (
            select(RecipeHistory.cooked_at)
            .where(RecipeHistory.recipe_id == recipe_id)
            .order_by(RecipeHistory.cooked_at.desc())
            .limit(1)
        )
        result = self.session.execute(stmt).scalar_one_or_none()
        return result

    def create_recipe(self, recipe: Recipe) -> Recipe:
        """Adds and returns a new recipe."""
        self.session.add(recipe)
        self.session.commit()
        self.session.refresh(recipe)
        return recipe

    def delete_recipe(self, recipe: Recipe) -> None:
        """Deletes the given recipe."""
        self.session.delete(recipe)
        self.session.commit()

    def recipe_exists(self, name: str, category: str) -> bool:
        """Check if a recipe exists with the same name and category (case-insensitive)."""
        return (
            self.session.query(Recipe)
            .filter(
                func.lower(Recipe.recipe_name) == name.strip().lower(),
                func.lower(Recipe.recipe_category) == category.strip().lower()
            )
            .first()
            is not None
    )