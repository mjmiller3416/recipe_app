""" service/dtos/recipe_dtos.py

This module defines data transfer objects (DTOs) for recipe-related operations.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from typing import Optional, List
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
    meal_category: str = Field(default="Dinner", min_length=1)
    instructions: Optional[str] = None
    prep_time: Optional[int] = None
    cook_time: Optional[int] = None
    servings: Optional[int] = None
    ingredients: List[RecipeIngredientInputDTO] = []

class RecipeFilterDTO(BaseModel):
    category: Optional[str] = None
    meal_category: Optional[str] = None
    sort_by: Optional[str] = None
    favorites_only: bool = False