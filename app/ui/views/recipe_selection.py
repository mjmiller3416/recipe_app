"""app/ui/views/recipe_selection_page.py

Defines a RecipeSelection for in-context recipe selection using RecipeBrowser.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget

from app.ui.components.composite.recipe_browser import RecipeBrowser
from app.ui.components.composite.recipe_card import LayoutSize

# ── Recipe Selection View ───────────────────────────────────────────────────────────────────────────────────
class RecipeSelection(QWidget):
    """Page displaying recipes in medium-sized cards for selection."""
    recipe_selected = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RecipeSelection")
        # layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # recipe browser in selection mode
        self.browser = RecipeBrowser(
            parent=self,
            card_size=LayoutSize.MEDIUM,
            selection_mode=True
        )
        self.browser.recipe_selected.connect(self.recipe_selected.emit)
        layout.addWidget(self.browser)
