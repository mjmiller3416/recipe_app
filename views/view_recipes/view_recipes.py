"""views/view_recipes/view_recipes.py

This module defines the ViewRecipes class, which displays a list of recipes in a scrollable layout.
"""


# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QPoint, QRect, QSize, Qt, Signal
from PySide6.QtWidgets import (QCheckBox, QHBoxLayout, QLayout, QScrollArea,
                               QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

from config import RECIPE_CATEGORIES, SORT_OPTIONS
from database.models.recipe import Recipe
from recipe_viewer.constants import LayoutSize
from recipe_viewer.recipe_viewer import RecipeViewer
from services.recipe_service import RecipeService
from ui.components.inputs import SmartComboBox


# ── Class Definition ────────────────────────────────────────────────────────────
class ViewRecipes(QWidget):
    """Dynamically displays all recipes in a responsive scrollable layout using RecipeViewer wrappers."""

    recipe_selected = Signal(int)  # Signal that emits selected recipe ID

    def __init__(self, parent=None, meal_selection=False):
        """
        Initialize ViewRecipes.

        Args:
            parent (QWidget, optional): Parent widget.
            meal_selection (bool): If True, enables recipe selection mode.
        """
        super().__init__(parent)

        # ── Initialize & Setup UI ──
        self.setObjectName("ViewRecipes")
        self.meal_selection = meal_selection
        self.build_ui()
        self.recipes_loaded = False
        self.load_recipes()

    def build_ui(self):
        """Initializes layout with a scrollable, responsive recipe area."""

        # ── Create Main Layout ──
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(10)

        # ── Create Filter & Sort Options ──
        self.lyt_cb = QHBoxLayout()
        self.lyt_cb.setSpacing(10)
        self.lyt_cb.setContentsMargins(0, 0, 0, 0)        

        # filter combobox
        self.cb_filter = SmartComboBox(list = RECIPE_CATEGORIES, placeholder = "Filter")
        self.cb_filter.setPlaceholderText("Filter")
        self.lyt_cb.addWidget(self.cb_filter) # add filter dropdown
        self.cb_filter.currentTextChanged.connect(self.handle_filter_change) # connect filter change event

        # sort combobox
        self.cb_sort = SmartComboBox(list = SORT_OPTIONS, placeholder = "Sort")
        self.cb_sort.setPlaceholderText("Sort")
        self.lyt_cb.addWidget(self.cb_sort) # add sort dropdown
        self.cb_sort.currentTextChanged.connect(self.handle_sort_change) # connect sort change event

        # favorites checkbox
        self.chk_favorites = QCheckBox("Show Favorites Only")
        self.lyt_cb.addWidget(self.chk_favorites)
        self.chk_favorites.stateChanged.connect(self.load_filtered_sorted_recipes)

        # create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.viewport().setStyleSheet("background-color: transparent;")

        # create scroll container
        self.scroll_container = QWidget()
        self.flow_layout = self.create_flow_layout(self.scroll_container)
        self.scroll_container.setLayout(self.flow_layout)

        spacer = QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.flow_layout.addItem(spacer) # add top padding
    
        self.scroll_area.setWidget(self.scroll_container) # add to scroll area

        # add widgets to main layout
        self.main_layout.addLayout(self.lyt_cb) # add filter & sort dropdowns
        self.main_layout.addWidget(self.scroll_area)
    
    def handle_filter_change(self, selected_category: str) -> None:
        """Handle category filter selection."""
        self.load_filtered_sorted_recipes()

    def handle_sort_change(self, selected_sort: str) -> None:
        """Handle sort option selection."""
        self.load_filtered_sorted_recipes()


    def load_filtered_sorted_recipes(self):
        """Loads recipes using current filter, sort, and favorites-only flag."""
        recipe_category = self.cb_filter.currentText()
        sort = self.cb_sort.currentText()
        favorites_only = self.chk_favorites.isChecked()

        self.clear_recipe_display()

        recipes = RecipeService.list_filtered(
            recipe_category=recipe_category,
            sort_by=sort,
            favorites_only=favorites_only,
        )

        for recipe in recipes:
            slot = RecipeViewer(LayoutSize.MEDIUM, parent=self.scroll_container)
            slot.set_recipe(recipe)

            if self.meal_selection:
                slot.card_clicked.connect(
                    lambda r, self=self: self.select_recipe(r.id)
                )

            self.flow_layout.addWidget(slot)

    def clear_recipe_display(self):
        """Removes all recipe widgets from the layout."""
        while self.flow_layout.count():
            item = self.flow_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def load_recipes(self) -> None:
        from recipe_viewer.constants import LayoutSize
        from recipe_viewer.recipe_viewer import RecipeViewer

        recipes = Recipe.all()  # fetch all recipes from the database
        if not recipes:
            return

        self.clear_recipe_display()

        for recipe in recipes:
            slot = RecipeViewer(LayoutSize.MEDIUM, parent=self.scroll_container)
            slot.set_recipe(recipe)

            if self.meal_selection:
                slot.card_clicked.connect(
                    lambda r, self=self: self.select_recipe(r.id)
                )

            self.flow_layout.addWidget(slot)

        self.recipes_loaded = True

    def select_recipe(self, recipe_id):
        """Emit the selected recipe's ID and close the selection dialog.

        Args:
            recipe_id (int): The ID of the selected recipe.
        """
        self.recipe_selected.emit(recipe_id)

    def refresh(self):
        """Force refresh all recipe cards (used when returning from Add/Edit views)."""
        self.recipes_loaded = False
        self.load_recipes()

    def showEvent(self, event):
        """Override showEvent to load recipes if not already loaded.

        Args:
            event (QShowEvent): The show event triggered when the widget is displayed.
        """
        super().showEvent(event)
        if not self.recipes_loaded:
            self.load_recipes()

    def create_flow_layout(self, parent):
        """Returns a responsive flow layout for displaying cards, with centered alignment."""
        class FlowLayout(QLayout):
            def __init__(self, parent=None, margin=0, spacing=45):
                super().__init__(parent)
                self._items = []
                self.setContentsMargins(margin, margin, margin, margin)
                self._spacing = spacing

            def addItem(self, item):
                self._items.append(item)

            def count(self):
                return len(self._items)

            def itemAt(self, index):
                return self._items[index] if 0 <= index < len(self._items) else None

            def takeAt(self, index):
                return self._items.pop(index) if 0 <= index < len(self._items) else None

            def expandingDirections(self):
                return Qt.Orientation(0)

            def hasHeightForWidth(self):
                return True

            def heightForWidth(self, width):
                return self.doLayout(QRect(0, 0, width, 0), True)

            def setGeometry(self, rect):
                super().setGeometry(rect)
                self.doLayout(rect, False)

            def sizeHint(self):
                return self.minimumSize()

            def minimumSize(self):
                size = QSize()
                for item in self._items:
                    size = size.expandedTo(item.minimumSize())
                size += QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
                return size

            def doLayout(self, rect, testOnly):
                TOP_PADDING = 20
                y = rect.y() + TOP_PADDING
                row = []
                row_width = 0
                row_height = 0

                def layout_row(items, y):
                    nonlocal testOnly
                    total_width = sum(i.sizeHint().width() for i in items) + self._spacing * (len(items) - 1)
                    offset = (rect.width() - total_width) // 2
                    x = rect.x() + offset
                    for item in items:
                        size = item.sizeHint()
                        if not testOnly:
                            item.setGeometry(QRect(QPoint(x, y), size))
                        x += size.width() + self._spacing
                    return y + row_height + self._spacing

                for item in self._items:
                    size = item.sizeHint()
                    if row and (row_width + size.width() + self._spacing > rect.width()):
                        y = layout_row(row, y)
                        row = []
                        row_width = 0
                        row_height = 0
                    row.append(item)
                    row_width += size.width() + (self._spacing if row else 0)
                    row_height = max(row_height, size.height())

                if row:
                    y = layout_row(row, y)

                return y - rect.y()

        return FlowLayout(parent)

    
