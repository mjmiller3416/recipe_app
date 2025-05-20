"""services/meal_service.py

Handles CRUD operations for individual MealSelection entries.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
import sqlite3
from typing import Optional

from core.helpers import DebugLogger
from database.db import get_connection
from database.models.meal_selection import MealSelection


# ── Class Definition ────────────────────────────────────────────────────────────
class MealService:

    @staticmethod
    def create_meal(
        meal: MealSelection,
        connection: Optional[sqlite3.Connection] = None
    ) -> MealSelection:
        """
        Create and persist a new MealSelection to the database.

        Args:
            meal (MealSelection): Unsaved model instance (meal.id should be None)
            connection (Optional[sqlite3.Connection]): An existing DB connection.

        Returns:
            MealSelection: Saved instance with assigned ID
        """
        if meal.id is not None:
            raise ValueError("Cannot create a meal that already has an ID.")

        if connection is None:
            with get_connection() as conn:
                return MealService.create_meal(meal, connection=conn)

        # Within a transaction, save and log
        meal.save(connection=connection)
        DebugLogger.log(f"[MealService] Created new meal: {meal}", "success")
        return meal

    @staticmethod
    def update_meal(
        meal: MealSelection,
        connection: Optional[sqlite3.Connection] = None
    ) -> None:
        """
        Update an existing MealSelection in the database.

        Args:
            meal (MealSelection): Model instance with valid ID
            connection (Optional[sqlite3.Connection]): An existing DB connection.
        """
        if meal.id is None:
            raise ValueError("Cannot update a meal without an ID.")

        if connection is None:
            with get_connection() as conn:
                return MealService.update_meal(meal, connection=conn)

        # Within a transaction, patch fields and log
        MealSelection.update(
            meal.id,
            meal_name=meal.meal_name,
            main_recipe_id=meal.main_recipe_id,
            side_recipe_1=meal.side_recipe_1,
            side_recipe_2=meal.side_recipe_2,
            side_recipe_3=meal.side_recipe_3,
            connection=connection
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
