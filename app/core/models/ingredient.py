""" database/models/ingredient.py

Ingredient model for the recipe database."""

# ── Imports ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING, List, Optional

from pydantic import Field, model_validator
from app.core.utils.validators import strip_string_values

from app.core.data.base_model import ModelBase

if TYPE_CHECKING:
    from app.core.models.recipe import Recipe

# ── Class Definition ────────────────────────────────────────────────────────────
class Ingredient(ModelBase):
    id: Optional[int] = None
    ingredient_name: str = Field(..., min_length=1, description="Name of the ingredient")
    ingredient_category: str = Field(..., min_length=1, description="Category of the ingredient")

    @model_validator(mode="before")
    def strip_strings(cls, values):
        return strip_string_values(values, ("ingredient_name", "ingredient_category"))

    def display_label(self) -> str:
        """Return a human-friendly label for this ingredient."""
        return f"{self.ingredient_name} ({self.ingredient_category})"

    def get_recipes(
        self,
        connection: Optional[sqlite3.Connection] = None
    ) -> List[Recipe]:
        """
        Return all Recipes that include this ingredient.
        """
        sql = (
            "SELECT recipes.* "
            "FROM recipes "
            "JOIN recipe_ingredients ON recipes.id = recipe_ingredients.recipe_id "
            "WHERE recipe_ingredients.ingredient_id = ?"
        )
        return Recipe.raw_query(sql, (self.id,), connection=connection)

