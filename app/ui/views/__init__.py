# app/ui/views/__init__.py

# ── Primary Views ──
from .add_recipes.view import AddRecipes
from .shopping_list.view import ShoppingList
from .recipe_browser.view import RecipeBrowser
from .meal_planner.view import MealPlanner
from .dashboard import Dashboard
from .settings import Settings

# ── Sub Views ──
from .full_recipe import FullRecipe

__all__ = [
    "Dashboard",
    "MealPlanner",
    "RecipeBrowser",
    "ShoppingList",
    "AddRecipes",
    "Settings",
    "FullRecipe",
]
