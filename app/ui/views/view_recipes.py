"""app/ui/pages/view_recipes/view_recipes.py

This module defines the ViewRecipes class, which displays a list of recipes in a scrollable
flow layout and can switch to a full recipe view.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QStackedWidget, QVBoxLayout, QWidget

from app.ui.components.composite.recipe_browser import RecipeBrowser
from app.ui.components.composite.recipe_card.constants import LayoutSize
from app.ui.views.full_recipe import FullRecipe
from dev_tools import DebugLogger


# ── View Recipes ─────────────────────────────────────────────────────────────────────────────
class ViewRecipes(QWidget):
    """Displays recipes using the shared RecipeBrowser component and can switch to full recipe view."""

    recipe_selected = Signal(int)

    def __init__(self, parent=None, meal_selection=False):
        """
        Initialize ViewRecipes.

        Args:
            parent (QWidget, optional): Parent widget.
            meal_selection (bool): If True, enables recipe selection mode.
        """
        super().__init__(parent)
        self.setObjectName("ViewRecipes")
        self.meal_selection = meal_selection
        self.current_full_recipe_view = None

        DebugLogger.log("Initializing ViewRecipes page", "info")

        # create layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        # create stacked widget to switch between recipe list and full recipe
        self.stacked_widget = QStackedWidget()
        
        # create recipe browser
        self.recipe_browser = RecipeBrowser(
            parent=self,
            card_size=LayoutSize.MEDIUM,
            selection_mode=meal_selection
        )
        self.recipe_browser.setObjectName("RecipeBrowser")

        # connect signals based on mode
        if meal_selection:
            self.recipe_browser.recipe_selected.connect(self.recipe_selected.emit)
        else:
            # normal mode - connect to show full recipe view instead of dialog
            self.recipe_browser.recipe_card_clicked.connect(self._show_full_recipe)

        # add recipe browser to stacked widget
        self.stacked_widget.addWidget(self.recipe_browser)  # index 0
        self.main_layout.addWidget(self.stacked_widget)

    def refresh(self):
        """Refresh the recipe display."""
        self.recipe_browser.refresh()

    def _show_full_recipe(self, recipe):
        """Show the full recipe view for the given recipe."""
        # remove current full recipe view if it exists
        if self.current_full_recipe_view:
            self.stacked_widget.removeWidget(self.current_full_recipe_view)
            self.current_full_recipe_view.deleteLater()
            self.current_full_recipe_view = None

        # create new full recipe view
        self.current_full_recipe_view = FullRecipe(recipe, parent=self)
        self.current_full_recipe_view.back_clicked.connect(self._show_recipe_list)
        
        # add to stacked widget and show
        self.stacked_widget.addWidget(self.current_full_recipe_view)  # index 1
        self.stacked_widget.setCurrentWidget(self.current_full_recipe_view)

    def _show_recipe_list(self):
        """Return to the recipe list view."""
        self.stacked_widget.setCurrentWidget(self.recipe_browser)
        
        # clean up the full recipe view
        if self.current_full_recipe_view:
            self.stacked_widget.removeWidget(self.current_full_recipe_view)
            self.current_full_recipe_view.deleteLater()
            self.current_full_recipe_view = None

    def showEvent(self, event):
        """Refresh on show if needed."""
        super().showEvent(event)
        if not self.recipe_browser.recipes_loaded:
            self.recipe_browser.load_recipes()

        # Force layout update after show
        from PySide6.QtCore import QTimer
        QTimer.singleShot(50, self._ensure_layout_update)

    def _ensure_layout_update(self):
        """Ensure the layout is properly updated after showing."""
        if hasattr(self.recipe_browser, 'scroll_container'):
            self.recipe_browser.scroll_container.updateGeometry()
            self.recipe_browser.scroll_area.updateGeometry()
            # Force the flow layout to recalculate
            self.recipe_browser.flow_layout.update()

