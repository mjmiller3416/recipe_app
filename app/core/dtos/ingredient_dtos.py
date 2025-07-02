"""app/core/features/ingredients/dtos.py

DTOs for ingredient-related operations.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from typing import NamedTuple


# ── Ingredient DTOs ──────────────────────────────────────────────────────────────────────────
class IngredientDetailDTO(NamedTuple): 
    ingredient_name: str
    ingredient_category: str
    quantity: Optional[float]
    unit: Optional[str]

class IngredientSearchDTO(BaseModel):
    """DTO for searching ingredients."""
    search_term: str = Field(..., min_length=1)
    category: Optional[str] = None


class IngredientCreateDTO(BaseModel):
    """DTO for creating or updating an ingredient."""
    ingredient_name: str = Field(..., min_length=1)
    ingredient_category: str = Field(..., min_length=1)
    quantity: Optional[float] = None
    unit: Optional[str] = None

    @field_validator("ingredient_name", "ingredient_category", mode="before")
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v