"""recipe_card/dialogs/recipe_selection_dialog.py

Dialog for selecting a recipe from a list.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from typing import List, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QAbstractItemView, QDialogButtonBox,
                               QListWidget, QListWidgetItem)

from database.models.recipe import Recipe
from ui.components.dialogs.dialog_window import DialogWindow


# ── Class Definition ────────────────────────────────────────────────────────────
class RecipeSelectionDialog(DialogWindow):
    """
    A dialog that displays a list of available recipes for selection.
    """
    def __init__(self, recipes: List[Recipe], parent=None):
        super().__init__(parent)
        self._recipes = recipes
        self._selected_recipe: Optional[Recipe] = None

        # ── Window Properties ──
        self.setWindowTitle("Select a Recipe")
        self.setMinimumSize(400, 500)
        self.title_bar.btn_ico_maximize.setVisible(False)
        self.title_bar.btn_ico_toggle_sidebar.setVisible(False)

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
