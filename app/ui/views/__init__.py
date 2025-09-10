# app/ui/views/__init__.py

from .add_recipes.add_recipes import AddRecipes
from .base import BaseView
from .dashboard.dashboard import Dashboard
from .meal_planner.meal_planner import MealPlanner
from .recipe_browser.recipe_browser import RecipeBrowser
from .settings.settings import Settings
from .shopping_list.shopping_list import ShoppingList

__all__ = [
    "Dashboard",
    "MealPlanner",
    "RecipeBrowser",
    "ShoppingList",
    "AddRecipes",
    "Settings",
    "BaseView",
]
