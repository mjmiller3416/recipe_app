# recipe_app/meal_planner/recipe_selection_dialog.py
"""
Module: meal_planner.recipe_selection_dialog

This module defines the RecipeSelectionDialog class, a modal dialog that lets users pick a recipe
via the ViewRecipes widget. Instead of emitting its own signal, the dialog listens for the
ViewRecipes widget's `recipe_selected` signal. When a recipe is selected, the dialog records the
recipe ID and closes.
"""

# 🔸 Third-party Imports
from PySide6.QtWidgets import QDialog, QVBoxLayout

# 🔸 Local Application Imports
from features.view_recipes import ViewRecipes

class RecipeSelectionDialog(QDialog):
    """
    Dialog window that allows users to select a recipe from ViewRecipes.
    
    Attributes:
        selected_recipe (str): The ID of the recipe chosen by the user.

        Signals:
            recipe_selected (Signal): Emitted when a recipe is selected, passing the recipe ID.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select a Recipe")
        self.setModal(True)
        self.setMinimumSize(1000, 900)

        # Setup layout
        layout = QVBoxLayout(self)
        self.view_recipes = ViewRecipes(meal_selection=True)
        layout.addWidget(self.view_recipes)

        # Connect selection signal
        self.view_recipes.recipe_selected.connect(self.recipe_chosen)

        self.selected_recipe = None  # Store selected recipe ID

    def recipe_chosen(self, recipe_id):
        """
        Handles the selected recipe and closes the dialog.
        
        Args:
            recipe_id (str): The ID of the selected recipe.
        """
        self.selected_recipe = recipe_id
        self.accept()
