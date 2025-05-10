"""database/models/recipe.py

This module defines the Recipe class, which represents a recipe in the database.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, List, Optional

from pydantic import Field, model_validator

from database.base_model import ModelBase
from database.db import get_connection
from database.models.recipe_ingredient import RecipeIngredient
from database.models.recipe_ingredient_detail import RecipeIngredientDetail

if TYPE_CHECKING:
    from database.models.ingredient import Ingredient

# ── Class Definition ────────────────────────────────────────────────────────────
class Recipe(ModelBase):
    id: Optional[int] = None
    recipe_name: str = Field(..., min_length=1)
    recipe_category: str = Field(..., min_length=1)
    total_time: Optional[int] = None
    servings: Optional[int] = None
    directions: Optional[str] = None
    image_path: Optional[str] = None

    @model_validator(mode="before")
    def strip_strings(cls, values):
        for fld in ("recipe_name","recipe_category","image_path"):
            v = values.get(fld)
            if isinstance(v, str):
                values[fld] = v.strip()
        # for directions: only trim at ends, but keep newlines inside
        if isinstance(values.get("directions"), str):
            values["directions"] = values["directions"].strip("\n ")
        return values

    @classmethod
    def suggest(cls, days: int) -> List[Recipe]:
        """
        Return all recipes whose last_cooked is None or older than `days` ago.
        """
        cutoff = datetime.now() - timedelta(days=days)
        suggestions: List[Recipe] = []
        for r in cls.all():
            last = r.last_cooked()
            if last is None or last <= cutoff:
                suggestions.append(r)
        return suggestions

    def formatted_time(self) -> str:
        if not self.total_time:
            return ""
        hrs, mins = divmod(self.total_time, 60)
        return f"{hrs}h {mins}m" if hrs else f"{mins}m"
    
    def formatted_servings(self) -> str:
        """Return servings with label."""
        return f"{self.servings}" if self.servings else ""

    def get_recipe_ingredients(self) -> List[RecipeIngredient]:
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM recipe_ingredients WHERE recipe_id = ?", (self.id,)
            ).fetchall()
            return [RecipeIngredient.model_validate(dict(r)) for r in rows]

    def get_ingredients(self) -> List[Ingredient]:
        # runtime import avoids circular import

        links = self.get_recipe_ingredients()
        return [Ingredient.get(link.ingredient_id) for link in links]

    def last_cooked(self) -> Optional[datetime]:
        """
        Return the most recent cooked_at timestamp for this recipe,
        or None if it’s never been cooked.
        """
        with get_connection() as conn:
            row = conn.execute(
                "SELECT MAX(cooked_at) AS last FROM recipe_histories WHERE recipe_id = ?",
                (self.id,),
            ).fetchone()

        last = row["last"] if row else None
        return datetime.fromisoformat(last) if last else None


    def get_directions_list(self) -> list[str]:
        """
        Return each non-empty line as a step.
        """
        if not self.directions:
            return []
        return [
            line.strip()
            for line in self.directions.splitlines()
            if line.strip()
        ]

    def get_ingredient_details(self) -> list[RecipeIngredientDetail]:
        """
        Fetch one 👀 on all ingredients for this recipe in a single JOIN
        (pulling name, category, quantity & unit).
        """

        sql = """
        SELECT
        i.ingredient_name,
        i.ingredient_category,
        ri.quantity,
        ri.unit
        FROM recipe_ingredients ri
        JOIN ingredients i
        ON ri.ingredient_id = i.id
        WHERE ri.recipe_id = ?
        """
        with get_connection() as conn:
            rows = conn.execute(sql, (self.id,)).fetchall()

        return [RecipeIngredientDetail.model_validate(dict(r)) for r in rows]
