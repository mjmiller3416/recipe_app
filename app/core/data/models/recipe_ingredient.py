"""database/models/recipe_ingredient.py

This module defines the RecipeIngredient model, which represents the join table
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from typing import NamedTuple, Optional

from pydantic import Field

from app.core.data.base_model import ModelBase


# ── Ingredient Detail Tuple ─────────────────────────────────────────────────────
class IngredientDetail(NamedTuple):
    ingredient_name: str
    ingredient_category: str
    quantity: Optional[float]
    unit: Optional[str]

# ── Recipe Ingredient Model ─────────────────────────────────────────────────────
class RecipeIngredient(ModelBase):
    """
    Pydantic model for the `recipe_ingredients` join table.
    """
    recipe_id: int = Field(..., description="Foreign key to recipes.id")
    ingredient_id: int = Field(..., description="Foreign key to ingredients.id")
    quantity: Optional[float] = Field(None, description="Quantity for this recipe")
    unit: Optional[str] = Field(None, description="Unit of measure for this ingredient")

    @classmethod
    def table_name(cls) -> str:
        # override default pluralization to match the actual table name
        return "recipe_ingredients"

    def get_ingredient_detail(self) -> IngredientDetail: 
        """
        Get the full ingredient details for this recipe ingredient.
        
        Returns:
            IngredientDetail: NamedTuple containing ingredient details.
        """
        from data.models.ingredient import Ingredient
        
        ingredient = Ingredient.get(self.ingredient_id) 
        
        if not ingredient:
            raise ValueError(f"Ingredient with id {self.ingredient_id} not found")
        
        return IngredientDetail(
            ingredient_name=ingredient.ingredient_name,
            ingredient_category=ingredient.ingredient_category,
            quantity=self.quantity,
            unit=self.unit
        )

    def __repr__(self) -> str:
        """
        Custom string representation for debugging.
        
        Returns:
            str: String representation of the RecipeIngredient instance.
        """
        return (
            f"RecipeIngredient(recipe_id={self.recipe_id}, "
            f"ingredient_id={self.ingredient_id}, quantity={self.quantity}, unit={self.unit})"
        )
