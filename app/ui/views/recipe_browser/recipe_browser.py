"""app/ui/views/recipe_browser/recipe_browser.py

Standalone recipe browser view for displaying recipes in a grid layout.
"""

# ── Imports ──
from functools import partial
from PySide6.QtCore import Qt, Signal, QCoreApplication

from app.core import RecipeFilterDTO
from app.core.services import RecipeService
from app.ui.components.composite.recipe_card import LayoutSize, create_recipe_card
from app.ui.components.layout.flow_layout import FlowLayoutContainer
from app.ui.views.base import BaseView
from ._filter_bar import FilterBar


class RecipeBrowser(BaseView):
    """Standalone recipe browser view with filtering and sorting."""

    recipe_card_clicked = Signal(object)  # recipe object
    recipe_selected = Signal(int)  # recipe ID

    def __init__(self, parent=None, card_size=LayoutSize.MEDIUM, selection_mode=False, navigation_service=None):
        """
        Initialize the RecipeBrowser.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
            card_size (LayoutSize, optional):
                Size of recipe cards. Defaults to LayoutSize.MEDIUM.
            selection_mode (bool, optional):
                If True, cards are clickable for selection. Defaults to False.
            navigation_service (NavigationService, optional): Service for handling navigation.
        """
        super().__init__(parent)
        self.setObjectName("RecipeBrowser")
        self.card_size = card_size
        self._selection_mode = selection_mode  # if True, cards are clickable for selection
        self.recipe_service = RecipeService()
        self.recipes_loaded = False
        self.navigation_service = navigation_service

        self._build_ui()
        self._load_recipes()

    @property
    def selection_mode(self):
        """Get the current selection mode."""
        return self._selection_mode

    @selection_mode.setter
    def selection_mode(self, value):
        """Set selection mode and refresh cards if needed."""
        if self._selection_mode != value:
            self._selection_mode = value
            # Refresh the recipe display to update card behavior
            # Only refresh if we're switching TO selection mode, not away from it
            if self.recipes_loaded and value:
                self._load_filtered_sorted_recipes()

    def _emit_recipe_selected(self, recipe):
        """Helper method to emit recipe_selected signal with recipe ID."""
        self.recipe_selected.emit(recipe.id)

    def _build_ui(self):
        """Build the UI with filters and recipe grid."""
        self._create_filter_bar()
        # Create the flow layout container
        self._flow_container = FlowLayoutContainer(tight=True)
        self._flow_container.setObjectName("RecipeFlowContainer")

        # Add the container to the existing content_layout
        self.content_layout.addWidget(self._flow_container)

    def _create_filter_bar(self):
        """Create and add the filter bar above the recipe grid."""
        self.filter_bar = FilterBar(self)
        self.content_layout.addWidget(self.filter_bar)
        self.filter_bar.filters_changed.connect(self._load_filtered_sorted_recipes)

    def _load_recipes(self):
        """Load recipes with default filter."""
        default_filter_dto = RecipeFilterDTO(
            recipe_category=None,
            sort_by="recipe_name",
            sort_order="asc",
            favorites_only=False
        )
        self._fetch_and_display_recipes(default_filter_dto)

    def _load_filtered_sorted_recipes(self):
        """Load recipes based on current filter/sort selections."""
        # Get the current filter state using the method
        filter_state = self.filter_bar.getFilterState()

        # Process the filter state
        recipe_category = filter_state['category']
        if not recipe_category or recipe_category in ("All", "Filter"):
            recipe_category = None

        sort_label = filter_state['sort']
        sort_map = {
            "A-Z": "recipe_name",
            "Z-A": "recipe_name",
            "Newest": "created_at",
            "Oldest": "created_at",
            "Shortest Time": "total_time",
            "Longest Time": "total_time",
            "Most Servings": "servings",
            "Fewest Servings": "servings",
        }

        filter_dto = RecipeFilterDTO(
            recipe_category=recipe_category,
            sort_by=sort_map.get(sort_label, "recipe_name"),
            sort_order="desc" if sort_label in ("Z-A",) else "asc",
            favorites_only=filter_state['favorites_only'],
        )
        self._fetch_and_display_recipes(filter_dto)

    def _fetch_and_display_recipes(self, filter_dto: RecipeFilterDTO):
        """
        Fetch and display recipes using the filter DTO.

        Args:
            filter_dto (RecipeFilterDTO): The filter and sort criteria.
        """
        self._clear_recipe_cards()

        recipes = self.recipe_service.list_filtered(filter_dto)

        for recipe in recipes:
            # Create card with flow container as parent
            card = create_recipe_card(self.card_size, parent=self._flow_container)
            card.set_recipe(recipe)

            # Set selection mode on the card
            card.set_selection_mode(self._selection_mode)

            if self._selection_mode:
                # connect card click behavior for selection
                # Use partial to avoid lambda closure issues
                card.card_clicked.connect(partial(self._emit_recipe_selected, recipe))

                # add visual feedback for selection mode
                # show pointer cursor on hover
                card.setCursor(Qt.PointingHandCursor)
            else:
                # normal card behavior (navigate to full recipe via navigation service)
                if self.navigation_service:
                    card.card_clicked.connect(self.navigation_service.show_full_recipe)
                else:
                    # fallback: emit signal for external handling
                    card.card_clicked.connect(self.recipe_card_clicked.emit)

            # Add to the flow container
            self._flow_container.addWidget(card)

        self.recipes_loaded = True

        # Force the container to update and recalculate its geometry
        self._flow_container.updateGeometry()
        self.scroll_area.updateGeometry()

        # Process any pending events to ensure proper layout
        QCoreApplication.processEvents()

    def _clear_recipe_cards(self):
        """Clear all existing recipe cards from the flow layout."""
        self._flow_container.takeAllWidgets()

    def refresh(self):
        """Refresh the recipe display."""
        self.recipes_loaded = False
        self._load_recipes()

    def showEvent(self, event):
        """Handle show event to ensure proper layout."""
        super().showEvent(event)
        # Force layout recalculation when widget is shown
        if hasattr(self, '_flow_container'):
            self._flow_container.updateGeometry()
            self.scroll_area.updateGeometry()

    def resizeEvent(self, event):
        """Handle resize event to update layout."""
        super().resizeEvent(event)
        # Force layout update on resize
        if hasattr(self, '_flow_container'):
            from PySide6.QtCore import QTimer
            # Use the flow container's layout for update
            QTimer.singleShot(10, lambda: self._flow_container.layout.update())
