# ── Imports ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from app.core.data.base_model import ModelBase
from pydantic import Field

if TYPE_CHECKING:
    from app.core.models.recipe import Recipe

# ── Class Definition ────────────────────────────────────────────────────────────
class WeeklyMenu(ModelBase):
    id: Optional[int]      = None
    recipe_id: int         = Field(..., ge=1)
    added_at: datetime     = Field(default_factory=datetime.now)

    def get_recipe(self) -> Recipe:
        """Return the Recipe added to the weekly menu."""
        return Recipe.get(self.recipe_id)
