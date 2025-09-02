# Navigation System Integration Guide

This guide explains how to integrate the new route-based navigation system into the MealGenie application.

## Overview

The new navigation system provides:
- **Route-based navigation** with string paths like `/dashboard`, `/recipes/browse`
- **Multiple view types**: Main, Modal, Overlay, and Embedded views
- **Navigation history** with back/forward functionality
- **Lifecycle hooks** for view initialization and cleanup
- **Dynamic route registration** without hardcoded mappings
- **Support for parameterized routes** like `/recipes/edit/{id}`

## Key Benefits

### Before (Old System)
- Hardcoded page mapping in NavigationService
- Only views with sidebar buttons could be navigated to
- No navigation history
- Mixed navigation and page lifecycle logic
- Difficult to add new navigable views

### After (New System)
- Dynamic route registration with decorators
- Any view can be navigable regardless of sidebar
- Full navigation history with back/forward
- Clean separation of concerns
- Easy to add new routes and view types

## Integration Steps

### 1. Replace Navigation Service

Replace the old `navigation_service.py` with `navigation_service_v2.py`:

```python
# In main.py or main_window.py
from app.ui.services.navigation_service_v2 import NavigationService
from PySide6.QtWidgets import QStackedWidget

# Create navigation service
main_stack = QStackedWidget()
nav_service = NavigationService.create(main_stack)
```

### 2. Update Views to Use New Base Classes

Migrate existing views to inherit from the new base classes:

```python
# Old way
class Dashboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # ... UI setup

# New way
from app.ui.services.navigation_views import MainView
from app.ui.services.navigation_registry import NavigationRegistry, ViewType, RouteConstants

@NavigationRegistry.register(
    path=RouteConstants.DASHBOARD,
    view_type=ViewType.MAIN,
    title="Dashboard"
)
class Dashboard(MainView):
    def __init__(self, parent=None):
        super().__init__(parent)
        # ... UI setup
        
    def on_route_changed(self, path: str, params: dict):
        # Handle route-specific initialization
        pass
```

### 3. Update Sidebar Integration

Replace the old sidebar with `sidebar_v2.py`:

```python
from app.ui.components.navigation.sidebar_v2 import Sidebar, connect_sidebar_navigation

# Create sidebar
sidebar = Sidebar()

# Connect to navigation service
connect_sidebar_navigation(sidebar)
```

### 4. Register Routes for Existing Views

Add route registration to existing views:

```python
# Dashboard
NavigationRegistry.register_route(
    path="/dashboard",
    view_class=Dashboard,
    view_type=ViewType.MAIN,
    title="Dashboard"
)

# View Recipes
NavigationRegistry.register_route(
    path="/recipes/browse", 
    view_class=ViewRecipes,
    view_type=ViewType.MAIN,
    title="Browse Recipes"
)

# Recipe Browser as standalone
NavigationRegistry.register_route(
    path="/recipes/browser",
    view_class=RecipeBrowser,
    view_type=ViewType.EMBEDDED,
    title="Recipe Browser"
)
```

### 5. Update Component Usage

For components like RecipeBrowser that can be both embedded and standalone:

```python
# Old way - always embedded
recipe_browser = RecipeBrowser(parent=self, selection_mode=False)

# New way - can be embedded or standalone
from app.ui.components.composite.recipe_browser_v2 import RecipeBrowser

# Embedded usage (same as before)
recipe_browser = RecipeBrowser(parent=self, selection_mode=False)

# Standalone usage via navigation
navigate_to("/recipes/browser")
```

## Usage Examples

### Basic Navigation

```python
from app.ui.services.navigation_service_v2 import navigate_to

# Navigate to dashboard
navigate_to("/dashboard")

# Navigate to recipes with parameters
navigate_to("/recipes/view/{id}", {"id": "123"})

# Navigate with additional options
navigate_to("/recipes/browse", context="main", replace_current=True)
```

### Navigation History

```python
from app.ui.services.navigation_service_v2 import NavigationService

nav_service = NavigationService.get_instance()

# Go back
nav_service.go_back()

# Go forward  
nav_service.go_forward()

# Check if navigation is possible
can_go_back = nav_service.can_go_back()
can_go_forward = nav_service.can_go_forward()
```

### View Lifecycle Hooks

```python
class MyView(MainView):
    def before_navigate_to(self, path: str, params: dict) -> bool:
        # Prepare view for display
        return True  # Return False to cancel navigation
        
    def after_navigate_to(self, path: str, params: dict):
        # View is now active
        pass
        
    def before_navigate_from(self, next_path: str, next_params: dict) -> bool:
        # Save state before leaving
        return True  # Return False to cancel navigation
        
    def after_navigate_from(self, next_path: str, next_params: dict):
        # Cleanup after navigation
        pass
```

### Route Parameters

```python
@NavigationRegistry.register("/recipes/edit/{id}", ViewType.MAIN)
class EditRecipe(MainView):
    def on_route_changed(self, path: str, params: dict):
        recipe_id = params.get('id')  # Get the ID parameter
        if recipe_id:
            self.load_recipe(recipe_id)
```

### Modal and Overlay Views

```python
# Modal view
@NavigationRegistry.register("/recipe/confirm", ViewType.MODAL)
class ConfirmDialog(ModalView):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Dialog setup

# Overlay view
@NavigationRegistry.register("/recipe/tooltip", ViewType.OVERLAY)  
class RecipeTooltip(OverlayView):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Tooltip setup
```

## Migration Checklist

- [ ] Replace `navigation_service.py` with `navigation_service_v2.py`
- [ ] Update main window to use new NavigationService  
- [ ] Replace sidebar with `sidebar_v2.py`
- [ ] Migrate views to inherit from new base classes
- [ ] Add route registration for all views
- [ ] Update component usage where needed
- [ ] Test navigation between all views
- [ ] Test back/forward functionality
- [ ] Test embedded vs standalone component usage
- [ ] Update any hardcoded navigation calls

## Testing the New System

Run the demo application:

```bash
python navigation_demo.py
```

This will show:
- Route registration working
- Sidebar navigation integration
- Back/forward history
- Standalone vs embedded component usage
- Different view types

## Benefits Achieved

### 1. **Flexible Navigation**
- RecipeBrowser can now be navigated to directly: `/recipes/browser`  
- No need to embed in other views
- Any component can become navigable

### 2. **Better UX**
- Navigation history with back/forward
- Route-based URLs enable bookmarking (future)
- Consistent navigation patterns

### 3. **Cleaner Code**  
- No hardcoded page mappings
- Separation of navigation from business logic
- Lifecycle hooks for proper initialization/cleanup

### 4. **Extensibility**
- Easy to add new navigable views
- Support for different view types
- Plugin-like route registration

## Troubleshooting

### Route Not Found
- Ensure route is registered before navigation
- Check route path spelling
- Verify view class is importable

### Navigation Not Working
- Check NavigationService is properly initialized
- Verify sidebar connection
- Check for circular imports

### View Not Updating
- Implement lifecycle hooks properly
- Check view's `on_route_changed` method
- Verify route parameters are handled

This new navigation system solves your original concerns:
1. ✅ **Design pattern is more optimal** - Route-based with clear separation of concerns
2. ✅ **Can navigate to any view** - Not limited to sidebar mappings  
3. ✅ **No need to embed views** - Components like RecipeBrowser can be standalone

The system is backward-compatible and can be integrated incrementally.