# database/models/meal_selection.py
from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from pydantic import Field, model_validator

from database.base_model import ModelBase

if TYPE_CHECKING:
    from database.models.recipe import Recipe

class MealSelection(ModelBase):
    id: Optional[int]         = None
    meal_name: str            = Field(..., min_length=1)
    main_recipe_id: int       = Field(..., ge=1)
    side_recipe_1: Optional[int] = None
    side_recipe_2: Optional[int] = None
    side_recipe_3: Optional[int] = None

    @model_validator(mode="before")
    def strip_strings(cls, values):
        name = values.get("meal_name")
        if isinstance(name, str):
            values["meal_name"] = name.strip()
        return values

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
