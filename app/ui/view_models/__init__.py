"""app/ui/view_models/__init__.py

View Model layer for MVVM architecture implementation.
Contains data binding, presentation logic, and UI-Core service coordination.
"""

from .add_recipe_view_model import AddRecipeViewModel, RecipeFormData
from .base_view_model import BaseValidationResult, BaseViewModel
from .ingredient_view_model import (
    IngredientFormData,
    IngredientMatchResult,
    IngredientValidationResult,
    IngredientViewModel,
)

__all__ = [
    "AddRecipeViewModel",
    "RecipeFormData", 
    "IngredientViewModel",
    "IngredientFormData",
    "IngredientMatchResult",
    "IngredientValidationResult",
    "BaseViewModel",
    "BaseValidationResult"
]