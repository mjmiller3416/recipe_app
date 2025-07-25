"""app/core/dtos/shopping_item_dtos.py

Pydantic DTOs for shopping item operations and data transfer.
Handles shopping item creation, updates, and responses.
"""

# ── Imports ──────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ── Base DTOs ──────────────────────────────────────────────────────────────
class ShoppingItemBaseDTO(BaseModel):
    """Base DTO for shopping item operations."""
    model_config = ConfigDict(from_attributes=True)
    ingredient_name: str = Field(..., min_length=1, max_length=255)
    quantity: float = Field(..., ge=0)
    unit: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=100)

    @field_validator("ingredient_name", mode="before")
    @classmethod
    def strip_ingredient_name(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

# ── Create DTOs ────────────────────────────────────────────────────────────
class ShoppingItemCreateDTO(ShoppingItemBaseDTO):
    """DTO for creating a new shopping item."""
    source: Literal["recipe", "manual"] = "manual"

class ManualItemCreateDTO(BaseModel):
    """DTO for creating a manual shopping item."""
    model_config = ConfigDict(from_attributes=True)
    ingredient_name: str = Field(..., min_length=1, max_length=255)
    quantity: float = Field(..., ge=0)
    unit: Optional[str] = Field(None, max_length=50)

    @field_validator("ingredient_name", mode="before")
    @classmethod
    def strip_ingredient_name(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

# ── Update DTOs ────────────────────────────────────────────────────────────
class ShoppingItemUpdateDTO(BaseModel):
    """DTO for updating a shopping item."""
    model_config = ConfigDict(from_attributes=True)
    ingredient_name: Optional[str] = Field(None, min_length=1, max_length=255)
    quantity: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=100)
    have: Optional[bool] = None

    @field_validator("ingredient_name", mode="before")
    @classmethod
    def strip_ingredient_name(cls, v):
        if isinstance(v, str) and v:
            return v.strip()
        return v

# ── Response DTOs ────────────────────────────────────────────────────────────
class ShoppingItemResponseDTO(ShoppingItemBaseDTO):
    """DTO for shopping item responses."""
    id: int
    source: Literal["recipe", "manual"]
    have: bool = False
    state_key: Optional[str] = None