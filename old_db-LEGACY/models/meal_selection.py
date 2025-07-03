""" app/core/models/meal_selection.py

Meal Selection model for selecting meals and their recipes.
"""
# ── Imports ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from pydantic import Field, model_validator
from app.core.utils.validators import strip_string_values

from app.core.database.base import ModelBase

if TYPE_CHECKING:
    from app.core.features.recipes.recipe_model import Recipe

# ── Class Definition ────────────────────────────────────────────────────────────
class MealSelection(ModelBase):
    id: Optional[int]         = None
    meal_name: str            = Field(..., min_length=1)
    main_recipe_id: int       = Field(..., ge=1)
    side_recipe_1: Optional[int] = None
    side_recipe_2: Optional[int] = None
    side_recipe_3: Optional[int] = None

    @model_validator(mode="before")
    def strip_strings(cls, values):
        return strip_string_values(values, ("meal_name",))

    def get_main_recipe(self) -> Recipe:
        """Return the primary Recipe for this meal."""
        return Recipe.get(self.main_recipe_id)

    def get_side_recipes(self) -> List[Recipe]:
        """Return any side dish Recipes for this meal."""
        sides = []
        for sid in (self.side_recipe_1, self.side_recipe_2, self.side_recipe_3):
            if sid is not None:
                sides.append(Recipe.get(sid))
        return sides

    def get_all_recipes(self) -> List[Recipe]:
        """Return all recipes (main and sides) for this meal."""
        return [self.get_main_recipe()] + self.get_side_recipes()