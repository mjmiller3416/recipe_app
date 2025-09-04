"""app/ui/services/navigation/routes.py

Route registration for the navigation system.
"""

from app.ui.services.navigation.navigation_registry import NavigationRegistry, ViewType
from app.ui.views import (
    Dashboard,
    MealPlanner, 
    ViewRecipes,
    ShoppingList,
    AddRecipes,
    Settings
)


def register_main_routes():
    """Register all main application routes."""
    
    # Main navigation routes using the constants
    NavigationRegistry.register_route(
        path="/dashboard",
        view_class=Dashboard,
        view_type=ViewType.MAIN,
        title="Dashboard",
        description="Main dashboard with overview and quick actions"
    )
    
    NavigationRegistry.register_route(
        path="/meal-planner", 
        view_class=MealPlanner,
        view_type=ViewType.MAIN,
        title="Meal Planner",
        description="Plan meals and create meal schedules"
    )
    
    NavigationRegistry.register_route(
        path="/recipes/browse",
        view_class=ViewRecipes,
        view_type=ViewType.MAIN, 
        title="View Recipes",
        description="Browse and search through recipe collection"
    )
    
    NavigationRegistry.register_route(
        path="/shopping-list",
        view_class=ShoppingList,
        view_type=ViewType.MAIN,
        title="Shopping List", 
        description="Manage shopping lists and ingredients"
    )
    
    NavigationRegistry.register_route(
        path="/recipes/add",
        view_class=AddRecipes,
        view_type=ViewType.MAIN,
        title="Add Recipes",
        description="Add new recipes to the collection"
    )
    
    NavigationRegistry.register_route(
        path="/settings",
        view_class=Settings,
        view_type=ViewType.MAIN,
        title="Settings",
        description="Application settings and preferences"
    )


def get_sidebar_route_mapping():
    """Get mapping of sidebar buttons to their corresponding routes."""
    return {
        "btn_dashboard": "/dashboard",
        "btn_meal_planner": "/meal-planner", 
        "btn_view_recipes": "/recipes/browse",
        "btn_shopping_list": "/shopping-list",
        "btn_add_recipes": "/recipes/add",
        "btn_settings": "/settings"
    }