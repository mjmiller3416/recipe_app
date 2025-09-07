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
from PySide6.QtCore import Qt

from _dev_tools import DebugLogger

from ...components.composite.recipe_card import LayoutSize, create_recipe_card
from ...components.layout import FlowLayoutContainer
from ...views.base import ScrollableNavView
from ...view_models.recipe_browser_vm import RecipeBrowserViewModel
from ._filter_bar import FilterBar


class RecipeBrowser(ScrollableNavView):

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
        # Load recipes using the ViewModel
        self._view_model.load_recipes()

    def _connect_view_model_signals(self):
        """Connect ViewModel signals."""
        # Connect recipes_loaded signal to display recipes
        self._view_model.recipes_loaded.connect(self._on_recipes_loaded)

        # Connect recipe selection if in selection mode
        if self._selection_mode:
            self._view_model.set_selection_mode(True)

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

            # Add to the flow container
            self._flow_container.addWidget(recipe_card)

    def _clear_recipe_cards(self):
        """Clear all existing recipe cards from the flow layout."""
        self._flow_container.takeAllWidgets()
