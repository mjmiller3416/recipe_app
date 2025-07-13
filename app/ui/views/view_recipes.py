"""app/ui/pages/view_recipes/view_recipes.py

This module defines the ViewRecipes class, which displays a list of recipes in a scrollable
flow layout.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget
from app.ui.components.composite.recipe_browser import RecipeBrowser
from app.ui.components.composite.recipe_card.constants import LayoutSize
from dev_tools import DebugLogger


# ── View Recipes ─────────────────────────────────────────────────────────────────────────────
class ViewRecipes(QWidget):
    """Displays recipes using the shared RecipeBrowser component."""

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

        DebugLogger.log("Initializing ViewRecipes page", "debug")

        # create layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

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
            # normal mode - cards open full recipe dialog
            pass  # recipeBrowser handles this internally

        self.main_layout.addWidget(self.recipe_browser)

    def refresh(self):
        """Refresh the recipe display."""
        self.recipe_browser.refresh()

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

