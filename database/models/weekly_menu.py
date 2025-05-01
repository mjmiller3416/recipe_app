# ── Imports ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from pydantic import Field

from database.base_model import ModelBase

if TYPE_CHECKING:
    from database.models.recipe import Recipe

# ── Class Definition ────────────────────────────────────────────────────────────
class WeeklyMenu(ModelBase):
    id: Optional[int]      = None
    recipe_id: int         = Field(..., ge=1)
    added_at: datetime     = Field(default_factory=datetime.now)

    def get_recipe(self) -> Recipe:
        """Return the Recipe added to the weekly menu."""
        return Recipe.get(self.recipe_id)
