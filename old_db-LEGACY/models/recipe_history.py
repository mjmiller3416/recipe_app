""" app/core/models/recipe_history.py

Recipe History model for tracking when recipes were cooked.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from app.core.database.base import ModelBase
from pydantic import Field

if TYPE_CHECKING:
    from app.core.features.recipes.recipe_model import Recipe

# ── Class Definition ────────────────────────────────────────────────────────────
class RecipeHistory(ModelBase):
    id: Optional[int]    = None
    recipe_id: int       = Field(..., ge=1)
    cooked_at: datetime  = Field(default_factory=datetime.now)

    def get_recipe(self) -> Recipe:
        from app.core.features.recipes.recipe_model import Recipe
        return Recipe.get(self.recipe_id)
