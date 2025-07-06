# app/ui/views/__init__.py

# ── Dashboard View ──
# ── Add Recipes View ──
from .add_recipes import AddRecipes
from .dashboard import Dashboard
# ── Meal Planner View ──
from .meal_planner import MealPlanner
# ── Shopping List View ──
from .shopping_list import ShoppingList
# ── View Recipes View ──
from .view_recipes import ViewRecipes

__all__ = [
    "Dashboard",
    "MealPlanner",
    "ViewRecipes",
    "ShoppingList",
    "AddRecipes",
]
