"""Data transfer objects for Recipe and Ingredient operations."""

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


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


class RecipeIngredientInputDTO(BaseModel):
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


class RecipeCreateDTO(BaseModel):
    """DTO used to create a new recipe with ingredients."""

    recipe_name: str = Field(..., min_length=1)
    recipe_category: str = Field(..., min_length=1)
    meal_type: str = Field(default="Dinner", min_length=1)
    total_time: Optional[int] = None
    servings: Optional[int] = None
    directions: Optional[str] = None
    image_path: Optional[str] = None
    ingredients: List[RecipeIngredientInputDTO] = []


class RecipeFilterDTO(BaseModel):
    """DTO for filtering recipe queries."""

    recipe_category: Optional[str] = None
    meal_type: Optional[str] = None
    sort_by: Optional[str] = None
    favorites_only: bool = False


