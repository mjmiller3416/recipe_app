# database/models/meal_log.py

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from pydantic import Field

from database.base_model import ModelBase

if TYPE_CHECKING:
    from database.models.meal_selection import MealSelection

class MealLog(ModelBase):
    """
    Logs each time a MealSelection was made (or checked off).
    """
    id: Optional[int] = None
    meal_selection_id: int = Field(..., ge=1)
    checked_at: datetime = Field(default_factory=datetime.now)

    def get_meal(self) -> MealSelection:
        from database.models.meal_selection import MealSelection
        return MealSelection.get(self.meal_selection_id)
