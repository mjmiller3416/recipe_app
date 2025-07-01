""" database/models/recipe.py

This module defines the Recipe class, which represents a recipe in the database.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, List, Optional

from pydantic import Field, model_validator
from app.core.utils.validators import strip_string_values

from app.core.data.base_model import ModelBase
from app.core.data.database import get_connection
from app.core.data.models.ingredient import Ingredient
from app.core.data.models.recipe_ingredient import (IngredientDetail,
                                                    RecipeIngredient)

if TYPE_CHECKING:
    from app.core.data.models.ingredient import Ingredient

# ── Recipe Model Definition ─────────────────────────────────────────────────────
class Recipe(ModelBase):
    id: Optional[int]         = None
    recipe_name: str          = Field(..., min_length=1)
    recipe_category: str      = Field(..., min_length=1)
    meal_type: str        = Field(default="Dinner", min_length=1)
    total_time: Optional[int] = None
    servings: Optional[int]   = None
    directions: Optional[str] = None
    image_path: Optional[str] = None
    created_at: datetime      = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_favorite: bool         = Field(default=False)

    @model_validator(mode="before")
    def strip_strings(cls, values):
        values = strip_string_values(
            values,
            ("recipe_name", "recipe_category", "meal_type", "image_path"),
        )
        if isinstance(values.get("directions"), str):
            values["directions"] = values["directions"].strip("\n ")
        return values

    @classmethod
    def recent(cls, days: int = 30) -> List[Recipe]:
        """
        Recipes created in the last *n* days.
        
        Args:
            days (int): Number of days to look back for recent recipes.
        Returns:
            List[Recipe]: List of recipes created in the last `days` days.
        """
        sql = (
            "SELECT * FROM recipes "
            "WHERE DATE(created_at) >= DATE('now', ? || ' days') "
            "ORDER BY created_at DESC"
        )
        return Recipe.raw_query(sql, params=(-days,))

    @classmethod  
    def list_all(cls) -> List[Recipe]:
        """
        Return every recipe in creation-date order.
        
        Returns:
            List[Recipe]: List of all recipes ordered by creation date.
        """
        sql = "SELECT * FROM recipes ORDER BY created_at DESC"
        return Recipe.raw_query(sql)

    @classmethod
    def suggest(cls, days: int) -> List[Recipe]:
        """
        Return all recipes whose last_cooked is None or older than `days` ago.

        Args:
            days (int): Number of days to consider for suggesting recipes.
        Returns:
            List[Recipe]: List of recipes that have not been cooked in the last `days` days.
        """
        cutoff = datetime.now() - timedelta(days=days)
        return [r for r in cls.all() if (last := r.last_cooked()) is None or last <= cutoff]

    def formatted_time(self) -> str:
        """Return total_time formatted as "Xh Ym" or "Ym" if less than 1 hour."""
        if not self.total_time:
            return ""
        hrs, mins = divmod(self.total_time, 60)
        return f"{hrs}h {mins}m" if hrs else f"{mins}m"
    
    def formatted_servings(self) -> str:
        """Return servings with label."""
        return f"{self.servings}" if self.servings else ""

    def get_recipe_ingredients(
        self,
        connection: Optional[sqlite3.Connection] = None
    ) -> List[RecipeIngredient]:
        """
        Return all RecipeIngredient link objects for this recipe.
        
        Args:
            connection (Optional[sqlite3.Connection]): Optional database connection.
        Returns:
            List[RecipeIngredient]: List of RecipeIngredient models for this recipe.
        """
        if not self.id:
            raise ValueError("Recipe must be saved before fetching ingredients.")
        sql = (
            "SELECT * FROM recipe_ingredients WHERE recipe_id = ?"
        )
        return RecipeIngredient.raw_query(sql, (self.id,), connection=connection)

    def get_ingredients(
        self,
        connection: Optional[sqlite3.Connection] = None
    ) -> List[Ingredient]:
        """
        Return all Ingredient models linked to this recipe.
        
        Args:
            connection (Optional[sqlite3.Connection]): Optional database connection.
        Returns:
            List[Ingredient]: List of Ingredient models for this recipe.
        """
        links = self.get_recipe_ingredients(connection=connection)
        return [Ingredient.get(link.ingredient_id) for link in links]

    def last_cooked(
        self,
        connection: Optional[sqlite3.Connection] = None
    ) -> Optional[datetime]:
        """
        Return the last time this recipe was cooked, or None if never cooked.

        Args:
            connection (Optional[sqlite3.Connection]): Optional database connection.
        Returns:
            Optional[datetime]: The last cooked datetime, or None if never cooked.
        """
        sql = (
            "SELECT MAX(cooked_at) AS last FROM recipe_histories"
            " WHERE recipe_id = ?"
        )

        def _run(conn: sqlite3.Connection) -> Optional[datetime]:
            row = conn.execute(sql, (self.id,)).fetchone()
            last = row["last"] if row else None
            return datetime.fromisoformat(last) if last else None

        if connection:
            return _run(connection)
        with get_connection() as conn:
            return _run(conn)

    def get_directions_list(self) -> list[str]:
        """Return each non-empty line as a step."""
        if not self.directions:
            return []
        return [line.strip() for line in self.directions.splitlines() if line.strip()]

    def get_ingredient_details(
            self, 
            connection: Optional[sqlite3.Connection] = None
    ) -> List[IngredientDetail]:
        """
        Get ingredient details using the consolidated approach.
        
        Args:
            connection (Optional[sqlite3.Connection]): Optional database connection.
        Returns:
            List[IngredientDetail]: List of ingredient details for this recipe.
        """
        recipe_ingredients = self.get_recipe_ingredients(connection)
        return [ri.get_ingredient_detail() for ri in recipe_ingredients]