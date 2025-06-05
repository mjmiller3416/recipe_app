""" service/dtos/recipe_dtos.py

This module defines data transfer objects (DTOs) for recipe-related operations.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


# ── DTOs for Recipe Operations ──────────────────────────────────────────────────
class RecipeIngredientInputDTO(BaseModel):
    ingredient_name: str = Field(..., min_length=1)
    ingredient_category: str = Field(..., min_length=1)
    quantity: Optional[float] = None
    unit: Optional[str] = None

    @field_validator("ingredient_name", "ingredient_category", mode="before")
    def strip_strings(cls, v: str) -> str:
        return v.strip()

class RecipeCreateDTO(BaseModel):
    recipe_name: str = Field(..., min_length=1)
    recipe_category: str = Field(..., min_length=1)
    meal_type: str = Field(default="Dinner", min_length=1)
    total_time: Optional[int] = None
    servings: Optional[int] = None
    directions: Optional[str] = None
    ingredients: List[RecipeIngredientInputDTO] = []

class RecipeFilterDTO(BaseModel):
    recipe_category: Optional[str] = None
    meal_type: Optional[str] = None
    sort_by: Optional[str] = None
    favorites_only: bool = False