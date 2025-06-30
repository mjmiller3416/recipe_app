"""app/ui/pages/view_recipes/view_recipes.py

This module defines the ViewRecipes class, which displays a list of recipes in a scrollable layout.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from app.config import RECIPE_CATEGORIES, SORT_OPTIONS
from app.core.data.models.recipe import Recipe
from app.core.services.recipe_service import RecipeService
from app.core.dtos.recipe_dtos import RecipeFilterDTO
from app.ui.components.inputs import ComboBox
from app.ui.components.recipe_card.constants import LayoutSize
from app.ui.components.recipe_card.recipe_card import RecipeCard
from app.ui.components.layout.flow_layout import FlowLayout
from app.core.utils import DebugLogger

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
        self.setObjectName("ViewRecipes") 
        DebugLogger.log("Initializing ViewRecipes page", "debug")   
        self.meal_selection = meal_selection

        self.build_ui()
        # sort recipes alphabetically on first load
        self.cb_sort.setCurrentText("A-Z")
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
        self.cb_filter = ComboBox(list_items=RECIPE_CATEGORIES, placeholder="Filter")
        self.lyt_cb.addWidget(self.cb_filter)  # add filter dropdown
        self.cb_filter.currentTextChanged.connect(
            self.handle_filter_change
        )  # connect filter change event

        # sort combobox
        self.cb_sort = ComboBox(list_items=SORT_OPTIONS, placeholder="Sort")
        self.lyt_cb.addWidget(self.cb_sort)  # add sort dropdown
        self.cb_sort.currentTextChanged.connect(
            self.handle_sort_change
        )  # connect sort change event

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

    def load_filtered_sorted_recipes(self):
        """Loads recipes using current filter, sort, and favorites-only flag."""
        recipe_category = self.cb_filter.currentText()
        sort = self.cb_sort.currentText()
        favorites_only = self.chk_favorites.isChecked()

        self.clear_recipe_display()

        filter_dto = RecipeFilterDTO(
            recipe_category=recipe_category,
            sort_by=sort,
            favorites_only=favorites_only,
        )

        recipes = RecipeService.list_filtered(filter_dto)

        for recipe in recipes:
            slot = RecipeCard(LayoutSize.MEDIUM, parent=self.scroll_container)
            slot.set_recipe(recipe)

            if self.meal_selection:
                slot.card_clicked.connect(lambda r, self=self: self.select_recipe(r.id))

            self.flow_layout.addWidget(slot)

    def clear_recipe_display(self):
        """Removes all recipe widgets from the layout."""
        while self.flow_layout.count():
            w = self.flow_layout.takeAt(0)
            if w:
                w.deleteLater()

    def load_recipes(self) -> None:
        from app.ui.components.recipe_card import RecipeCard
        from app.ui.components.recipe_card.constants import LayoutSize

        filter_dto = RecipeFilterDTO(sort_by="A-Z")
        recipes = RecipeService.list_filtered(filter_dto)
        if not recipes:
            return

        self.clear_recipe_display()

        for recipe in recipes:
            slot = RecipeCard(LayoutSize.MEDIUM, parent=self.scroll_container)
            slot.set_recipe(recipe)

            if self.meal_selection:
                slot.card_clicked.connect(lambda r, self=self: self.select_recipe(r.id))

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

