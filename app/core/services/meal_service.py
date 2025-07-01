"""services/meal_service.py

Handles CRUD operations for individual MealSelection entries.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
import sqlite3
from typing import Optional

from .base_service import BaseService
from app.core.models.meal_selection import MealSelection
from dev_tools import DebugLogger


# ── Class Definition ────────────────────────────────────────────────────────────
class MealService(BaseService):

    @staticmethod
    def create_meal(
        meal: MealSelection,
        conn: Optional[sqlite3.Connection] = None
    ) -> MealSelection:
        """
        Create and persist a new MealSelection to the database.

        Args:
            meal (MealSelection): Unsaved model instance (meal.id should be None)
            conn (Optional[sqlite3.Connection]): An existing DB connection.

        Returns:
            MealSelection: Saved instance with assigned ID
        """
        if meal.id is not None:
            raise ValueError("Cannot create a meal that already has an ID.")

        with MealService.connection_ctx(conn) as db:
            meal.save(connection=db)
            DebugLogger.log(f"[MealService] Created new meal: {meal}", "success")
            return meal

    @staticmethod
    def update_meal(
        meal: MealSelection,
        conn: Optional[sqlite3.Connection] = None
    ) -> None:
        """
        Update an existing MealSelection in the database.

        Args:
            meal (MealSelection): Model instance with valid ID
            conn (Optional[sqlite3.Connection]): An existing DB connection.
        """
        if meal.id is None:
            raise ValueError("Cannot update a meal without an ID.")

        with MealService.connection_ctx(conn) as db:
            MealSelection.update(
                meal.id,
                meal_name=meal.meal_name,
                main_recipe_id=meal.main_recipe_id,
                side_recipe_1=meal.side_recipe_1,
                side_recipe_2=meal.side_recipe_2,
                side_recipe_3=meal.side_recipe_3,
                connection=db,
            )
            DebugLogger.log(f"[MealService] Updated meal: {meal}", "info")

    @staticmethod
    def load_meal(meal_id: int) -> Optional[MealSelection]:
        """
        Load a MealSelection from the database by ID.

        Args:
            meal_id (int): ID of the meal to load

        Returns:
            MealSelection or None: Loaded model or None if not found
        """
        meal = MealSelection.get(meal_id)

        if not meal:
            DebugLogger.log(f"[MealService] No meal found with ID: {meal_id}", "warning")
            return None

        DebugLogger.log(f"[MealService] Loaded meal: {meal}", "info")
        return meal
