"""app/ui/components/recipe_selection.py

Dialog for selecting a recipe from a list.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from typing import List, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QAbstractItemView, QDialogButtonBox,
                               QListWidget, QListWidgetItem)

from app.core.data.models.recipe import Recipe
from app.ui.components.dialogs.dialog_window import DialogWindow


# ── Class Definition ────────────────────────────────────────────────────────────
class RecipeSelection(DialogWindow):
    """Dialog that allows the user to choose a recipe from a list."""

    def __init__(self, recipes: List[Recipe], parent=None) -> None:
        # ``DialogWindow``'s constructor expects width/height parameters and does
        # not take ``parent`` positionally. Passing the parent as the first
        # argument caused ``int(parent)`` to be evaluated when the base class
        # called ``resize`` which raised the reported ``int()`` TypeError.
        super().__init__(width=400, height=500, window_title="Select a Recipe")

        if parent is not None:
            self.setParent(parent)

        self._recipes = recipes
        self._selected_recipe: Optional[Recipe] = None

        # ── Window Properties ──
        self.setWindowTitle("Select a Recipe")
        self.setMinimumSize(400, 500)
        # ``DialogWindow``'s title bar only exposes a close button. Previous
        # versions attempted to hide maximize and sidebar toggle buttons that do
        # not exist on this minimal title bar, causing an AttributeError when
        # the dialog was shown. Those calls are removed.

        # ── Widgets ──
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.populate_list()

        # connect double-click for quick selection
        self.list_widget.itemDoubleClicked.connect(self.accept)

        # ok/cancel buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        # add widgets to layout
        self.content_layout.addWidget(self.list_widget)
        self.content_layout.addWidget(self.button_box)

    def populate_list(self):
        """ Fills the list widget with recipe names. """
        self.list_widget.clear()
        # populate the list widget with recipe names
        for recipe in self._recipes:
            item = QListWidgetItem(recipe.recipe_name)
            item.setData(Qt.UserRole, recipe)
            self.list_widget.addItem(item)

    def selected_recipe(self) -> Optional[Recipe]:
        """ Returns the Recipe object selected by the user, or None. """
        current_item = self.list_widget.currentItem()
        if current_item:
            #retrieve the stored Recipe object
            return current_item.data(Qt.UserRole)
        return None

    def accept(self):
        """ Stores the selected recipe before accepting the dialog. """
        selected = self.selected_recipe()
        if selected:
            self._selected_recipe = selected
            super().accept() # call BaseDialog accept method
        else:
            print("Please select a recipe.") # handle no selection case
