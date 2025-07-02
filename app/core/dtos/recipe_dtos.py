"""app/core/features/recipes/recipe_dtos.py

Pydantic DTOs for recipe and ingredient data transfer.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

# ── Recipe Ingredient DTOs ───────────────────────────────────────────────────────────────────
class RecipeIngredientDTO(BaseModel):
    """DTO describing an ingredient entry within a recipe."""
    existing_ingredient_id: Optional[int] = None
    ingredient_name: str = Field(..., min_length=1)
    ingredient_category: str = Field(..., min_length=1)
    quantity: Optional[float] = None
    unit: Optional[str] = None

    @field_validator("ingredient_name", "ingredient_category", mode="before")
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


# ── Recipe DTOs ──────────────────────────────────────────────────────────────────────────────
class RecipeCreateDTO(BaseModel):
    """DTO used to create a new recipe with ingredients."""
    recipe_name: str = Field(..., min_length=1)
    recipe_category: str = Field(..., min_length=1)
    meal_type: str = Field(default="Dinner", min_length=1)
    diet_preference: Optional[str] = None
    total_time: Optional[int] = None
    servings: Optional[int] = None
    directions: Optional[str] = None
    image_path: Optional[str] = None
    ingredients: List[RecipeIngredientDTO] = []

class RecipeUpdateDTO(BaseModel):
    """DTO used to update a recipe's core attributes and ingredient list."""
    recipe_name: Optional[str] = None
    recipe_category: Optional[str] = None
    meal_type: Optional[str] = None
    diet_preference: Optional[str] = None
    total_time: Optional[int] = None
    servings: Optional[int] = None
    directions: Optional[str] = None
    image_path: Optional[str] = None
    ingredients: Optional[List[RecipeIngredientDTO]] = None

class RecipeFilterDTO(BaseModel):
    """DTO for filtering recipe queries."""
    recipe_category: Optional[str] = None
    meal_type: Optional[str] = None
    sort_by: Optional[str] = None
    favorites_only: bool = False
