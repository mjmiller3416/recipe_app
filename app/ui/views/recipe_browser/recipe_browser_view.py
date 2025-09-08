"""app/ui/views/recipe_browser/recipe_browser_view.py

Simplified RecipeBrowser view for displaying recipe cards.
"""

from PySide6.QtCore import Qt, Signal

from _dev_tools import DebugLogger
from app.ui.components.composite.recipe_card import LayoutSize, create_recipe_card
from app.ui.components.layout import FlowLayoutContainer
from app.ui.views.base import ScrollableNavView
from app.ui.view_models.recipe_browser_vm import RecipeBrowserViewModel
from ._filter_bar import FilterBar

class RecipeBrowserView(ScrollableNavView):
    """Recipe browser view for displaying and selecting recipes."""

    recipe_selected = Signal(int, object)  # For meal planner selection mode

    def __init__(self, parent=None, selection_mode: bool = False, card_size: LayoutSize = LayoutSize.MEDIUM):
        # Store configuration
        self._selection_mode = selection_mode
        self._card_size = card_size

        # Initialize ViewModel
        self._view_model = RecipeBrowserViewModel()

        super().__init__(parent)
        self.setObjectName("RecipeBrowserView")
        DebugLogger.log("RecipeBrowserView initialized - selection_mode: {selection_mode}", "info")

        self._build_ui()

    def _build_ui(self):
        """Build UI components."""
        # Add filter bar
        filter_bar = FilterBar()
        self.content_layout.addWidget(filter_bar, alignment=Qt.AlignTop)

        # Create flow container for recipe cards
        self._flow_container = FlowLayoutContainer(tight=True)
        self._flow_container.setObjectName("RecipeFlowContainer")
        self.content_layout.addWidget(self._flow_container)

        # Connect signals and load recipes
        self._connect_signals()
        self._load_recipes()

    def _connect_signals(self):
        """Connect ViewModel signals."""
        self._view_model.recipes_loaded.connect(self._display_recipes)

        if self._selection_mode:
            self._view_model.set_selection_mode(True)
            self._view_model.recipe_selected.connect(
                lambda id, recipe: self.recipe_selected.emit(id, recipe)
            )

    def _load_recipes(self):
        """Load recipes from ViewModel."""
        if not self._view_model.recipes_loaded_state:
            DebugLogger.log("Loading recipes from database", "info")
            self._view_model.load_recipes()
        else:
            DebugLogger.log("Using cached recipes", "info")
            self._display_recipes(self._view_model.current_recipes)

    def _display_recipes(self, recipes):
        """Display recipe cards."""
        DebugLogger.log(f"Displaying {len(recipes)} recipes, selection_mode={self._selection_mode}", "info")

        # Clear existing cards
        self._flow_container.takeAllWidgets()

        # Create cards for each recipe
        for recipe in recipes:
            card = create_recipe_card(self._card_size)
            card.set_recipe(recipe)

            if self._selection_mode:
                DebugLogger.log(f"Setting up card for selection mode: {recipe.recipe_name}", "debug")
                card.set_selection_mode(True)
                card.card_clicked.connect(
                    lambda r=recipe: self._view_model.handle_recipe_selection(r)
                )
            else:
                DebugLogger.log(f"Setting up card for normal mode: {recipe.recipe_name}", "debug")
                card.card_clicked.connect(
                    lambda r=recipe: self._navigate_to_recipe(r)
                )

            self._flow_container.addWidget(card)

    def _navigate_to_recipe(self, recipe):
        """Navigate to recipe detail view."""
        main_window = self.window()
        if hasattr(main_window, 'nav'):
            # Pass recipe ID to view_recipe
            main_window.nav.show("view_recipe", recipe_id=recipe.id)
        else:
            DebugLogger.log("No navigator found", "warning")

    def load_data(self, **kwargs):
        """Handle data passed from navigator."""
        DebugLogger.log(f"RecipeBrowser.load_data called with kwargs: {kwargs}", "info")

        if 'selection_mode' in kwargs:
            # Update selection mode
            old_mode = self._selection_mode
            self._selection_mode = kwargs['selection_mode']

            DebugLogger.log(f"Selection mode changed from {old_mode} to {self._selection_mode}", "info")

            # Update ViewModel
            self._view_model.set_selection_mode(self._selection_mode)

            # Reconnect the signal if in selection mode
            if self._selection_mode:
                # Safely disconnect any existing connection
                try:
                    self._view_model.recipe_selected.disconnect()
                except (TypeError, RuntimeError):
                    pass  # No connection existed, which is fine

                self._view_model.recipe_selected.connect(
                    lambda id, recipe: self.recipe_selected.emit(id, recipe)
                )
                DebugLogger.log("Connected recipe_selected signal", "info")

            # Always redisplay to update card connections
            self._display_recipes(self._view_model.current_recipes)
