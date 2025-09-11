"""app/ui/views/recipe_browser/recipe_browser.py

Standalone recipe browser view for displaying recipes in a grid layout.
"""

# ── Imports ──
from PySide6.QtCore import Qt, Signal

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
        """Set selection mode and update existing cards' behavior."""
        if self._selection_mode != value:
            self._selection_mode = value
            if self.recipes_loaded:
                self._update_cards_selection_mode()

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
        filter_state = self.filter_bar.getFilterState()

        # Simplify category processing
        recipe_category = None if filter_state['category'] in (None, "All", "Filter") else filter_state['category']

        # Simplified sort mapping
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
        
        sort_by = sort_map.get(sort_label, "recipe_name")
        sort_order = "desc" if sort_label in ("Z-A", "Newest", "Longest Time", "Most Servings") else "asc"

        filter_dto = RecipeFilterDTO(
            recipe_category=recipe_category,
            sort_by=sort_by,
            sort_order=sort_order,
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
            card = self._create_recipe_card(recipe)
            self._flow_container.addWidget(card)

        self.recipes_loaded = True
        self._update_layout()

    def _create_recipe_card(self, recipe):
        """Create and configure a recipe card.
        
        Args:
            recipe: The recipe data object.
            
        Returns:
            Configured recipe card widget.
        """
        card = create_recipe_card(self.card_size, parent=self._flow_container)
        card.set_recipe(recipe)
        card.set_selection_mode(self._selection_mode)
        
        # Store recipe reference for later use
        card.recipe_data = recipe
        
        self._setup_card_behavior(card, recipe)
        return card
    
    def _setup_card_behavior(self, card, recipe):
        """Setup click behavior for a recipe card based on current mode.
        
        Args:
            card: The recipe card widget.
            recipe: The recipe data object.
        """
        # Disconnect any existing connections
        try:
            card.card_clicked.disconnect()
        except (RuntimeError, TypeError):
            pass  # No connections to disconnect
        
        if self._selection_mode:
            # Selection mode: emit recipe ID when clicked
            card.card_clicked.connect(lambda: self.recipe_selected.emit(recipe.id))
            card.setCursor(Qt.PointingHandCursor)
        else:
            # Normal mode: navigate or emit signal
            if self.navigation_service:
                card.card_clicked.connect(self.navigation_service.show_full_recipe)
            else:
                card.card_clicked.connect(self.recipe_card_clicked.emit)
            card.setCursor(Qt.ArrowCursor)
    
    def _update_cards_selection_mode(self):
        """Update all existing recipe cards to match current selection mode."""
        if not hasattr(self, '_flow_container'):
            return
            
        # Update each card's behavior without reloading data
        for i in range(self._flow_container.layout.count()):
            item = self._flow_container.layout.itemAt(i)
            if item:
                card = item.widget()
                if card and hasattr(card, 'recipe_data'):
                    card.set_selection_mode(self._selection_mode)
                    self._setup_card_behavior(card, card.recipe_data)

    def _update_layout(self):
        """Update the flow container and scroll area layouts."""
        if hasattr(self, '_flow_container'):
            self._flow_container.updateGeometry()
            if hasattr(self, 'scroll_area'):
                self.scroll_area.updateGeometry()

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
        self._update_layout()

    def resizeEvent(self, event):
        """Handle resize event to update layout."""
        super().resizeEvent(event)
        if hasattr(self, '_flow_container'):
            from PySide6.QtCore import QTimer
            QTimer.singleShot(10, self._flow_container.layout.update)
