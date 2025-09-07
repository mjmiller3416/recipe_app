"""app/ui/view_models/__init__.py

View Model layer for MVVM architecture implementation.
Contains data binding, presentation logic, and UI-Core service coordination.
"""

from .add_recipe_vm import AddRecipesViewModel, RecipeFormData
from .base_view_model import BaseValidationResult, BaseViewModel
from .ingredient_vm import (
    IngredientFormData,
    IngredientMatchResult,
    IngredientValidationResult,
    IngredientViewModel,
)
from .meal_planner_vm import MealPlannerViewModel
from .meal_widget_vm import MealSummaryDTO, MealWidgetViewModel
from .recipe_browser_vm import RecipeBrowserViewModel
from .shopping_list_vm import ShoppingListViewModel

__all__ = [
    "AddRecipesViewModel",
    "RecipeFormData",
    "IngredientViewModel",
    "IngredientFormData",
    "IngredientMatchResult",
    "IngredientValidationResult",
    "MealPlannerViewModel",
    "MealWidgetViewModel",
    "MealSummaryDTO",
    "RecipeBrowserViewModel",
    "BaseViewModel",
    "BaseValidationResult",
    "ShoppingListViewModel"
]
