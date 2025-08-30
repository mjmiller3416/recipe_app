"""app/core/dtos/recipe_dtos.py

Pydantic DTOs for recipe operations and data transfer.
Handles recipe creation, updates, filtering, and responses with ingredient relationships.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

if TYPE_CHECKING:
    from app.core.models.ingredient import Ingredient
    from app.core.models.recipe import Recipe


# ── Recipe Ingredient DTOs ───────────────────────────────────────────────────────────────────
class RecipeIngredientDTO(BaseModel):
    """DTO describing an ingredient entry within a recipe."""

    model_config = ConfigDict(from_attributes=True)

    existing_ingredient_id: Optional[int] = None
    ingredient_name: str = Field(..., min_length=1)
    ingredient_category: str = Field(..., min_length=1)
    quantity: Optional[float] = None
    unit: Optional[str] = None

    @field_validator("ingredient_name", "ingredient_category", mode="before")
    @classmethod
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

# ── Base DTOs ─────────────────────────────────────────────────────────────────────────
class RecipeBaseDTO(BaseModel):
    """Base DTO for recipe operations."""

    model_config = ConfigDict(from_attributes=True)

    recipe_name: str = Field(..., min_length=1)
    recipe_category: str = Field(..., min_length=1)
    meal_type: str = Field(default="Dinner", min_length=1)
    diet_pref: Optional[str] = None  # match the model field name
    total_time: Optional[int] = Field(None, ge=0)
    servings: Optional[int] = Field(None, ge=1)
    directions: Optional[str] = None
    notes: Optional[str] = None
    reference_image_path: Optional[str] = None
    banner_image_path: Optional[str] = None

    @field_validator("recipe_name", "recipe_category", "meal_type", mode="before")
    @classmethod
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

# ── Create DTO ───────────────────────────────────────────────────────────────────────────────
class RecipeCreateDTO(RecipeBaseDTO):
    """DTO used to create a new recipe with ingredients."""
    ingredients: List[RecipeIngredientDTO] = []

# ── Update DTO ───────────────────────────────────────────────────────────────────────────────
class RecipeUpdateDTO(BaseModel):
    """DTO used to update a recipe's core attributes and ingredient list."""

    model_config = ConfigDict(from_attributes=True)

    recipe_name: Optional[str] = Field(None, min_length=1)
    recipe_category: Optional[str] = Field(None, min_length=1)
    meal_type: Optional[str] = Field(None, min_length=1)
    diet_pref: Optional[str] = None
    total_time: Optional[int] = Field(None, ge=0)
    servings: Optional[int] = Field(None, ge=1)
    directions: Optional[str] = None
    notes: Optional[str] = None
    reference_image_path: Optional[str] = None
    banner_image_path: Optional[str] = None
    ingredients: Optional[List[RecipeIngredientDTO]] = None
    is_favorite: Optional[bool] = None

    @field_validator("recipe_name", "recipe_category", "meal_type", mode="before")
    @classmethod
    def strip_strings(cls, v):
        if isinstance(v, str) and v:
            return v.strip()
        return v

# ── Response DTO ─────────────────────────────────────────────────────────────────────────────
class RecipeResponseDTO(RecipeBaseDTO):
    """DTO for recipe responses with full ingredient information."""

    id: int
    is_favorite: bool = False
    created_at: Optional[str] = None  # ISO format datetime string
    ingredients: List["Ingredient"] = []

# ── Filter DTO ───────────────────────────────────────────────────────────────────────────────
class RecipeFilterDTO(BaseModel):
    """DTO for filtering recipe queries."""

    model_config = ConfigDict(from_attributes=True)

    recipe_category: Optional[str] = None
    meal_type: Optional[str] = None
    diet_pref: Optional[str] = None
    cook_time: Optional[int] = Field(None, ge=0)
    servings: Optional[int] = Field(None, ge=1)
    sort_by: Optional[str] = Field(
        None, pattern="^(recipe_name|created_at|total_time|servings)$")
    sort_order: Optional[str] = Field(
        "asc", pattern="^(asc|desc)$")
    favorites_only: bool = False
    search_term: Optional[str] = None
    limit: Optional[int] = Field(None, ge=1, le=100)
    offset: Optional[int] = Field(None, ge=0)
