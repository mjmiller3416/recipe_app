# app/ui/views/__init__.py

from .add_recipes.add_recipes import AddRecipes
from .base import BaseView
from .dashboard.dashboard import Dashboard
from .meal_planner.meal_planner import MealPlanner
from .recipe_selection import RecipeSelection
from .settings.settings import Settings
from .shopping_list.shopping_list import ShoppingList
from .view_recipes.view_recipes import ViewRecipes

__all__ = [
    "Dashboard",
    "MealPlanner",
    "ViewRecipes",
    "ShoppingList",
    "AddRecipes",
    "Settings",
    "RecipeSelection",
    "BaseView",
]
