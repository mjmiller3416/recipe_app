"""services/dtos/ingredient_dtos.py

This module defines the IngredientSearchDTO class for searching ingredients.
"""

from typing import Optional

# ── Imports ─────────────────────────────────────────────────────────────────────
from pydantic import BaseModel, Field, field_validator


# ── DTO for Ingredient Operations ───────────────────────────────────────────────
class IngredientSearchDTO(BaseModel):
    search_term: str = Field(..., min_length=1)
    category: Optional[str] = None

class IngredientCreateDTO(BaseModel):
    ingredient_name: str = Field(..., min_length=1)
    ingredient_category: str = Field(..., min_length=1)
    quantity: Optional[float] = None
    unit: Optional[str] = None

    @field_validator("ingredient_name", "ingredient_category", mode="before")
    def strip_strings(cls, v: str) -> str:
        return v.strip()