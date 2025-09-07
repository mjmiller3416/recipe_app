"""app/ui/views/recipe_browser_view.py

RecipeBrowserView - Advanced recipe browsing interface following strict MVVM architecture.

This MainView provides a comprehensive recipe browsing experience with dual operation modes,
advanced filtering capabilities, and seamless integration with the MealGenie navigation system.
All business logic is handled through the RecipeBrowserViewModel, ensuring proper separation
of concerns and maintaining architectural integrity.

## Architecture Overview

The RecipeBrowserView follows MealGenie's layered MVVM architecture:

- **View Layer (this file)**: Pure UI presentation and user interaction handling
- **ViewModel Layer**: `RecipeBrowserViewModel` handles all business logic and data operations
- **Service Layer**: `RecipeService` performs data access through repositories
- **Model Layer**: Recipe entities and DTOs for data transfer

## Key Features

- **Dual Operation Modes**: Normal browsing and selection modes for different workflows
- **Advanced Filtering**: Category, favorites, and search-based filtering
- **Multiple Sort Options**: Name, date, time, servings-based sorting
- **Responsive Layout**: Dynamic grid layout with FlowLayout adaptation
- **Navigation Integration**: Full lifecycle support with navigation service
- **MVVM Compliance**: Strict separation of UI and business logic

## Usage Patterns

### Normal Browsing Mode
```python
# Standard recipe browsing - opens full recipe details when clicked
view = RecipeBrowserView(selection_mode=False)
view.recipe_opened.connect(handle_recipe_navigation)

# Via navigation service
navigation_service.navigate_to("/recipes/browse")
```

### Selection Mode for Meal Planning
```python
# Recipe selection for meal planning workflows
view = RecipeBrowserView(selection_mode=True)
view.recipe_selected.connect(handle_meal_planning_selection)

# Via navigation service
navigation_service.navigate_to("/recipes/browse/selection")
```

### Custom Card Sizing
```python
from app.ui.components.composite.recipe_card import LayoutSize

# Large cards for featured display
view = RecipeBrowserView(card_size=LayoutSize.LARGE)

# Compact cards for dense layouts
view = RecipeBrowserView(card_size=LayoutSize.SMALL)
```

## Navigation Integration

The RecipeBrowserView integrates seamlessly with MealGenie's navigation system:

### Route Registration
- `/recipes/browse` - Normal browsing mode
- `/recipes/browse/selection` - Selection mode for meal planning

### Navigation Lifecycle
- `after_navigate_to()`: Ensures ViewModel initialization and data loading
- `before_navigate_from()`: Cleanup and state validation
- `on_route_changed()`: Handles route parameter changes

### Route Parameters
```python
# Selection mode via route parameters
navigation_service.navigate_to("/recipes/browse", {"selection_mode": "true"})
```

## Signal Architecture

### Navigation Signals
- `recipe_selected(int, Recipe)`: Emitted when recipe selected in selection mode
- `recipe_opened(Recipe)`: Emitted when recipe opened in normal mode
- `view_ready()`: Emitted when view is fully initialized and ready

### ViewModel Integration
All data operations flow through RecipeBrowserViewModel signals:
- `recipes_loaded`: Updates UI with new recipe data
- `filter_state_changed`: Reflects current filter state
- `selection_mode_changed`: Updates UI interaction mode

## Integration Examples

### Meal Planning Integration
```python
class MealPlannerView(ScrollableNavView):
    def open_recipe_selection(self):
        # Navigate to recipe browser in selection mode
        self.navigation_service.navigate_to("/recipes/browse/selection")

    def handle_recipe_selection(self, recipe_id: int, recipe: Recipe):
        # Process selected recipe for meal planning
        self.add_recipe_to_meal_plan(recipe_id, recipe)
```

### Search Integration
```python
def setup_search_integration(self):
    # Connect search widget to recipe browser
    search_widget.search_requested.connect(
        lambda term: self.recipe_browser.search_recipes(term)
    )

    search_widget.search_cleared.connect(
        lambda: self.recipe_browser.clear_search()
    )
```

## Performance Considerations

- **Lazy Loading**: ViewModel and data loading only occur when navigated to
- **Efficient Updates**: Layout updates are batched and optimized
- **Memory Management**: Proper cleanup in `__del__` method
- **Event Batching**: UI updates are processed in batches for smooth performance

## MVVM Compliance

### View Responsibilities (this class)
- ✅ UI widget management and layout
- ✅ User interaction handling (clicks, selections)
- ✅ Visual state management (loading, empty states)
- ✅ Signal emission for navigation

### ViewModel Responsibilities (RecipeBrowserViewModel)
- ✅ Business logic (filtering, sorting, search)
- ✅ Data service coordination
- ✅ State management (selection mode, filters)
- ✅ Error handling and validation

### Forbidden Patterns
- ❌ Direct database access from View
- ❌ Business logic in UI event handlers
- ❌ Importing core services directly in View
- ❌ UI logic in ViewModel

## Testing Support

The RecipeBrowserView is designed for comprehensive testing:

```python
# Unit testing individual components
def test_recipe_browser_initialization():
    view = RecipeBrowserView(selection_mode=True)
    assert view.is_selection_mode() == True

# Integration testing with navigation
def test_navigation_integration():
    view = create_test_view()
    view.after_navigate_to("/recipes/browse", {})
    assert view.is_recipes_loaded() == True
```

## Common Integration Patterns

### Dialog Integration
```python
class RecipeSelectionDialog(QDialog):
    def setup_browser(self):
        browser = RecipeBrowserView(selection_mode=True)
        browser.recipe_selected.connect(self.accept_selection)
        layout.addWidget(browser)
```

### Tab Integration
```python
def add_browse_tab(self):
    browser = RecipeBrowserView()
    browser.recipe_opened.connect(self.handle_recipe_details)
    tab_widget.addTab(browser, "Browse Recipes")
```

See Also:
- `RecipeBrowserViewModel`: Business logic layer
- `RecipeService`: Data access service
- Navigation system documentation
- MVVM architecture guidelines
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from typing import Any, Dict, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QScrollArea, QVBoxLayout, QWidget

from _dev_tools import DebugLogger
from app.config import RECIPE_CATEGORIES, SORT_OPTIONS
from app.core.dtos.recipe_dtos import RecipeFilterDTO
from app.core.models.recipe import Recipe
from app.ui.components.composite.recipe_card import LayoutSize, create_recipe_card
from app.ui.components.layout.flow_layout import FlowLayout
from app.ui.components.widgets import ComboBox
from app.ui.view_models.recipe_browser_view_model import RecipeBrowserViewModel
from app.ui.views.base import ScrollableNavView

# ── Recipe Browser View ─────────────────────────────────────────────────────────────────────────────────────
class RecipeBrowserView(ScrollableNavView):
    """
    MainView for recipe browsing with dual-mode operation following MVVM pattern.

    This view provides comprehensive recipe browsing with filtering, sorting, and search
    capabilities. Supports both normal browsing mode (for recipe viewing) and selection
    mode (for meal planning workflows).

    Key Features:
    - Dual operation modes (browse/selection) via constructor or route parameters
    - Advanced filtering: category, favorites, search term
    - Multiple sort options: name, date, time, servings
    - Responsive FlowLayout with dynamic card sizing
    - Full navigation lifecycle integration
    - Strict MVVM compliance through RecipeBrowserViewModel

    Usage Examples:
        # Normal browsing mode
        view = RecipeBrowserView(selection_mode=False)
        view.recipe_opened.connect(handle_recipe_navigation)

        # Selection mode for meal planning
        view = RecipeBrowserView(selection_mode=True)
        view.recipe_selected.connect(handle_meal_selection)

        # Via navigation service
        navigate_to("/recipes/browse")              # Normal mode
        navigate_to("/recipes/browse/selection")    # Selection mode

    Signals:
        recipe_selected(int, Recipe): Recipe selected in selection mode
        recipe_opened(Recipe): Recipe opened in normal mode
        view_ready(): View fully initialized and ready

    Architecture:
        View Layer: UI presentation and user interaction (this class)
        ViewModel: RecipeBrowserViewModel handles all business logic
        Service: RecipeService performs data access via repositories

    Navigation Routes:
        /recipes/browse - Normal browsing mode
        /recipes/browse/selection - Selection mode for meal planning
    """

    # Navigation and interaction signals
    recipe_selected = Signal(int, object)   # recipe_id, recipe_object - for selection mode
    recipe_opened = Signal(object)          # recipe_object - for navigation to full recipe
    view_ready = Signal()                   # emitted when view is fully initialized

    def __init__(self, parent=None, selection_mode: bool = False, card_size: LayoutSize = LayoutSize.MEDIUM):
        """
        Initialize the RecipeBrowserView with specified configuration.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
            selection_mode (bool, optional): Enable selection mode for meal planning workflows.
                When True, recipe clicks emit recipe_selected signal. When False, recipe clicks
                emit recipe_opened signal for navigation to detail views. Defaults to False.
            card_size (LayoutSize, optional): Size of recipe cards in the grid layout.
                Options: SMALL, MEDIUM, LARGE. Affects card dimensions and information density.
                Defaults to LayoutSize.MEDIUM.

        Note:
            The view automatically initializes its ViewModel and sets up navigation lifecycle
            hooks. Recipe loading occurs when navigated to via the navigation system.
        """
        self._selection_mode = selection_mode
        self._card_size = card_size
        self._view_model: Optional[RecipeBrowserViewModel] = None
        self._recipes_loaded = False

        super().__init__(parent)
        self.setObjectName("RecipeBrowserView")

        DebugLogger.log(
            f"RecipeBrowserView initialized - selection_mode: {selection_mode}, card_size: {card_size.name}",
            "info"
        )

    # ── ScrollableNavView Implementation ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        """Build the view-specific content including filters and recipe grid."""
        try:
            # Initialize ViewModel first
            self._initialize_view_model()

            # Build filter controls
            self._build_filter_controls()

            # Build recipe grid
            self._build_recipe_grid()

            # Set initial state
            self._set_initial_filter_state()

            DebugLogger.log("RecipeBrowserView UI built successfully", "debug")

        except Exception as e:
            DebugLogger.log(f"Error building RecipeBrowserView UI: {e}", "error")
            raise

    def _connect_view_model_signals(self):
        """Connect ViewModel signals to UI update methods."""
        if self._view_model is None:
            return

        try:
            # Recipe data signals
            self._view_model.recipes_loaded.connect(self._on_recipes_loaded)
            self._view_model.recipes_cleared.connect(self._on_recipes_cleared)

            # Selection and navigation signals
            self._view_model.recipe_selected.connect(self._on_recipe_selected)

            # State change signals
            self._view_model.selection_mode_changed.connect(self._on_selection_mode_changed)
            self._view_model.filter_state_changed.connect(self._on_filter_state_changed)

            # Status signals
            self._view_model.search_completed.connect(self._on_search_completed)
            self._view_model.error_occurred.connect(self._on_view_model_error)
            # Note: loading_changed signal is not available in current ViewModel implementation

            DebugLogger.log("RecipeBrowserViewModel signals connected", "debug")

        except Exception as e:
            DebugLogger.log(f"Error connecting ViewModel signals: {e}", "error")

    def _connect_signals(self):
        """Connect UI component signals to handlers."""
        try:
            # Filter control signals
            self._cb_filter.currentTextChanged.connect(self._on_category_filter_changed)
            self._cb_sort.currentTextChanged.connect(self._on_sort_option_changed)
            self._chk_favorites.stateChanged.connect(self._on_favorites_filter_changed)

            DebugLogger.log("RecipeBrowserView UI signals connected", "debug")

        except Exception as e:
            DebugLogger.log(f"Error connecting UI signals: {e}", "error")

    # ── ViewModel Initialization ────────────────────────────────────────────────────────────────────────────
    def _initialize_view_model(self):
        """Initialize and configure the RecipeBrowserViewModel."""
        try:
            self._view_model = RecipeBrowserViewModel()

            # Configure selection mode
            self._view_model.set_selection_mode(self._selection_mode)

            DebugLogger.log("RecipeBrowserViewModel initialized", "debug")

        except Exception as e:
            DebugLogger.log(f"Error initializing RecipeBrowserViewModel: {e}", "error")
            raise

    # ── UI Building Methods ─────────────────────────────────────────────────────────────────────────────────
    def _build_filter_controls(self):
        """Build the filter and sort control section."""
        # Create filter layout
        self._filter_layout = QHBoxLayout()
        self._filter_layout.setSpacing(10)
        self._filter_layout.setContentsMargins(0, 0, 0, 0)

        # Create filter controls
        self._cb_filter = ComboBox(list_items=RECIPE_CATEGORIES, placeholder="Filter")
        self._cb_filter.setObjectName("CategoryFilter")

        self._cb_sort = ComboBox(list_items=SORT_OPTIONS, placeholder="Sort")
        self._cb_sort.setObjectName("SortFilter")

        self._chk_favorites = QCheckBox("Show Favorites Only")
        self._chk_favorites.setObjectName("FavoritesFilter")

        # Add to layout
        self._filter_layout.addWidget(self._cb_filter)
        self._filter_layout.addWidget(self._cb_sort)
        self._filter_layout.addWidget(self._chk_favorites)
        self._filter_layout.addStretch()  # Push controls to left

        # Add to main content layout
        self.content_layout.addLayout(self._filter_layout)

    def _build_recipe_grid(self):
        """Build the scrollable recipe grid section."""
        # Create scroll area for recipes
        self._scroll_area = QScrollArea()
        self._scroll_area.setObjectName("RecipeBrowserScrollArea")
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Set transparent background styles
        self._scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
        """)

        # Create scroll container with flow layout
        self._scroll_container = QWidget()
        self._scroll_container.setObjectName("RecipeBrowserContainer")
        self._scroll_container.setStyleSheet("""
            QWidget#RecipeBrowserContainer {
                background: transparent;
            }
        """)

        # Create flow layout for recipe cards
        self._flow_layout = FlowLayout(self._scroll_container, needAni=False, isTight=True)
        self._scroll_container.setLayout(self._flow_layout)

        # Set container in scroll area
        self._scroll_area.setWidget(self._scroll_container)

        # Add to main content layout
        self.content_layout.addWidget(self._scroll_area)

    def _set_initial_filter_state(self):
        """Set initial filter control states."""
        # Set default sort option
        self._cb_sort.setCurrentText("A-Z")

        # Load initial recipes
        self._load_initial_recipes()

    # ── Recipe Loading Methods ──────────────────────────────────────────────────────────────────────────────────
    def _load_initial_recipes(self):
        """Load recipes with default settings."""
        if self._view_model is None:
            DebugLogger.log("Cannot load recipes: ViewModel not initialized", "error")
            return

        success = self._view_model.load_recipes()
        if not success:
            DebugLogger.log("Failed to load initial recipes", "warning")

    def _reload_with_current_filters(self):
        """Reload recipes based on current filter control states."""
        if self._view_model is None:
            return

        # Update ViewModel with current filter states
        self._view_model.update_category_filter(self._cb_filter.currentText())
        self._view_model.update_sort_option(self._cb_sort.currentText())
        self._view_model.update_favorites_filter(self._chk_favorites.isChecked())

    # ── Recipe Display Methods ──────────────────────────────────────────────────────────────────────────────────
    def _display_recipes(self, recipes: list[Recipe]):
        """
        Display recipes in the grid layout.

        Args:
            recipes: List of Recipe objects to display
        """
        try:
            # Clear existing recipe cards
            self._clear_recipe_cards()

            # Create and add recipe cards
            for recipe in recipes:
                card = create_recipe_card(self._card_size, parent=self._scroll_container)
                card.set_recipe(recipe)

                # Configure card for selection mode
                card.set_selection_mode(self._selection_mode)

                if self._selection_mode:
                    # Selection mode: connect to selection handler
                    card.card_clicked.connect(lambda r=recipe: self._handle_recipe_selection(r))
                    card.setCursor(Qt.PointingHandCursor)
                else:
                    # Browse mode: connect to navigation handler
                    card.card_clicked.connect(lambda r=recipe: self._handle_recipe_opened(r))

                self._flow_layout.addWidget(card)

            # Force layout updates
            self._update_layout_geometry()

            self._recipes_loaded = True
            DebugLogger.log(f"Displayed {len(recipes)} recipe cards", "debug")

        except Exception as e:
            DebugLogger.log(f"Error displaying recipes: {e}", "error")

    def _clear_recipe_cards(self):
        """Remove all recipe cards from the layout."""
        try:
            while self._flow_layout.count():
                child = self._flow_layout.takeAt(0)
                if child and child.widget():
                    child.widget().deleteLater()

            # Force layout update
            self._update_layout_geometry()

            DebugLogger.log("Recipe cards cleared", "debug")

        except Exception as e:
            DebugLogger.log(f"Error clearing recipe cards: {e}", "error")

    def _update_layout_geometry(self):
        """Force layout geometry updates for proper display."""
        if hasattr(self, '_scroll_container'):
            self._scroll_container.updateGeometry()
        if hasattr(self, '_scroll_area'):
            self._scroll_area.updateGeometry()

        # Process pending events for immediate update
        from PySide6.QtCore import QCoreApplication
        QCoreApplication.processEvents()

    # ── Event Handlers ──────────────────────────────────────────────────────────────────────────────────────────
    def _on_category_filter_changed(self, category: str):
        """Handle category filter changes."""
        if self._view_model is None:
            return

        self._view_model.update_category_filter(category)

    def _on_sort_option_changed(self, sort_option: str):
        """Handle sort option changes."""
        if self._view_model is None:
            return

        self._view_model.update_sort_option(sort_option)

    def _on_favorites_filter_changed(self, state: int):
        """Handle favorites filter changes."""
        if self._view_model is None:
            return

        favorites_only = state == Qt.Checked.value
        self._view_model.update_favorites_filter(favorites_only)

    def _handle_recipe_selection(self, recipe: Recipe):
        """Handle recipe selection in selection mode."""
        if recipe is None:
            return

        if self._view_model:
            self._view_model.handle_recipe_selection(recipe)

    def _handle_recipe_opened(self, recipe: Recipe):
        """Handle recipe opening in browse mode."""
        if recipe is None:
            return

        DebugLogger.log(f"Recipe opened: {recipe.recipe_name}", "debug")
        self.recipe_opened.emit(recipe)

    # ── ViewModel Signal Handlers ───────────────────────────────────────────────────────────────────────────
    def _on_recipes_loaded(self, recipes: list[Recipe]):
        """Handle recipes loaded from ViewModel."""
        self._display_recipes(recipes)

    def _on_recipes_cleared(self):
        """Handle recipes cleared from ViewModel."""
        self._clear_recipe_cards()

    def _on_recipe_selected(self, recipe_id: int, recipe: Recipe):
        """Handle recipe selection from ViewModel."""
        DebugLogger.log(f"Recipe selected: {recipe.recipe_name} (ID: {recipe_id})", "debug")
        self.recipe_selected.emit(recipe_id, recipe)

    def _on_selection_mode_changed(self, enabled: bool):
        """Handle selection mode changes from ViewModel."""
        if self._selection_mode != enabled:
            self._selection_mode = enabled
            # Refresh display to update card interaction modes
            if self._recipes_loaded:
                self._reload_with_current_filters()

    def _on_filter_state_changed(self, filter_dto: RecipeFilterDTO):
        """Handle filter state changes from ViewModel."""
        DebugLogger.log(f"Filter state changed: {filter_dto.model_dump()}", "debug")

    def _on_search_completed(self, result_count: int):
        """Handle search completion from ViewModel."""
        DebugLogger.log(f"Search completed: {result_count} results", "debug")

    def _on_view_model_error(self, error_info: Dict[str, Any]):
        """Handle errors from ViewModel."""
        error_msg = error_info.get("message", "Unknown error occurred")
        DebugLogger.log(f"ViewModel error: {error_msg}", "error")

    def _on_loading_changed(self, is_loading: bool):
        """Handle loading state changes from ViewModel."""
        # TODO: Implement loading indicator UI when ViewModel supports loading_changed signal
        DebugLogger.log(f"Loading state: {'Loading' if is_loading else 'Complete'}", "debug")

    # ── Navigation Lifecycle Methods ────────────────────────────────────────────────────────────────────────
    def after_navigate_to(self, path: str, params: Dict[str, str]):
        """
        Called after successfully navigating to this view via navigation service.

        Ensures proper view initialization including ViewModel setup, signal connections,
        and initial data loading. This is part of the navigation lifecycle management.

        Args:
            path (str): The route path that was navigated to (e.g., "/recipes/browse")
            params (Dict[str, str]): Route parameters (future expansion)

        Navigation Integration:
            - Initializes ViewModel if not already done
            - Connects ViewModel signals for UI updates
            - Triggers initial recipe loading if needed
            - Forces layout geometry updates for proper display

        Called by:
            Navigation system after successful route matching and view activation
        """
        super().after_navigate_to(path, params)

        try:
            # Ensure ViewModel is ready
            if self._view_model is None:
                self._initialize_view_model()
                self._connect_view_model_signals()

            # Refresh recipes if needed
            if not self._recipes_loaded:
                self._load_initial_recipes()

            # Force layout update
            self._update_layout_geometry()

            DebugLogger.log(f"RecipeBrowserView navigated to: {path}", "debug")

        except Exception as e:
            DebugLogger.log(f"Error in after_navigate_to: {e}", "error")

    def before_navigate_from(self, next_path: str, next_params: Dict[str, str]) -> bool:
        """Called before navigating away from this view."""
        DebugLogger.log(f"RecipeBrowserView navigating away to: {next_path}", "debug")
        return super().before_navigate_from(next_path, next_params)

    def on_route_changed(self, path: str, params: Dict[str, str]):
        """
        Handle dynamic route parameter changes during navigation.

        Processes route parameters to update view behavior, particularly for
        selection mode configuration. Allows the same view instance to adapt
        to different route configurations dynamically.

        Args:
            path (str): Current route path
            params (Dict[str, str]): Route parameters including:
                - selection_mode: "true"/"false" to enable/disable selection mode

        Behavior:
            - Updates selection mode based on route parameters
            - Configures ViewModel selection mode state
            - Maintains consistency between route and view state

        Route Examples:
            /recipes/browse -> selection_mode=False (default)
            /recipes/browse?selection_mode=true -> selection_mode=True
            /recipes/browse/selection -> handled by wrapper class
        """
        super().on_route_changed(path, params)

        # Handle selection mode parameter
        selection_mode_param = params.get('selection_mode', 'false').lower()
        new_selection_mode = selection_mode_param in ('true', '1', 'yes')

        if new_selection_mode != self._selection_mode:
            self._selection_mode = new_selection_mode
            if self._view_model:
                self._view_model.set_selection_mode(new_selection_mode)

        DebugLogger.log(f"RecipeBrowserView route changed: {path}, params: {params}", "debug")

    # ── Public Interface Methods ────────────────────────────────────────────────────────────────────────────
    def refresh_recipes(self):
        """
        Refresh the recipe display with current filter settings.

        Reloads recipes from the data source using current filter, sort, and search
        settings. Useful for updating the display after external changes or user
        interactions that might affect the recipe collection.

        MVVM Pattern:
            Delegates to ViewModel which handles data loading through RecipeService.
            UI updates occur automatically via ViewModel signals.
        """
        if self._view_model:
            self._view_model.refresh_recipes()

    def clear_recipes(self):
        """
        Clear all recipes from display and reset the view to empty state.

        Removes all recipe cards from the UI and resets internal state.
        Does not affect filter settings - use refresh_recipes() to reload.

        MVVM Pattern:
            Delegates to ViewModel which emits recipes_cleared signal for UI updates.
        """
        if self._view_model:
            self._view_model.clear_recipes()

    def set_selection_mode(self, enabled: bool):
        """
        Set selection mode state for the recipe browser.

        Args:
            enabled (bool): Whether to enable selection mode. When True, recipe
                clicks emit recipe_selected signals. When False, clicks emit
                recipe_opened signals for navigation.

        Integration:
            Used by navigation system and meal planning workflows to switch
            between browsing and selection behaviors dynamically.

        MVVM Pattern:
            Delegates to ViewModel which handles mode state and emits
            selection_mode_changed signal for UI updates.
        """
        if self._view_model:
            self._view_model.set_selection_mode(enabled)

    def search_recipes(self, search_term: str):
        """
        Search recipes by term with current filter settings applied.

        Args:
            search_term (str): Search term to filter recipes by name or content.
                Empty or None clears the search.

        Behavior:
            Combines search with current category and sort filters for refined results.
            Search is applied in real-time with immediate UI updates.

        MVVM Pattern:
            Delegates to ViewModel which coordinates with RecipeService and emits
            search_completed signal with result count.
        """
        if self._view_model:
            self._view_model.search_recipes(search_term)

    def clear_search(self):
        """
        Clear current search and restore filtered view.

        Removes search term while preserving category and sort filters.
        Returns to the full filtered recipe collection view.

        MVVM Pattern:
            Delegates to ViewModel which updates search state and reloads
            recipes with current non-search filters.
        """
        if self._view_model:
            self._view_model.clear_search()

    def get_current_recipe_count(self) -> int:
        """
        Get count of currently displayed recipes.

        Returns:
            int: Number of recipes currently loaded and displayed in the UI.
                 Returns 0 if ViewModel not initialized or no recipes loaded.

        Usage:
            Useful for UI status updates, analytics, or conditional behavior
            based on recipe availability.
        """
        if self._view_model:
            return self._view_model.recipe_count
        return 0

    def is_selection_mode(self) -> bool:
        """
        Check if view is currently in selection mode.

        Returns:
            bool: True if in selection mode (recipe clicks emit recipe_selected),
                  False if in browse mode (recipe clicks emit recipe_opened).

        Usage:
            Used by integration code to determine appropriate signal handling
            and UI behavior configuration.
        """
        return self._selection_mode

    def is_recipes_loaded(self) -> bool:
        """
        Check if recipes have been loaded into the view.

        Returns:
            bool: True if recipes have been successfully loaded and are displayed,
                  False if view is in initial state or loading failed.

        Usage:
            Used for conditional logic in navigation lifecycle and integration
            components to ensure data availability before performing operations.
        """
        return self._recipes_loaded

    # ── Qt Event Overrides ──────────────────────────────────────────────────────────────────────────────────
    def showEvent(self, event):
        """Handle show event to ensure proper layout."""
        super().showEvent(event)

        # Force layout recalculation when widget is shown
        if hasattr(self, '_scroll_container'):
            self._update_layout_geometry()

    def resizeEvent(self, event):
        """Handle resize event to update layout."""
        super().resizeEvent(event)

        # Force layout update on resize with slight delay
        if hasattr(self, '_flow_layout'):
            from PySide6.QtCore import QTimer
            QTimer.singleShot(10, lambda: self._flow_layout.update())

    # ── Cleanup ─────────────────────────────────────────────────────────────────────────────────────────────
    def __del__(self):
        """Cleanup resources when view is destroyed."""
        try:
            if self._view_model:
                # Note: ViewModel cleanup is handled by BaseViewModel.__del__
                self._view_model = None
            DebugLogger.log("RecipeBrowserView cleanup completed", "debug")
        except Exception as e:
            DebugLogger.log(f"Error during RecipeBrowserView cleanup: {e}", "error")
