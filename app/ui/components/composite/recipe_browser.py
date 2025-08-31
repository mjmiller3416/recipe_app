"""app/ui/components/composite/recipe_browser.py

Shared recipe browser component for displaying recipes in a grid layout.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QScrollArea, QVBoxLayout, QWidget

from app.config import RECIPE_CATEGORIES, SORT_OPTIONS
from app.core.dtos import RecipeFilterDTO
from app.core.services.recipe_service import RecipeService
from app.ui.components.composite.recipe_card import create_recipe_card, LayoutSize
from app.ui.components.layout.flow_layout import FlowLayout
from app.ui.components.widgets import ComboBox


# ── Recipe Browser ──────────────────────────────────────────────────────────────────────────────────────────
class RecipeBrowser(QWidget):
    """Reusable recipe browser component with filtering and sorting."""

    recipe_card_clicked = Signal(object)  # recipe object
    recipe_selected = Signal(int)  # recipe ID

    def __init__(self, parent=None, card_size=LayoutSize.MEDIUM, selection_mode=False):
        """
        Initialize the RecipeBrowser.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
            card_size (LayoutSize, optional):
                Size of recipe cards. Defaults to LayoutSize.MEDIUM.
            selection_mode (bool, optional):
                If True, cards are clickable for selection. Defaults to False.
        """
        super().__init__(parent)
        self.setObjectName("RecipeBrowser")
        self.card_size = card_size
        self.selection_mode = selection_mode  # if True, cards are clickable for selection
        self.recipe_service = RecipeService()
        self.recipes_loaded = False

        self.build_ui()
        self.load_recipes()

    def build_ui(self):
        """Build the UI with filters and recipe grid."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(10)

        # filter and sort controls
        self.lyt_cb = QHBoxLayout()
        self.lyt_cb.setSpacing(10)

        self.cb_filter = ComboBox(list_items=RECIPE_CATEGORIES, placeholder="Filter")
        self.cb_sort = ComboBox(list_items=SORT_OPTIONS, placeholder="Sort")
        self.chk_favorites = QCheckBox("Show Favorites Only")

        self.lyt_cb.addWidget(self.cb_filter)
        self.lyt_cb.addWidget(self.cb_sort)
        self.lyt_cb.addWidget(self.chk_favorites)

        # connect signals
        self.cb_filter.currentTextChanged.connect(self.load_filtered_sorted_recipes)
        self.cb_sort.currentTextChanged.connect(self.load_filtered_sorted_recipes)
        self.chk_favorites.stateChanged.connect(self.load_filtered_sorted_recipes)

        # recipe grid
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("RecipeBrowserScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # Set transparent backgrounds to inherit from parent
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
        # Ensure container is transparent and takes full width
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

        # set initial sort
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
        """
        Fetch and display recipes using the filter DTO.

        Args:
            filter_dto (RecipeFilterDTO): The filter and sort criteria.
        """
        self.clear_recipe_display()

        recipes = self.recipe_service.list_filtered(filter_dto)

        for recipe in recipes:
            card = create_recipe_card(self.card_size, parent=self.scroll_container)
            card.set_recipe(recipe)

            # Set selection mode on the card
            card.set_selection_mode(self.selection_mode)

            if self.selection_mode:
                # connect card click behavior for selection
                card.card_clicked.connect(lambda r: self.recipe_selected.emit(r.id))

                # add visual feedback for selection mode
                # TODO: create hover effect in stylesheet
                # show pointer cursor on hover
                card.setCursor(Qt.PointingHandCursor)
            else:
                # normal card behavior (opens full recipe)
                card.card_clicked.connect(self.recipe_card_clicked.emit)

            self.flow_layout.addWidget(card)

        self.recipes_loaded = True

        # Force the scroll area to update and recalculate its geometry
        self.scroll_container.updateGeometry()
        self.scroll_area.updateGeometry()
        # Process any pending events to ensure proper layout
        from PySide6.QtCore import QCoreApplication
        QCoreApplication.processEvents()

    def clear_recipe_display(self):
        """Remove all recipe cards from the layout."""
        while self.flow_layout.count():
            widget = self.flow_layout.takeAt(0)
            if widget:
                widget.deleteLater()

        # Force layout update after clearing
        self.scroll_container.updateGeometry()

    def refresh(self):
        """Refresh the recipe display."""
        self.recipes_loaded = False
        self.load_recipes()

    def showEvent(self, event):
        """Handle show event to ensure proper layout."""
        super().showEvent(event)
        # Force layout recalculation when widget is shown
        if hasattr(self, 'scroll_container'):
            self.scroll_container.updateGeometry()
            self.scroll_area.updateGeometry()

    def resizeEvent(self, event):
        """Handle resize event to update layout."""
        super().resizeEvent(event)
        # Force layout update on resize
        if hasattr(self, 'flow_layout'):
            from PySide6.QtCore import QTimer
            QTimer.singleShot(10, lambda: self.flow_layout.update())
