# database/models/recipe_history.py

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from pydantic import Field

from database.base_model import ModelBase

if TYPE_CHECKING:
    from database.models.recipe import Recipe

class RecipeHistory(ModelBase):
    id: Optional[int]    = None
    recipe_id: int       = Field(..., ge=1)
    cooked_at: datetime  = Field(default_factory=datetime.now)

    def get_recipe(self) -> Recipe:
        from database.models.recipe import Recipe
        return Recipe.get(self.recipe_id)
