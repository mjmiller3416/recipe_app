from typing import Optional

from pydantic import Field

from database.base_model import ModelBase


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
        # Override default pluralization to match the actual table name
        return "recipe_ingredients"

    def __repr__(self) -> str:
        return (
            f"RecipeIngredient(recipe_id={self.recipe_id}, "
            f"ingredient_id={self.ingredient_id}, quantity={self.quantity}, unit={self.unit})"
        )
