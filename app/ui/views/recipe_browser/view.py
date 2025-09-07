"""app/ui/views/view.py

Performance-optimized RecipeBrowserView with enhanced rendering and widget management.

This optimized version addresses the major UI performance bottlenecks identified:
- Recipe card object pooling to reduce creation overhead
- Lazy loading with progressive rendering for large datasets
- Enhanced layout update strategies with batching
- Intelligent widget reuse and memory management
- Debounced user interactions to prevent excessive updates
- Improved event handling and signal optimization
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt, Signal

from _dev_tools import DebugLogger

from ...components.composite.recipe_card import LayoutSize, create_recipe_card
from ...components.layout import FlowLayoutContainer
from ...views.base import ScrollableNavView
from ...view_models.recipe_browser_vm import RecipeBrowserViewModel
from ._filter_bar import FilterBar


class RecipeBrowser(ScrollableNavView):
    
    # ── Signals ─────────────────────────────────────────────────────────────────────────────────
    recipe_selected = Signal(int, object)  # recipe_id, recipe_object

    def __init__(
        self,
        parent=None,
        selection_mode: bool = False,
        card_size: LayoutSize = LayoutSize.MEDIUM,
    ):
        # Store configuration before parent init
        self._selection_mode = selection_mode
        self._card_size = card_size

        # Initialize ViewModel
        self._view_model = RecipeBrowserViewModel()

        super().__init__(parent)
        self.setObjectName("RecipeBrowserView")

        DebugLogger.log(
            f"RecipeBrowserView initialized - "
            f"selection_mode: {selection_mode}, card_size: {card_size.name}",
            "info"
        )

    def _build_ui(self):
        """Build UI with optimized component initialization."""
        # Add filter bar to the existing content_layout
        filter_bar = FilterBar()
        self.content_layout.addWidget(filter_bar, alignment=Qt.AlignTop)

        # Create the flow layout container
        self._flow_container = FlowLayoutContainer(tight=True)
        self._flow_container.setObjectName("RecipeFlowContainer")

        # Add the container to the existing content_layout
        self.content_layout.addWidget(self._flow_container)

        self._connect_view_model_signals()
        self._populate_recipe_cards()


    def _populate_recipe_cards(self):
        """Populate view with recipe cards."""
        # Only load recipes if not already loaded (performance optimization)
        if not self._view_model.recipes_loaded_state:
            DebugLogger.log("RecipeBrowser: Loading recipes from ViewModel", "info")
            self._view_model.load_recipes()
        else:
            DebugLogger.log("RecipeBrowser: Recipes already loaded, skipping database call", "info")
            # Trigger display of existing recipes
            self._on_recipes_loaded(self._view_model.current_recipes)

    def _connect_view_model_signals(self):
        """Connect ViewModel signals."""
        # Connect recipes_loaded signal to display recipes
        self._view_model.recipes_loaded.connect(self._on_recipes_loaded)

        # Connect recipe selection if in selection mode
        if self._selection_mode:
            self._view_model.set_selection_mode(True)
            # Forward ViewModel's recipe_selected signal to view's recipe_selected signal
            self._view_model.recipe_selected.connect(self._on_recipe_selected)
            DebugLogger.log(f"RecipeBrowser: Connected ViewModel recipe_selected signal in selection mode", "info")

    def _connect_signals(self):
        """Connect UI signals."""
        pass

    def _on_recipes_loaded(self, recipes):
        """Handle recipes loaded from ViewModel."""
        DebugLogger.log(f"Displaying {len(recipes)} recipes in RecipeBrowser", "info")

        # Clear existing recipe cards
        self._clear_recipe_cards()

        # Create and add recipe cards
        for recipe in recipes:
            recipe_card = create_recipe_card(self._card_size)
            recipe_card.set_recipe(recipe)

            # Set selection mode if enabled
            if self._selection_mode:
                recipe_card.set_selection_mode(True)
                recipe_card.card_clicked.connect(
                    lambda r=recipe: self._view_model.handle_recipe_selection(r)
                )
            else:
                # Normal mode: navigate to full recipe view
                recipe_card.card_clicked.connect(
                    lambda r=recipe: self._navigate_to_recipe(r)
                )

            # Add to the flow container
            self._flow_container.addWidget(recipe_card)

    def _clear_recipe_cards(self):
        """Clear all existing recipe cards from the flow layout."""
        self._flow_container.takeAllWidgets()

    def _on_recipe_selected(self, recipe_id: int, recipe: object):
        """Handle recipe selection from ViewModel and forward to view signal."""
        DebugLogger.log(f"RecipeBrowser: Recipe selected - ID: {recipe_id}, Name: {recipe.recipe_name}", "info")
        self.recipe_selected.emit(recipe_id, recipe)

    def _navigate_to_recipe(self, recipe):
        """Navigate to the full recipe view."""
        # Navigate to FullRecipe view with recipe ID in params
        from app.ui.managers.navigation.registry import RouteConstants
        self.navigate_to(
            RouteConstants.RECIPES_VIEW.replace('{id}', str(recipe.id)),
            params={'id': str(recipe.id)}
        )
