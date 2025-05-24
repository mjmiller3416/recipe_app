"""services/dtos/ingredient_dtos.py

This module defines the IngredientSearchDTO class for searching ingredients.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from typing import Optional
from pydantic import BaseModel, Field

# ── DTO for Ingredient Operations ───────────────────────────────────────────────
class IngredientSearchDTO(BaseModel):
    search_term: str = Field(..., min_length=1)
    category: Optional[str] = None