"""database/models/saved_meal_state.py

SavedMealState model for storing the state of saved meals in the database.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from typing import List

from app.core.data.base_model import ModelBase
from app.core.dev_tools import DebugLogger


# ── Class Definition ────────────────────────────────────────────────────────────
class SavedMealState(ModelBase):
    meal_id: int

    @classmethod
    def all(cls) -> list["SavedMealState"]:
        """
        Fetch all saved meal states from the database.
        
        Returns:
            list[SavedMealState]: List of all saved meal states.
        """
        rows = super().all()
        DebugLogger.log(f"[SavedMealState] Loaded {len(rows)} saved meal states", "info")
        return rows

    @classmethod
    def clear_all(cls) -> None:
        """
        Delete all entries from the saved meal state table.
        """
        for entry in cls.all():
            entry.delete()