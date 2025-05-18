"""services/planner_service.py

Service module for managing MealPlanner state.

This includes saving and restoring open meal tabs, validating saved IDs, and
coordinating planner-wide session state. This module does not modify individual meals.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from typing import Optional

from core.helpers import DebugLogger
from database.models.meal_selection import MealSelection
from database.models.saved_meal_state import SavedMealState


# ── Class Definition ────────────────────────────────────────────────────────────
class PlannerService: 

    @staticmethod
    def load_saved_meal_ids() -> list[int]:
        """
        Load saved meal IDs from the database.

        Returns:
            list[int]: List of saved meal IDs.
        """
        meal_ids = [entry.meal_id for entry in SavedMealState.all()]
        DebugLogger.log(f"[PlannerService] Loaded saved meal IDs: {meal_ids}", "info")
        return meal_ids
    
    @staticmethod
    def save_active_meal_ids(meal_ids: list[int]) -> None:
        """
        Save the active meal IDs to the database.

        Args:
            meal_ids (list[int]): List of meal IDs to save.
        """
        SavedMealState.clear_all()
        for mid in meal_ids:
            SavedMealState(meal_id=mid).save()

    @staticmethod
    def clear_planner_state() -> None:
        """
        Clear all saved meal states from the database.
        """
        for entry in SavedMealState.all():
            entry.delete()

    @staticmethod
    def validate_meal_ids(meal_ids: list[int]) -> list[int]:
        """
        Validate the given meal IDs against the database.

        Args:
            meal_ids (list[int]): List of meal IDs to validate.

        Returns:
            list[int]: List of valid meal IDs.
        """
        valid_ids = []
        for mid in meal_ids:
            if MealSelection.get(mid):
                valid_ids.append(mid)
        return valid_ids