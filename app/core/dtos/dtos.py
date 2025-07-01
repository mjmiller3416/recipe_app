"""Data transfer objects for MealGenie core services."""

from typing import List, Optional, Any

from pydantic import BaseModel, Field, field_validator

from app.core.utils.validators import strip_string


class IngredientSearchDTO(BaseModel):
    """Criteria for searching ingredients."""

    search_term: str = Field(..., min_length=1)
    category: Optional[str] = None


class IngredientCreateDTO(BaseModel):
    """Input data for creating or retrieving an ingredient."""

    ingredient_name: str = Field(..., min_length=1)
    ingredient_category: str = Field(..., min_length=1)
    quantity: Optional[float] = None
    unit: Optional[str] = None

    @field_validator("ingredient_name", "ingredient_category", mode="before")
    def _strip_strings(cls, v: Any) -> Any:
        return strip_string(v)


class RecipeIngredientInputDTO(BaseModel):
    """Ingredient information when creating a recipe."""

    existing_ingredient_id: Optional[int] = None
    ingredient_name: str = Field(..., min_length=1)
    ingredient_category: str = Field(..., min_length=1)
    quantity: Optional[float] = None
    unit: Optional[str] = None

    @field_validator("ingredient_name", "ingredient_category", mode="before")
    def _strip_strings(cls, v: Any) -> Any:
        return strip_string(v)


class RecipeCreateDTO(BaseModel):
    """Input data for creating a recipe with ingredients."""

    recipe_name: str = Field(..., min_length=1)
    recipe_category: str = Field(..., min_length=1)
    meal_type: str = Field(default="Dinner", min_length=1)
    total_time: Optional[int] = None
    servings: Optional[int] = None
    directions: Optional[str] = None
    image_path: Optional[str] = None
    ingredients: List[RecipeIngredientInputDTO] = []


class RecipeFilterDTO(BaseModel):
    """Filtering options when listing recipes."""

    recipe_category: Optional[str] = None
    meal_type: Optional[str] = None
    sort_by: Optional[str] = None
    favorites_only: bool = False

