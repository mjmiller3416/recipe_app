from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel
)
from PySide6.QtCore import Qt
from core.modules.recipe_module import Recipe
from recipe_widget.recipe_widget import RecipeWidget
# Import the database instance
from database import DB_INSTANCE

def fetch_real_recipes(limit=3):
    # Fetch all recipes from the database (no limit argument)
    recipes_data = DB_INSTANCE.get_all_recipes()
    # Slice to the desired limit
    recipes_data = recipes_data[:limit]
    # Convert to Recipe objects
    recipes = [Recipe(recipe_dict) for recipe_dict in recipes_data]
    return recipes

def create_test_widget():
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setAlignment(Qt.AlignTop)
    layout.setSpacing(20)

    # Use real recipes from the database
    recipes = fetch_real_recipes(limit=3)

    full_row = QHBoxLayout()
    mini_row = QHBoxLayout()

    layout.addWidget(QLabel("Medium View Layout"))
    for _ in range(3):
        # Pass meal_selection=True to show the Add Meal button for empty widgets
        card = RecipeWidget(layout_mode="medium", meal_selection=True)
        full_row.addWidget(card)

    layout.addLayout(full_row)

    layout.addWidget(QLabel("Small View Layout"))
    for _ in range(3):
        card = RecipeWidget(layout_mode="small", meal_selection=True)
        mini_row.addWidget(card)

    layout.addLayout(mini_row)

    return container 


def run_test(app: QApplication):
    test_window = QScrollArea()
    test_window.setWindowTitle("RecipeWidget View Test")
    test_window.setWidgetResizable(True)
    test_window.setMinimumSize(1000, 700)
    test_window.setWidget(create_test_widget())
    test_window.show()
    return test_window

