"""
This module exposes all main view classes as flat imports for convenience.

Usage:
    from app.ui.views import Dashboard, MealPlanner, AddRecipes
"""

# ── Dashboard View ──
from .dashboard.dashboard import Dashboard

# ── Meal Planner View ──
from .meal_planner.meal_planner import MealPlanner

# ── View Recipes View ──
from .view_recipes.view_recipes import ViewRecipes

# ── Shopping List View ──
from .shopping_list.shopping_list import ShoppingList

# ── Add Recipes View ──
from .add_recipes.add_recipes import AddRecipes

__all__ = [
    "Dashboard",
    "MealPlanner",
    "ViewRecipes",
    "ShoppingList",
    "AddRecipes",
]
# this allows importing all main views directly from app.ui.views