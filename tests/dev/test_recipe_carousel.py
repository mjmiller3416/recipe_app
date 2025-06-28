"""Test script for TestRecipeCarousel."""

import sys
from pathlib import Path

# Add project root to the Python path
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QApplication
from app.ui.components.carousel.recipe_carousel import RecipeCarousel
from app.core.dtos.recipe_dtos import RecipeCreateDTO

class TestRecipeCarousel(QMainWindow):
    """A test class for development testing."""

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("TestRecipeCarousel")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # sample recipe data
        recipes = [
            RecipeCreateDTO(
                recipe_name="Spaghetti Carbonara", 
                recipe_category="Italian", 
                image_path="path/to/image1.png"),
            RecipeCreateDTO(
                recipe_name="Chicken Tikka Masala", 
                recipe_category="Indian", 
                image_path="path/to/image2.png"),
            RecipeCreateDTO(
                recipe_name="Beef Tacos", 
                recipe_category="Mexican", 
                image_path="path/to/image3.png"),
            RecipeCreateDTO(
                recipe_name="Sushi Platter", 
                recipe_category="Japanese", 
                image_path="path/to/image4.png"),
        ]

        # Create and add the carousel
        carousel = RecipeCarousel(recipes)
        layout.addWidget(carousel)

        self.resize(carousel.sizeHint())
        self.show()

def run_test(app):
    """Runs the test window."""
    window = TestRecipeCarousel(app)
    return window

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TestRecipeCarousel(app)
    sys.exit(app.exec())
