"""app/core/features/recipes/repo.py

Repository layer for Recipe model. Handles all direct database interactions
related to recipes, including related ingredients and history.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from datetime import datetime
from typing import List, Optional
from sqlalchemy import func

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select

from ..models.recipe import Recipe
from ..models.recipe_history import RecipeHistory


# ── Recipe Repository ────────────────────────────────────────────────────────────────────────
class RecipeRepo:
    """Handles direct DB queries for the Recipe model."""

    def __init__(self, session: Session):
        """Initialize Recipe Repository with a database session."""
        self.session = session

    def get_all_recipes(self) -> List[Recipe]:
        """
        Returns all recipes with their ingredients (eager loaded).

        Returns:
            List[Recipe]: A list of all recipes with their ingredients loaded.
        """
        stmt = select(Recipe).options(joinedload(Recipe.ingredients))
        return self.session.scalars(stmt).unique().all()

    def get_recipe_by_id(self, recipe_id: int) -> Optional[Recipe]:
        """
        Returns a single recipe by ID, with ingredients and history.

        Args:
            recipe_id (int): The ID of the recipe to retrieve.

        Returns:
            Optional[Recipe]: The recipe with the given ID, or None if not found.
        """
        stmt = (
            select(Recipe)
            .options(
                joinedload(Recipe.ingredients),
                joinedload(Recipe.history),
            )
            .where(Recipe.id == recipe_id)
        )
        return self.session.scalars(stmt).unique().first()

    def get_by_id(self, recipe_id: int) -> Optional[Recipe]:
        """
        Get a recipe by ID (alias for get_recipe_by_id).
        Args:
            recipe_id (int): The ID of the recipe to retrieve.
            
        Returns:
            Optional[Recipe]: The recipe with the given ID, or None if not found.
        """
        return self.get_recipe_by_id(recipe_id)

    def get_last_cooked_date(self, recipe_id: int) -> Optional[datetime]:
        """
        Returns the most recent cooked_at datetime for a recipe.
        
        Args:
            recipe_id (int): The ID of the recipe to check.
            
        Returns:
            Optional[datetime]: The last cooked date, or None if no history exists.
        """
        stmt = (
            select(RecipeHistory.cooked_at)
            .where(RecipeHistory.recipe_id == recipe_id)
            .order_by(RecipeHistory.cooked_at.desc())
            .limit(1)
        )
        result = self.session.execute(stmt).scalar_one_or_none()
        return result

    def create_recipe(self, recipe: Recipe) -> Recipe:
        """
        Adds and returns a new recipe.
        
        Args:
            recipe (Recipe): The recipe instance to add.
            
        Returns:
            Recipe: The newly created recipe with ID and other defaults set.
        """
        self.session.add(recipe)
        self.session.commit()
        self.session.refresh(recipe)
        return recipe

    def delete_recipe(self, recipe: Recipe) -> None:
        """
        Deletes the given recipe.
        
        Args:
            recipe (Recipe): The recipe instance to delete.
            
        """
        self.session.delete(recipe)
        self.session.commit()

    def recipe_exists(self, name: str, category: str) -> bool:
        """
        Check if a recipe exists with the same name and category (case-insensitive).
        Args:
            name (str): The name of the recipe.
            category (str): The category of the recipe.

        Returns:
            bool: True if a recipe with the same name and category exists, False otherwise.
        """
        return (
            self.session.query(Recipe)
            .filter(
                func.lower(Recipe.recipe_name) == name.strip().lower(),
                func.lower(Recipe.recipe_category) == category.strip().lower()
            )
            .first()
            is not None
    )

    def filter_recipes(self, filter_dto) -> List[Recipe]:
        """
        Filter recipes based on criteria (placeholder implementation).

        Args:
            filter_dto: DTO containing filter criteria.

        Returns:
            List[Recipe]: List of recipes matching the filter criteria.
        """
        # for now, just return all recipes - implement filtering logic as needed
        return self.get_all_recipes()