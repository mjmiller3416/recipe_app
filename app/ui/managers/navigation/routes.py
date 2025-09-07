"""app/ui/managers/navigation/routes.py

Navigation route registration and configuration for MealGenie application.

This module defines all application routes and their associated view classes, providing
centralized route management for the navigation system. Includes specialized route
wrappers and route-to-sidebar button mappings.

## Route Architecture

The navigation system uses a route-based architecture with centralized registration:

- **Route Registration**: All routes registered through NavigationRegistry
- **View Association**: Each route maps to a specific view class
- **Route Constants**: Centralized route path definitions
- **Wrapper Classes**: Specialized view configurations for specific routes

## Navigation Routes

### Main Application Routes
- `/dashboard` - Dashboard view with overview and quick actions
- `/meal-planner` - Meal planning and weekly schedule management
- `/recipes/browse` - Recipe browsing in normal mode
- `/recipes/browse/selection` - Recipe browsing in selection mode for meal planning
- `/recipes/add` - Add new recipes to the collection
- `/shopping-list` - Shopping list management and ingredient tracking
- `/settings` - Application settings and preferences

### Route Patterns
```python
# Static routes (exact match)
navigation_service.navigate_to("/dashboard")
navigation_service.navigate_to("/recipes/browse")

# Parameterized routes (future expansion)
# navigation_service.navigate_to("/recipes/view/123")
```

## RecipeBrowserView Route Integration

The RecipeBrowserView supports dual operation modes through route configuration:

### Normal Browsing Mode
- **Route**: `/recipes/browse`
- **View Class**: `RecipeBrowserView`
- **Configuration**: `selection_mode=False` (default)
- **Purpose**: Standard recipe browsing with recipe detail navigation
- **Usage**: Main recipe collection browsing

### Selection Mode for Meal Planning
- **Route**: `/recipes/browse/selection`
- **View Class**: `RecipeBrowserSelectionView` (wrapper class)
- **Configuration**: `selection_mode=True` (forced)
- **Purpose**: Recipe selection for meal planning workflows
- **Usage**: Select recipes to add to meal plans

### Route Wrapper Implementation
```python
class RecipeBrowserSelectionView(RecipeBrowserView):
    '''RecipeBrowserView configured for selection mode.'''

    def __init__(self, parent=None, **kwargs):
        # Force selection_mode=True for this route
        kwargs['selection_mode'] = True
        super().__init__(parent, **kwargs)
```

This pattern allows the same base view class to serve different purposes
through route-specific configuration while maintaining clean separation.

## Navigation Integration Patterns

### Sidebar Button Mapping
```python
def get_sidebar_route_mapping():
    '''Get mapping of sidebar buttons to their corresponding routes.'''
    return {
        "btn_dashboard": "/dashboard",
        "btn_meal_planner": "/meal-planner",
        "btn_browse_recipes": "/recipes/browse",        # Normal mode
        "btn_shopping_list": "/shopping-list",
        "btn_add_recipes": "/recipes/add",
        "btn_settings": "/settings"
    }
```

### Programmatic Navigation Examples
```python
# Navigate to standard recipe browsing
navigation_service.navigate_to("/recipes/browse")

# Navigate to recipe selection for meal planning
navigation_service.navigate_to("/recipes/browse/selection")

# Navigate from meal planner to recipe selection
def open_recipe_selector(self):
    self.navigation_service.navigate_to("/recipes/browse/selection")
```

## Route Registration Process

Routes are registered through the NavigationRegistry with metadata:

```python
NavigationRegistry.register_route(
    path="/recipes/browse",
    view_class=RecipeBrowserView,
    view_type=ViewType.MAIN,
    title="Browse Recipes",
    description="Browse and search through recipe collection"
)

NavigationRegistry.register_route(
    path="/recipes/browse/selection",
    view_class=RecipeBrowserSelectionView,
    view_type=ViewType.MAIN,
    title="Select Recipes",
    description="Select recipes for meal planning"
)
```

## View Lifecycle Integration

All registered routes support full view lifecycle management:

- **Lazy Loading**: Views instantiated only when navigated to
- **Caching**: View instances cached for performance (configurable)
- **Lifecycle Hooks**: `after_navigate_to`, `before_navigate_from`
- **Route Parameters**: Support for dynamic route parameters (future)

## Usage Guidelines

### Adding New Routes
1. Define route constant in `RouteConstants`
2. Import required view class
3. Register route with `NavigationRegistry.register_route()`
4. Add to sidebar mapping if needed (in `get_sidebar_route_mapping()`)

### Route Naming Conventions
- Use kebab-case for route paths: `/meal-planner`, `/recipes/browse`
- Group related routes with path prefixes: `/recipes/*`
- Use descriptive names that match UI labels
- Maintain consistency with existing patterns

See Also:
- `NavigationRegistry`: Route registration and management
- `NavigationService`: Route-based navigation service
- `RecipeBrowserView`: Recipe browsing view implementation
- View lifecycle documentation
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from app.ui.managers.navigation.registry import (
    NavigationRegistry, RouteConstants, ViewType,
)
from app.ui.views import (
    AddRecipes,
    Dashboard,
    MealPlanner,
    RecipeBrowser,
    Settings,
    ShoppingList,
)

# ── Route Wrapper Classes ───────────────────────────────────────────────────────────────────────────────────
class RecipeBrowserSelectionView(RecipeBrowser):
    """
    RecipeBrowserView configured specifically for selection mode workflows.

    This wrapper class provides a route-specific configuration of RecipeBrowserView
    that forces selection mode to be enabled. Used by the navigation system for
    the `/recipes/browse/selection` route to provide recipe selection functionality
    for meal planning workflows.

    Key Differences from Base RecipeBrowserView:
    - Selection mode is always enabled (selection_mode=True)
    - Recipe clicks emit recipe_selected signal instead of recipe_opened
    - Optimized for meal planning integration workflows
    - Cards show selection-appropriate visual feedback

    Usage:
        # Instantiated automatically by navigation system
        navigation_service.navigate_to("/recipes/browse/selection")

        # Manual instantiation (equivalent to RecipeBrowserView(selection_mode=True))
        selection_view = RecipeBrowserSelectionView()
        selection_view.recipe_selected.connect(handle_meal_plan_selection)

    Route Integration:
        - Route: /recipes/browse/selection
        - Purpose: Recipe selection for meal planning
        - Navigation: Accessed via navigation service or meal planner workflows
        - Signals: Emits recipe_selected(int, Recipe) when recipes are selected

    Architecture:
        - Inherits all functionality from RecipeBrowserView
        - Uses same RecipeBrowserViewModel for business logic
        - Same MVVM compliance and architectural patterns
        - Only difference is forced selection_mode=True configuration
    """

    def __init__(self, parent=None, **kwargs):
        # Force selection_mode=True for this route wrapper
        kwargs['selection_mode'] = True
        super().__init__(parent, **kwargs)


# ── Route Registration ──────────────────────────────────────────────────────────────────────────────────────
def register_main_routes():
    """
    Register all main application routes with the navigation system.

    This function registers all primary application routes with their associated
    view classes, metadata, and configuration. Should be called during application
    initialization to set up the navigation system.

    Registered Routes:
        /dashboard - Main dashboard with overview and quick actions
        /meal-planner - Meal planning and weekly schedule management
        /recipes/browse - Recipe browsing in normal mode
        /recipes/browse/selection - Recipe selection mode for meal planning
        /recipes/add - Add new recipes to the collection
        /shopping-list - Shopping list management and ingredient tracking
        /settings - Application settings and preferences

    Route Configuration:
        - All routes use ViewType.MAIN for full-screen navigation
        - Lazy loading enabled for performance (views created when accessed)
        - Caching enabled for frequently accessed views
        - Descriptive titles and descriptions for UI integration

    RecipeBrowserView Route Integration:
        The recipe browsing functionality is split into two routes:

        1. /recipes/browse (Normal Mode):
           - Uses RecipeBrowserView with selection_mode=False
           - For standard recipe browsing and detail viewing
           - Accessible via sidebar "View Recipes" button

        2. /recipes/browse/selection (Selection Mode):
           - Uses RecipeBrowserSelectionView wrapper class
           - Forces selection_mode=True for meal planning workflows
           - Used by meal planner for recipe selection
           - Emits recipe_selected signals for integration

    Usage:
        # Call during application startup
        register_main_routes()

        # Routes become available via navigation service
        navigation_service.navigate_to("/recipes/browse")
        navigation_service.navigate_to("/recipes/browse/selection")
    """

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
        path=RouteConstants.RECIPES_BROWSE,
        view_class=RecipeBrowser,
        view_type=ViewType.MAIN,
        title="Browse Recipes",
        description="Browse and search through recipe collection"
    )

    NavigationRegistry.register_route(
        path=RouteConstants.RECIPES_BROWSE_SELECTION,
        view_class=RecipeBrowserSelectionView,
        view_type=ViewType.MAIN,
        title="Select Recipes",
        description="Select recipes for meal planning"
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
    """
    Get mapping of sidebar buttons to their corresponding navigation routes.

    Returns a dictionary mapping sidebar button object names to their target
    navigation routes. Used by the sidebar component to enable navigation
    when buttons are clicked.

    Sidebar Navigation:
        btn_dashboard -> /dashboard (Dashboard view)
        btn_meal_planner -> /meal-planner (Meal Planner view)
        btn_browse_recipes -> /recipes/browse (Recipe Browser in normal mode)
        btn_shopping_list -> /shopping-list (Shopping List view)
        btn_add_recipes -> /recipes/add (Add Recipes view)
        btn_settings -> /settings (Settings view)

    Note on Recipe Browsing:
        The sidebar "View Recipes" button maps to /recipes/browse (normal mode).
        The selection mode route /recipes/browse/selection is used programmatically
        by other components (like meal planner) and is not directly accessible
        from the sidebar navigation.

    Usage:
        # Get mapping dictionary
        button_routes = get_sidebar_route_mapping()

        # Used by sidebar component for navigation
        def handle_sidebar_click(self, button_name):
            route = button_routes.get(button_name)
            if route:
                self.navigation_service.navigate_to(route)

    Returns:
        Dict[str, str]: Mapping of button names to route paths
    """
    return {
        "btn_dashboard": RouteConstants.DASHBOARD,
        "btn_meal_planner": RouteConstants.MEAL_PLANNER,
        "btn_browse_recipes": RouteConstants.RECIPES_BROWSE,
        "btn_shopping_list": RouteConstants.SHOPPING_LIST,
        "btn_add_recipes": RouteConstants.RECIPES_ADD,
        "btn_settings": RouteConstants.SETTINGS
    }
