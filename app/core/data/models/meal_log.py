""" database/models/meal_log.py

Meal Log model for logging meal selections.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from app.core.data.base_model import ModelBase
from pydantic import Field

if TYPE_CHECKING:
    from app.core.data.models.meal_selection import MealSelection

# ── Class Definition ────────────────────────────────────────────────────────────
class MealLog(ModelBase):
    """
    Logs each time a MealSelection was made (or checked off).
    """
    id: Optional[int] = None
    meal_selection_id: int = Field(..., ge=1)
    checked_at: datetime = Field(default_factory=datetime.now)

    def get_meal(self) -> MealSelection:
        from app.core.data.models.meal_selection import MealSelection
        return MealSelection.get(self.meal_selection_id)
