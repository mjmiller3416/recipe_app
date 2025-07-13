"""app/ui/components/dialogs/recipe_selection.py

Dialog for selecting a recipe from a grid of recipe cards.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from typing import Optional
from PySide6.QtWidgets import QDialogButtonBox
from app.core.models import Recipe
from app.ui.components.dialogs.dialog_window import DialogWindow
from app.ui.components.composite.recipe_browser import RecipeBrowser
from app.ui.components.composite.recipe_card.constants import LayoutSize
from dev_tools import DebugLogger


# ── Recipe Selection ─────────────────────────────────────────────────────────────────────────
class RecipeSelection(DialogWindow):
    """A dialog that displays recipes in a grid for selection."""

    def __init__(self, recipes=None, parent=None):
        """
        Initialize the RecipeSelection dialog.

        Args:
            recipes (list[Recipe], optional): List of Recipe objects to display.
                Defaults to None (RecipeBrowser will load all recipes).
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(width=900, height=700, parent=parent)
        self._selected_recipe: Optional[Recipe] = None

        self.setWindowTitle("Select a Recipe")
        self.setMinimumSize(900, 700)
        self.title_bar.btn_ico_maximize.setVisible(False)
        self.title_bar.btn_ico_toggle_sidebar.setVisible(False)

        # use RecipeBrowser in selection mode with smaller cards
        self.recipe_browser = RecipeBrowser(
            parent=self,
            card_size=LayoutSize.SMALL,
            selection_mode=True
        )
        self.recipe_browser.scroll_area.setObjectName("RecipeSelectionBrowser")
        # connect selection signal
        self.recipe_browser.recipe_selected.connect(self._on_recipe_selected)

        # OK/Cancel buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        # initially disable OK button until selection is made
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)

        # add to layout
        self.content_layout.addWidget(self.recipe_browser)
        self.content_layout.addWidget(self.button_box)

        DebugLogger.log("[RecipeSelection] Initialized with RecipeBrowser", "debug")

    def _on_recipe_selected(self, recipe_id: int):
        """
        Handle recipe selection from the browser.

        Args:
            recipe_id (int): The ID of the selected recipe.
        """
        # get the recipe object from the service
        recipe = self.recipe_browser.recipe_service.get_recipe(recipe_id)
        if recipe:
            self._selected_recipe = recipe
            self.button_box.button(QDialogButtonBox.Ok).setEnabled(True)
            # auto-accept on selection (optional - remove if you want manual OK)
            self.accept()

    def selected_recipe(self) -> Optional[Recipe]:
        """Return the selected recipe."""
        return self._selected_recipe

    def accept(self):
        """Accept the dialog if a recipe is selected."""
        if self._selected_recipe:
            super().accept()
        else:
            DebugLogger.log("[RecipeSelection] No recipe selected", "warning")
