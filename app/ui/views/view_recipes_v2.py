"""app/ui/views/view_recipes_v2.py

ViewRecipes view migrated to the new route-based navigation system.
Demonstrates handling of embedded components and sub-navigation.
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QStackedWidget, QVBoxLayout

from app.ui.components.composite.recipe_browser import RecipeBrowser
from app.ui.components.composite.recipe_card import LayoutSize
from app.ui.services.navigation_views import MainView
from app.ui.services.navigation_registry import NavigationRegistry, ViewType, RouteConstants
from _dev_tools import DebugLogger


@NavigationRegistry.register(
    path=RouteConstants.RECIPES_BROWSE,
    view_type=ViewType.MAIN,
    title="Browse Recipes",
    description="Browse and search recipes"
)
class ViewRecipes(MainView):
    """
    View recipes using the shared RecipeBrowser component with navigation integration.

    This demonstrates how to integrate existing components with the new navigation system.
    """

    recipe_selected = Signal(int)

    def __init__(self, parent=None, meal_selection=False):
        super().__init__(parent)
        self.setObjectName("ViewRecipes")
        self.meal_selection = meal_selection
        self.current_full_recipe_view = None

        DebugLogger.log("Initializing ViewRecipes page (v2)", "info")
        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        """Build the view recipes UI."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Create stacked widget for switching between recipe list and full recipe
        self.stacked_widget = QStackedWidget()

        # Create recipe browser
        self.recipe_browser = RecipeBrowser(
            parent=self,
            card_size=LayoutSize.MEDIUM,
            selection_mode=self.meal_selection
        )
        self.recipe_browser.setObjectName("RecipeBrowser")

        # Add recipe browser to stacked widget
        self.stacked_widget.addWidget(self.recipe_browser)  # index 0
        self.main_layout.addWidget(self.stacked_widget)

    def _connect_signals(self):
        """Connect component signals based on mode."""
        if self.meal_selection:
            self.recipe_browser.recipe_selected.connect(self.recipe_selected.emit)
        else:
            # Normal mode - use navigation to show full recipe
            self.recipe_browser.recipe_card_clicked.connect(self._show_full_recipe)

    def refresh(self):
        """Refresh the recipe display."""
        self.recipe_browser.refresh()

    def _show_full_recipe(self, recipe):
        """
        Navigate to full recipe view using the new navigation system.

        This demonstrates sub-navigation within a main view.
        """
        DebugLogger.log(f"Showing full recipe: {recipe.id}", "info")

        # Use navigation to show full recipe
        # This could be implemented as:
        # 1. A route parameter: /recipes/view/{id}
        # 2. Navigation to a modal view
        # 3. Navigation within this stacked widget (current approach)

        # For now, maintain existing behavior but with navigation hooks
        self._navigate_to_full_recipe(recipe)

    def _navigate_to_full_recipe(self, recipe):
        """Internal navigation to full recipe view."""
        # Import here to avoid circular imports
        from app.ui.views.full_recipe import FullRecipe

        # Remove current full recipe view if it exists
        if self.current_full_recipe_view:
            self.stacked_widget.removeWidget(self.current_full_recipe_view)
            self.current_full_recipe_view.deleteLater()
            self.current_full_recipe_view = None

        # Create new full recipe view
        self.current_full_recipe_view = FullRecipe(recipe, parent=self)

        # Connect back navigation
        if hasattr(self.current_full_recipe_view, 'back_clicked'):
            self.current_full_recipe_view.back_clicked.connect(self._show_recipe_list)

        # Add to stacked widget and show
        self.stacked_widget.addWidget(self.current_full_recipe_view)
        self.stacked_widget.setCurrentWidget(self.current_full_recipe_view)

        # Update navigation data to track current recipe
        self.set_navigation_data('current_recipe_id', recipe.id)

    def _show_recipe_list(self):
        """Return to the recipe list view."""
        self.stacked_widget.setCurrentWidget(self.recipe_browser)

        # Clean up the full recipe view
        if self.current_full_recipe_view:
            self.stacked_widget.removeWidget(self.current_full_recipe_view)
            self.current_full_recipe_view.deleteLater()
            self.current_full_recipe_view = None

        # Clear navigation data
        self.set_navigation_data('current_recipe_id', None)

    def showEvent(self, event):
        """Handle show event with lazy loading."""
        super().showEvent(event)
        if not self.recipe_browser.recipes_loaded:
            self.recipe_browser.load_recipes()

        # Force layout update after show
        from PySide6.QtCore import QTimer
        QTimer.singleShot(50, self._ensure_layout_update)

    def _ensure_layout_update(self):
        """Ensure the layout is properly updated after showing."""
        if hasattr(self.recipe_browser, 'scroll_container'):
            self.recipe_browser.scroll_container.updateGeometry()
            self.recipe_browser.scroll_area.updateGeometry()
            self.recipe_browser.flow_layout.update()

    # Navigation lifecycle hooks
    def on_route_changed(self, path: str, params: dict):
        """Handle route changes."""
        DebugLogger.log(f"ViewRecipes route changed: {path}", "info")

        # Handle route parameters if any
        recipe_id = params.get('id')
        if recipe_id:
            # If we have a recipe ID parameter, we could load that specific recipe
            DebugLogger.log(f"Loading specific recipe: {recipe_id}", "info")

    def before_navigate_to(self, path: str, params: dict) -> bool:
        """Called before navigating to this view."""
        DebugLogger.log("Preparing to show recipes view", "info")
        return True

    def after_navigate_to(self, path: str, params: dict):
        """Called after navigating to this view."""
        DebugLogger.log("Recipes view is now active", "info")
        # Ensure recipes are loaded
        if not self.recipe_browser.recipes_loaded:
            self.recipe_browser.load_recipes()

    def before_navigate_from(self, next_path: str, next_params: dict) -> bool:
        """Called before navigating away from this view."""
        DebugLogger.log(f"Leaving recipes view for: {next_path}", "info")

        # Save current view state if needed
        current_recipe_id = self.get_navigation_data('current_recipe_id')
        if current_recipe_id:
            DebugLogger.log(f"Saving state: viewing recipe {current_recipe_id}", "info")

        return True

    def after_navigate_from(self, next_path: str, next_params: dict):
        """Called after navigating away from this view."""
        DebugLogger.log("Left recipes view", "info")


