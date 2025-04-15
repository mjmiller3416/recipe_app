from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel
)
from PySide6.QtCore import Qt
from core.modules.recipe_module import Recipe
from dev_sandbox.recipe_card import RecipeCard


def generate_mock_recipe(name, time, servings, image_path):
    return Recipe({
        "id": hash(name) % 10000,
        "recipe_name": name,
        "total_time": time,
        "servings": servings,
        "image_path": image_path,
        "ingredients": [],  # Optional; add fake ingredient data if needed
        "directions": "Some simple steps for cooking.",
    })


def create_test_widget():
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setAlignment(Qt.AlignTop)
    layout.setSpacing(20)

    recipes = [
        generate_mock_recipe("Beef Stroganoff", 40, 4, "recipe_images/beef_stroganoff.jpg"),
        generate_mock_recipe("Vegetarian Stir-Fry", 25, 3, "recie_images/vegetarian_stir-fry.jpg"),
        generate_mock_recipe("Shrimp Pad Thai", 40, 3, "recipe_images/shrimp_pad_thai.jpg"),
    ]

    full_row = QHBoxLayout()
    mini_row = QHBoxLayout()

    layout.addWidget(QLabel("Full View Layout"))
    for recipe in recipes:
        card = RecipeCard(recipe, layout_mode="full")
        full_row.addWidget(card)

    layout.addLayout(full_row)

    layout.addWidget(QLabel("Mini View Layout"))
    for recipe in recipes:
        card = RecipeCard(recipe, layout_mode="mini")
        mini_row.addWidget(card)

    layout.addLayout(mini_row)

    return container


def run_test(app: QApplication):
    test_window = QScrollArea()
    test_window.setWindowTitle("RecipeCard View Test")
    test_window.setWidgetResizable(True)
    test_window.setMinimumSize(1000, 700)
    test_window.setWidget(create_test_widget())
    test_window.show()
    return test_window

