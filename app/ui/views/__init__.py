# app/ui/views/__init__.py

# ── Primary Views ──
from .add_recipes.add_recipes_view import AddRecipes
from .shopping_list.shopping_list_view import ShoppingList
from .recipe_browser.recipe_browser_view import RecipeBrowser
from .meal_planner.meal_planner_view import MealPlanner
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
