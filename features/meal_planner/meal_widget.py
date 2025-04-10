# recipe_app/meal_planner/meal_widget.py
"""
Module: meal_planner.meal_widget

This module defines the MealWidget class, which is responsible for displaying a meal selection interface.
It allows users to add a meal, open a recipe selection dialog, and display the selected recipe as a card.
"""

# 🔸 Third-party Imports
from core.helpers.qt_imports import QFrame, QVBoxLayout, QPushButton, QSize, Qt, Signal, QIcon

# 🔸 Local Application Imports
from meal_planner.recipe_selection_dialog import RecipeSelectionDialog
from view_recipes.recipe_card import RecipeCard 
from database import DB_INSTANCE

class MealWidget(QFrame):
    """
    MealWidget is a custom QFrame that provides an interface for selecting a meal recipe.
    It displays a button to add a meal, and upon selection of a recipe, it shows the recipe card.

    Signals:
        recipe_selected (Signal): Emitted when a recipe is selected, passing the meal type and recipe ID.
    
    Attributes:
        meal_type (str): The type of meal (e.g., "main" or "side") for which this widget is used.
        recipe_card (RecipeCard): The card displaying the selected recipe.

    """

    recipe_selected = Signal(str, int)  # meal_type, recipe_id

    def __init__(self, parent=None, meal_type="main"):
        """
        Initialize the MealWidget.

        Args:
            parent (QWidget, optional): The parent widget for this MealWidget.
            meal_type (str): The type of meal this widget represents (default is "main").
                - "main" for main dishes, full-sized recipe card
                - "side" for side dishes, mini-sized recipe card
        """
        super().__init__(parent)

        self.meal_type = meal_type
        self.setObjectName("MealWidget")
        self.setProperty("class", "CardFrame")
        self.setAttribute(Qt.WA_StyledBackground, True)

        self._setup_ui()

    def _setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Add Meal Button (acts as placeholder until recipe selected)
        self.btn_add_meal = QPushButton()
        self.btn_add_meal.setObjectName("btn_add_meal")
        self.btn_add_meal.setStyleSheet("background: transparent;")
        self.btn_add_meal.setIcon(QIcon(":/icons/add_meal.svg"))
        self.btn_add_meal.setIconSize(QSize(50, 50))
        self.btn_add_meal.clicked.connect(self.open_recipe_selection)

        self.layout.addWidget(self.btn_add_meal, alignment=Qt.AlignCenter)

    def open_recipe_selection(self):
        """Open the recipe selection dialog and handle the selected recipe."""
        dialog = RecipeSelectionDialog(self)
        if dialog.exec():
            self.set_selected_recipe(dialog.selected_recipe)

    def set_selected_recipe(self, recipe_id):
        """
        Set the selected recipe by replacing the add meal button with a RecipeCard.
        This method will create a RecipeCard based on the selected recipe ID and update the layout.

        Args:
            recipe_id (int): The ID of the selected recipe.
        """
        recipe = DB_INSTANCE.get_recipe(recipe_id)
        if not recipe:
            return

        card_mode = "full" if self.meal_type == "main" else "mini"

        self.recipe_card = RecipeCard(
            recipe_data=recipe,
            parent=self,
            mode=card_mode,
            meal_selection=False
        )

        self.layout.replaceWidget(self.btn_add_meal, self.recipe_card)
        self.btn_add_meal.deleteLater()
        self.btn_add_meal = None

        self.recipe_selected.emit(self.meal_type, recipe_id)

    def clear(self):
        """Optional method to reset the widget."""
        if hasattr(self, "recipe_card"):
            self.layout.removeWidget(self.recipe_card)
            self.recipe_card.deleteLater()
        self._setup_ui()
