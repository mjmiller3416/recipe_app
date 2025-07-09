"""app/ui/pages/view_recipes/view_recipes.py

This module defines the ViewRecipes class, which displays a list of recipes in a scrollable layout.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QCheckBox, QHBoxLayout, QScrollArea,
                               QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

from app.config import RECIPE_CATEGORIES, SORT_OPTIONS
from app.core.dtos import RecipeFilterDTO
from app.core.models.recipe import Recipe
from app.core.services.recipe_service import RecipeService
from app.ui.components.composite import RecipeCard
from app.ui.components.composite.recipe_card.constants import LayoutSize
from app.ui.components.layout.flow_layout import FlowLayout
from app.ui.components.widgets import ComboBox
from dev_tools import DebugLogger


# ── Class Definition ────────────────────────────────────────────────────────────
class ViewRecipes(QWidget):
    """Dynamically displays all recipes in a responsive scrollable layout using RecipeViewer wrappers."""

    recipe_selected = Signal(int)  # signal that emits selected recipe ID

    def __init__(self, parent=None, meal_selection=False):
        """
        Initialize ViewRecipes.

        Args:
            parent (QWidget, optional): Parent widget.
            meal_selection (bool): If True, enables recipe selection mode.
        """
        super().__init__(parent)
        self.setObjectName("ViewRecipes")
        DebugLogger.log("Initializing ViewRecipes page", "debug")
        self.meal_selection = meal_selection

        self.build_ui()
        # sort recipes alphabetically on first load
        self.cb_sort.setCurrentText("A-Z")
        self.recipes_loaded = False

        self.load_recipes()

    # mapping from user-friendly sort options to backend field names
    SORT_OPTION_MAP = {
        "A-Z": "recipe_name",
        "Z-A": "recipe_name",  # you may want to handle order elsewhere
        "Newest": "created_at",
        "Oldest": "created_at",
        "Shortest Time": "total_time",
        "Longest Time": "total_time",
        "Most Servings": "servings",
        "Fewest Servings": "servings",
    }

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
        self.cb_filter = ComboBox(list_items=RECIPE_CATEGORIES, placeholder="Filter")
        self.lyt_cb.addWidget(self.cb_filter)
        # connect when user picks an item (selection_validated covers clicks) or text changes
        self.cb_filter.currentTextChanged.connect(self.handle_filter_change)
        self.cb_filter.selection_validated.connect(
            lambda valid: self.handle_filter_change(self.cb_filter.currentText())
        )

        # sort combobox
        self.cb_sort = ComboBox(list_items=SORT_OPTIONS, placeholder="Sort")
        self.lyt_cb.addWidget(self.cb_sort)
        self.cb_sort.currentTextChanged.connect(self.handle_sort_change)
        self.cb_sort.selection_validated.connect(
            lambda valid: self.handle_sort_change(self.cb_sort.currentText())
        )

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
        self.flow_layout = FlowLayout(
            self.scroll_container,
            needAni=False,     # you can turn on animations by setting True
            isTight=True       # hide invisible widgets without gaps
        )
        self.scroll_container.setLayout(self.flow_layout)
        self.flow_layout.setContentsMargins(0, 20, 0, 0)

        self.scroll_area.setWidget(self.scroll_container)  # add to scroll area

        # add widgets to main layout
        self.main_layout.addLayout(self.lyt_cb)  # add filter & sort dropdowns
        self.main_layout.addWidget(self.scroll_area)

    def handle_filter_change(self, selected_category: str) -> None:
        """Handle category filter selection."""
        self.load_filtered_sorted_recipes()

    def handle_sort_change(self, selected_sort: str) -> None:
        """Handle sort option selection."""
        self.load_filtered_sorted_recipes()

    def _fetch_and_display_recipes(self, filter_dto: RecipeFilterDTO) -> None:
        """Helper method to fetch recipes using a DTO and update the UI."""
        from app.ui.components.composite import RecipeCard
        from app.ui.components.composite.recipe_card import LayoutSize

        self.clear_recipe_display()

        # fetch recipes via RecipeService
        service = RecipeService()
        recipes = service.list_filtered(filter_dto)

        if not recipes:
            # optionally, display a "No recipes found" message
            return

        # populate the layout with recipe cards
        for recipe in recipes:
            slot = RecipeCard(LayoutSize.MEDIUM, parent=self.scroll_container)
            slot.set_recipe(recipe)

            if self.meal_selection:
                slot.card_clicked.connect(lambda r, self=self: self.select_recipe(r.id))

            self.flow_layout.addWidget(slot)

        self.recipes_loaded = True

    def load_recipes(self) -> None:
        """Loads initial, default-sorted list of recipes."""
        default_filter_dto = RecipeFilterDTO(
            recipe_category=None,
            sort_by=self.SORT_OPTION_MAP.get("A-Z", "recipe_name"),
            sort_order="asc",
            favorites_only=False
        )
        self._fetch_and_display_recipes(default_filter_dto)

    def load_filtered_sorted_recipes(self) -> None:
        """Loads recipes using current UI filter and sort selections."""
        recipe_category = self.cb_filter.currentText()
        if not recipe_category or recipe_category in ("All", "Filter"):
            recipe_category = None

        sort_label = self.cb_sort.currentText()

        filter_dto = RecipeFilterDTO(
            recipe_category=recipe_category,
            sort_by=self.SORT_OPTION_MAP.get(sort_label, "recipe_name"),
            sort_order="desc" if sort_label in ("Z-A",) else "asc",
            favorites_only=self.chk_favorites.isChecked(),
        )
        self._fetch_and_display_recipes(filter_dto)

    def clear_recipe_display(self):
        """Removes all recipe widgets from the layout."""
        while self.flow_layout.count():
            w = self.flow_layout.takeAt(0)
            if w:
                w.deleteLater()

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

