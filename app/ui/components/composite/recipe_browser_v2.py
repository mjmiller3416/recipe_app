"""app/ui/components/composite/recipe_browser_v2.py

Enhanced RecipeBrowser that supports both embedded and standalone navigation modes.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QScrollArea, QVBoxLayout, QWidget

from app.config import RECIPE_CATEGORIES, SORT_OPTIONS
from app.core.dtos import RecipeFilterDTO
from app.core.services.recipe_service import RecipeService
from app.ui.components.composite.recipe_card import create_recipe_card, LayoutSize
from app.ui.components.layout.flow_layout import FlowLayout
from app.ui.components.widgets import ComboBox
from app.ui.services.navigation_views import EmbeddedView
from app.ui.services.navigation_registry import NavigationRegistry, ViewType


class RecipeBrowser(EmbeddedView):
    """
    Enhanced recipe browser that can work as both embedded component and standalone view.

    This demonstrates how to migrate existing components to the new navigation system
    while maintaining backward compatibility.
    """

    recipe_card_clicked = Signal(object)  # recipe object
    recipe_selected = Signal(int)  # recipe ID

    def __init__(self, parent=None, card_size=LayoutSize.MEDIUM, selection_mode=False):
        super().__init__(parent)
        self.setObjectName("RecipeBrowser")
        self.card_size = card_size
        self.selection_mode = selection_mode
        self.recipe_service = RecipeService()
        self.recipes_loaded = False

        self.build_ui()
        self.load_recipes()

    def build_ui(self):
        """Build the UI with filters and recipe grid."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(10)

        # Filter and sort controls
        self.lyt_cb = QHBoxLayout()
        self.lyt_cb.setSpacing(10)

        self.cb_filter = ComboBox(list_items=RECIPE_CATEGORIES, placeholder="Filter")
        self.cb_sort = ComboBox(list_items=SORT_OPTIONS, placeholder="Sort")
        self.chk_favorites = QCheckBox("Show Favorites Only")

        self.lyt_cb.addWidget(self.cb_filter)
        self.lyt_cb.addWidget(self.cb_sort)
        self.lyt_cb.addWidget(self.chk_favorites)

        # Connect signals
        self.cb_filter.currentTextChanged.connect(self.load_filtered_sorted_recipes)
        self.cb_sort.currentTextChanged.connect(self.load_filtered_sorted_recipes)
        self.chk_favorites.stateChanged.connect(self.load_filtered_sorted_recipes)

        # Recipe grid
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("RecipeBrowserScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
        """)

        self.scroll_container = QWidget()
        self.scroll_container.setObjectName("RecipeBrowserContainer")
        self.scroll_container.setStyleSheet("""
            QWidget#RecipeBrowserContainer {
                background: transparent;
            }
        """)
        self.flow_layout = FlowLayout(self.scroll_container, needAni=False, isTight=True)
        self.scroll_container.setLayout(self.flow_layout)

        self.scroll_area.setWidget(self.scroll_container)

        self.main_layout.addLayout(self.lyt_cb)
        self.main_layout.addWidget(self.scroll_area)

        # Set initial sort
        self.cb_sort.setCurrentText("A-Z")

    def load_recipes(self):
        """Load recipes with default filter."""
        default_filter_dto = RecipeFilterDTO(
            recipe_category=None,
            sort_by="recipe_name",
            sort_order="asc",
            favorites_only=False
        )
        self._fetch_and_display_recipes(default_filter_dto)

    def load_filtered_sorted_recipes(self):
        """Load recipes based on current filter/sort selections."""
        recipe_category = self.cb_filter.currentText()
        if not recipe_category or recipe_category in ("All", "Filter"):
            recipe_category = None

        sort_label = self.cb_sort.currentText()
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
            favorites_only=self.chk_favorites.isChecked(),
        )
        self._fetch_and_display_recipes(filter_dto)

    def _fetch_and_display_recipes(self, filter_dto: RecipeFilterDTO):
        """Fetch and display recipes using the filter DTO."""
        self.clear_recipe_display()

        recipes = self.recipe_service.list_filtered(filter_dto)

        for recipe in recipes:
            card = create_recipe_card(self.card_size, parent=self.scroll_container)
            card.set_recipe(recipe)

            # Set selection mode on the card
            card.set_selection_mode(self.selection_mode)

            if self.selection_mode:
                # Connect card click behavior for selection
                card.card_clicked.connect(lambda r: self.recipe_selected.emit(r.id))
                card.setCursor(Qt.PointingHandCursor)
            else:
                # Normal card behavior - handle based on standalone mode
                card.card_clicked.connect(self._handle_recipe_card_click)

            self.flow_layout.addWidget(card)

        self.recipes_loaded = True

        # Force the scroll area to update and recalculate its geometry
        self.scroll_container.updateGeometry()
        self.scroll_area.updateGeometry()
        from PySide6.QtCore import QCoreApplication
        QCoreApplication.processEvents()

    def _handle_recipe_card_click(self, recipe):
        """Handle recipe card clicks based on navigation mode."""
        if self.is_standalone():
            # In standalone mode, use navigation system
            self.navigate_to(f"/recipes/view/{recipe.id}")
        else:
            # In embedded mode, emit signal for parent to handle
            self.recipe_card_clicked.emit(recipe)

    def clear_recipe_display(self):
        """Remove all recipe cards from the layout."""
        while self.flow_layout.count():
            widget = self.flow_layout.takeAt(0)
            if widget:
                widget.deleteLater()
        self.scroll_container.updateGeometry()

    def refresh(self):
        """Refresh the recipe display."""
        self.recipes_loaded = False
        self.load_recipes()

    def set_selection_mode(self, selection_mode: bool):
        """Update selection mode and refresh display."""
        if self.selection_mode != selection_mode:
            self.selection_mode = selection_mode
            self.refresh()

    def showEvent(self, event):
        """Handle show event to ensure proper layout."""
        super().showEvent(event)
        if hasattr(self, 'scroll_container'):
            self.scroll_container.updateGeometry()
            self.scroll_area.updateGeometry()

    def resizeEvent(self, event):
        """Handle resize event to update layout."""
        super().resizeEvent(event)
        if hasattr(self, 'flow_layout'):
            from PySide6.QtCore import QTimer
            QTimer.singleShot(10, lambda: self.flow_layout.update())

    # EmbeddedView overrides for navigation support
    def on_standalone_changed(self, standalone: bool):
        """Called when standalone mode changes."""
        super().on_standalone_changed(standalone)
        from _dev_tools import DebugLogger

        if standalone:
            DebugLogger.log("RecipeBrowser switched to standalone mode", "info")
            # Refresh to update click behaviors
            self.refresh()
        else:
            DebugLogger.log("RecipeBrowser switched to embedded mode", "info")

    def on_route_changed(self, path: str, params: dict):
        """Handle route changes in standalone mode."""
        super().on_route_changed(path, params)

        # Handle any route-specific parameters
        if params.get('category'):
            category = params['category']
            self.cb_filter.setCurrentText(category.title())

        if params.get('sort'):
            sort_option = params['sort']
            self.cb_sort.setCurrentText(sort_option)

    def before_navigate_to(self, path: str, params: dict) -> bool:
        """Called before navigating to this browser."""
        from _dev_tools import DebugLogger
        DebugLogger.log("Preparing to show recipe browser", "info")
        return True

    def after_navigate_to(self, path: str, params: dict):
        """Called after navigating to this browser."""
        from _dev_tools import DebugLogger
        DebugLogger.log("Recipe browser is now active", "info")

        # Ensure recipes are loaded
        if not self.recipes_loaded:
            self.load_recipes()


# Register as a standalone navigable view
@NavigationRegistry.register(
    path="/recipes/browser",
    view_type=ViewType.EMBEDDED,
    title="Recipe Browser",
    description="Browse recipes with filtering and sorting"
)
class StandaloneRecipeBrowser(RecipeBrowser):
    """Standalone version of RecipeBrowser for direct navigation."""

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        # This will be automatically set to standalone mode by the navigation system
        # when accessed via route
