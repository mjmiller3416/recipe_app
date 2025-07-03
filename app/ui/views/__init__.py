# app/ui/views/__init__.py

# ── Dashboard View ──
from .dashboard import Dashboard

# ── Meal Planner View ──
from .meal_planner import MealPlanner

# ── View Recipes View ──
from .view_recipes import ViewRecipes

# ── Shopping List View ──
from .shopping_list import ShoppingList

# ── Add Recipes View ──
from .add_recipes import AddRecipes

__all__ = [
    "Dashboard",
    "MealPlanner",
    "ViewRecipes",
    "ShoppingList",
    "AddRecipes",
]
