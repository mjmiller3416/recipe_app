"""app/ui/components/composite/recipe_browser.py

RecipeBrowser - Reusable recipe browser component for embedded recipe display.

This component provides recipe browsing functionality for embedding within other views
or dialogs. It offers basic filtering, sorting, and recipe display capabilities with
a simpler architecture compared to the full RecipeBrowserView.

## Architecture Relationship

- **RecipeBrowserView**: Full MainView with MVVM pattern, navigation integration
- **RecipeBrowser (this component)**: Embeddable component with direct service access

Both serve similar purposes but with different architectural approaches:

### RecipeBrowserView (MainView)
- Full MVVM architecture with ViewModel layer
- Navigation system integration and lifecycle management
- Advanced signal architecture and state management
- Designed for full-screen navigation experiences
- Route-based initialization and configuration

### RecipeBrowser (Component)
- Direct RecipeService access for simpler integration
- Embeddable within other views and dialogs
- Lightweight with essential features only
- Event-based signal patterns
- Constructor-based configuration only

## When to Use Each

**Use RecipeBrowserView when:**
- Building full-screen recipe browsing experiences
- Navigation integration is required
- Complex state management needed
- MVVM pattern compliance is important
- Route-based configuration is beneficial

**Use RecipeBrowser (this component) when:**
- Embedding recipe browsing in dialogs or other views
- Simple recipe selection workflows
- Lighter weight integration is preferred
- Direct control over initialization is needed
- MVVM overhead is not justified

## Migration Path

Components using RecipeBrowser can be migrated to RecipeBrowserView:

```python
# Old approach with RecipeBrowser component
browser = RecipeBrowser(selection_mode=True, card_size=LayoutSize.LARGE)
browser.recipe_selected.connect(handle_selection)

# New approach with RecipeBrowserView
browser = RecipeBrowserView(selection_mode=True, card_size=LayoutSize.LARGE)
browser.recipe_selected.connect(handle_selection)
```

The APIs are designed to be similar for easier migration.

See Also:
- `RecipeBrowserView`: Full MainView implementation with MVVM pattern
- `RecipeBrowserViewModel`: ViewModel for advanced recipe browsing
- Navigation system documentation
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QScrollArea, QVBoxLayout, QWidget

from app.config import RECIPE_CATEGORIES, SORT_OPTIONS
from app.core.dtos import RecipeFilterDTO
from app.core.services.recipe_service import RecipeService
from app.ui.components.composite.recipe_card import LayoutSize, create_recipe_card
from app.ui.components.layout.flow_layout import FlowLayout
from app.ui.components.widgets import ComboBox

# ── Recipe Browser ──────────────────────────────────────────────────────────────────────────────────────────
class RecipeBrowser(QWidget):
    """
    Lightweight recipe browser component for embedded use cases.
    
    This component provides basic recipe browsing functionality with filtering
    and sorting capabilities. Designed for embedding within other views, dialogs,
    or components where full MVVM architecture is not required.
    
    Key Features:
    - Category and favorites filtering
    - Multiple sorting options (A-Z, date, time, servings)
    - Selection mode for recipe picking workflows
    - Direct RecipeService integration for simplicity
    - Configurable card sizing and layout
    
    Architecture:
    - Direct service access (no ViewModel layer)
    - Simple signal-based communication
    - Lightweight initialization and lifecycle
    - Constructor-based configuration only
    
    Signals:
        recipe_card_clicked(Recipe): Recipe card clicked in browse mode
        recipe_selected(int): Recipe selected in selection mode (recipe ID)
        
    Comparison with RecipeBrowserView:
        RecipeBrowser: Embeddable component, direct service access, lighter weight
        RecipeBrowserView: Full MainView, MVVM pattern, navigation integration
        
    Usage:
        # Basic browsing
        browser = RecipeBrowser()
        browser.recipe_card_clicked.connect(handle_recipe_open)
        
        # Selection mode for dialogs
        browser = RecipeBrowser(selection_mode=True)
        browser.recipe_selected.connect(handle_recipe_selection)
    """

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
