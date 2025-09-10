# app/ui/views/__init__.py

from .base import BaseView
from .add_recipes.add_recipes import AddRecipes
from .dashboard.dashboard import Dashboard
from .meal_planner.meal_planner import MealPlanner
from .recipe_browser.recipe_browser import RecipeBrowser
from .settings.settings import Settings
from .shopping_list.shopping_list import ShoppingList
from .view_recipe.view_recipe import ViewRecipe

__all__ = [
    "Dashboard",
    "MealPlanner",
    "RecipeBrowser",
    "ShoppingList",
    "AddRecipes",
    "Settings",
    "BaseView",
    "ViewRecipe",
]
