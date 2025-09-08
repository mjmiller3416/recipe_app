# app/ui/views/__init__.py

# ── Primary Views ──
from .add_recipes.add_recipes_view import AddRecipesView
from .shopping_list.shopping_list_view import ShoppingListView
from .recipe_browser.recipe_browser_view import RecipeBrowserView
from .meal_planner.meal_planner_view import MealPlannerView
from .dashboard_view import DashboardView
from .settings_view import SettingsView

# ── Sub Views ──
from .view_recipe.view_recipe import ViewRecipe

__all__ = [
    "DashboardView",
    "MealPlannerView",
    "RecipeBrowserView",
    "ShoppingListView",
    "AddRecipesView",
    "SettingsView",
    "ViewRecipe",
]
