# app/ui/views/__init__.py

# ── Primary Views ──
from .add_recipes.add_recipes import AddRecipes
from .dashboard import Dashboard
from .meal_planner.meal_planner import MealPlanner
from .shopping_list.shopping_list import ShoppingList
from .view_recipes.view_recipes import ViewRecipes
from .settings import Settings

# ── Sub Views ──
from .full_recipe import FullRecipe
from .recipe_selection import RecipeSelection



__all__ = [
    "Dashboard",
    "MealPlanner",
    "ViewRecipes",
    "ShoppingList",
    "AddRecipes",
    "Settings",
    "FullRecipe",
    "RecipeSelection",
]