# Register RecipeBrowser as a standalone embedded view that can be navigated to directly
@NavigationRegistry.register(
    path="/recipes/browser",
    view_type=ViewType.EMBEDDED,
    title="Recipe Browser",
    description="Standalone recipe browser component"
)
class StandaloneRecipeBrowser(RecipeBrowser):
    """
    Standalone version of RecipeBrowser that can be navigated to directly.

    This demonstrates how existing components can be made navigable.
    """

    def __init__(self, parent=None):
        # Initialize as embedded view but allow standalone usage
        super().__init__(parent, card_size=LayoutSize.MEDIUM, selection_mode=False)
        self.setObjectName("StandaloneRecipeBrowser")

        # Connect signals for standalone navigation
        self.recipe_card_clicked.connect(self._handle_recipe_click)

    def _handle_recipe_click(self, recipe):
        """Handle recipe card clicks in standalone mode."""
        # Navigate to full recipe view or open modal
        # This demonstrates different navigation patterns
        DebugLogger.log(f"Standalone browser: showing recipe {recipe.id}", "info")

        # Option 1: Navigate to recipe view route
        from app.ui.services.navigation_service_v2 import navigate_to
        navigate_to(f"/recipes/view/{recipe.id}")

        # Option 2: Could open as modal
        # navigate_to("/recipes/modal", {"id": str(recipe.id)})

    def set_route_info(self, path: str, params: dict):
        """Handle route information for standalone mode."""
        super().set_route_info(path, params)
        # Set standalone mode when used as navigable view
        if hasattr(self, 'set_standalone_mode'):
            self.set_standalone_mode(True)
