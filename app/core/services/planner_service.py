""" services/planner_service.py

Service module for managing MealPlanner state.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
import sqlite3
from typing import List, Optional

from app.core.data.database import get_connection
from app.core.data.models.meal_selection import MealSelection
from app.core.data.models.saved_meal_state import SavedMealState
from app.core.utils import DebugLogger


# ── Class Definition ────────────────────────────────────────────────────────────
class PlannerService:

    @staticmethod
    def load_saved_meal_ids(
        connection: Optional[sqlite3.Connection] = None
    ) -> List[int]:
        """
        Load saved meal IDs from the database.

        Returns:
            list[int]: List of saved meal IDs.
        """
        if connection:
            entries = SavedMealState.raw_query(
                f"SELECT * FROM {SavedMealState.table_name()}",
                (),
                connection=connection
            )
        else:
            entries = SavedMealState.all()

        meal_ids = [entry.meal_id for entry in entries]
        DebugLogger.log(f"[PlannerService] Loaded saved meal IDs: {meal_ids}", "info")
        return meal_ids

    @staticmethod
    def save_active_meal_ids(
        meal_ids: List[int],
        connection: Optional[sqlite3.Connection] = None
    ) -> None:
        """
        Save the active meal IDs to the database atomically.

        Args:
            meal_ids (list[int]): List of meal IDs to save.
        """
        if connection is None:
            with get_connection() as conn:
                PlannerService.save_active_meal_ids(meal_ids, connection=conn)
            return

        # Clear existing states
        connection.execute(f"DELETE FROM {SavedMealState.table_name()}")
        # Insert new states
        for mid in meal_ids:
            SavedMealState(meal_id=mid).save(connection=connection)
        DebugLogger.log(f"[PlannerService] Saved active meal IDs: {meal_ids}", "info")

    @staticmethod
    def clear_planner_state(
        connection: Optional[sqlite3.Connection] = None
    ) -> None:
        """
        Clear all saved meal states from the database.
        """
        if connection is None:
            with get_connection() as conn:
                PlannerService.clear_planner_state(connection=conn)
            return

        connection.execute(f"DELETE FROM {SavedMealState.table_name()}")
        DebugLogger.log("[PlannerService] Cleared planner state.", "info")

    @staticmethod
    def validate_meal_ids(
        meal_ids: List[int]
    ) -> List[int]:
        """
        Validate the given meal IDs against the database.

        Returns:
            list[int]: List of valid meal IDs.
        """
        valid_ids = []
        for mid in meal_ids:
            if MealSelection.get(mid):
                valid_ids.append(mid)
        return valid_ids
