# ── Imports ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

from pydantic import Field

from database.base_model import ModelBase


# ── Class Definition ────────────────────────────────────────────────────────────
class RecipeIngredientDetail(ModelBase):
    """
    A flattened view of one row from recipe_ingredients JOIN ingredients.
    """
    ingredient_name:     str   = Field(..., description="Name of the ingredient")
    ingredient_category: str   = Field(..., description="Category of the ingredient")
    quantity:            float | None = Field(None, description="Amount required")
    unit:                str   | None = Field(None, description="Unit for the amount")
