# ── Imports ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from pydantic import Field, model_validator

from database.base_model import ModelBase
from database.db import get_connection

if TYPE_CHECKING:
    from database.models.recipe import Recipe

# ── Class Definition ────────────────────────────────────────────────────────────
class Ingredient(ModelBase):
    id: Optional[int] = None
    ingredient_name: str = Field(..., min_length=1, description="Name of the ingredient")
    ingredient_category: str = Field(..., min_length=1, description="Category of the ingredient")

    @model_validator(mode="before")
    def strip_strings(cls, values):
        # trim whitespace on string fields
        for fld in ("ingredient_name", "ingredient_category"):
            v = values.get(fld)
            if isinstance(v, str):
                values[fld] = v.strip()
        return values

    def display_label(self) -> str:
        """Return a human-friendly label for this ingredient."""
        return f"{self.ingredient_name} ({self.ingredient_category})"

    def get_recipes(self) -> List[Recipe]:
        """
        Traverse the recipe_ingredients join table to return all Recipes
        that include this ingredient.
        """
        conn = get_connection()
        rows = conn.execute(
            "SELECT recipe_id FROM recipe_ingredients WHERE ingredient_id = ?",
            (self.id,),
        ).fetchall()

        return [Recipe.get(row["recipe_id"]) for row in rows]
