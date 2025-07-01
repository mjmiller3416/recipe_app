""" services/planner_service.py

Service module for managing MealPlanner state.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
import sqlite3
from typing import List, Optional

from app.core.data.database import get_connection
from app.core.data.models.meal_selection import MealSelection
from app.core.data.models.saved_meal_state import SavedMealState
from app.core.dev_tools import DebugLogger


# ── Class Definition ────────────────────────────────────────────────────────────
class PlannerService:

    @staticmethod
    def load_saved_meal_ids(
        conn: Optional[sqlite3.Connection] = None
    ) -> List[int]:
        """
        Load saved meal IDs from the database.

        Returns:
            list[int]: List of saved meal IDs.
        """
        if conn:
            entries = SavedMealState.raw_query(
                f"SELECT * FROM {SavedMealState.table_name()}",
                (),
                connection=conn
            )
        else:
            entries = SavedMealState.all()

        meal_ids = [entry.meal_id for entry in entries]
        DebugLogger.log(f"[PlannerService] Loaded saved meal IDs: {meal_ids}", "info")
        return meal_ids

    @staticmethod
    def save_active_meal_ids(
        meal_ids: List[int],
        conn: Optional[sqlite3.Connection] = None
    ) -> None:
        """
        Save the active meal IDs to the database atomically.

        Args:
            meal_ids (list[int]): List of meal IDs to save.
        """
        if conn is None:
            with get_connection() as db_conn:
                PlannerService.save_active_meal_ids(meal_ids, conn=db_conn)
            return

        # Clear existing states
        conn.execute(f"DELETE FROM {SavedMealState.table_name()}")
        # Insert new states
        for mid in meal_ids:
            SavedMealState(meal_id=mid).save(connection=conn)
        DebugLogger.log(f"[PlannerService] Saved active meal IDs: {meal_ids}", "info")

    @staticmethod
    def clear_planner_state(
        conn: Optional[sqlite3.Connection] = None
    ) -> None:
        """
        Clear all saved meal states from the database.
        """
        if conn is None:
            with get_connection() as db_conn:
                PlannerService.clear_planner_state(conn=db_conn)
            return
        conn.execute(f"DELETE FROM {SavedMealState.table_name()}")
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

