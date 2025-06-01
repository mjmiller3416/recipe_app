"""Test script for MyTestApp."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QGridLayout, QLineEdit, QMainWindow,
                               QVBoxLayout, QWidget)

from config import INGREDIENT_CATEGORIES, INGREDIENT_WIDGET, MEASUREMENT_UNITS
from ui.components.inputs import SmartComboBox
from ui.components.widget_frame import WidgetFrame
from ui.iconkit import ToolButtonIcon
from views.add_recipes.upload_recipe import UploadRecipeImage


class MyTestApp(QMainWindow):
    """A test class for development testing."""

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("MyTestApp")
        self.setGeometry(100, 100, 800, 600)
        self.show()

        # Set up the central widget and layout
        self.central_widget = QWidget()
        self.central_layout = QVBoxLayout()
        self.central_widget.setLayout(self.central_layout)
        self.setCentralWidget(self.central_widget)
        self.setObjectName("IngredientWidget")

        self.build_ui()

    def build_ui(self):
        """Builds the UI components."""
        # Create widget frame, with embedded layout
        self.btn = UploadRecipeImage(self)
        self.central_layout.addWidget(self.btn)

    def ingredient_row(self):
        """Creates and returns an ingredient row widget."""
        ingredient_row = QWidget()
        grid_layout = QGridLayout()
        ingredient_row.setLayout(grid_layout)

        le_quantity = QLineEdit(self)
        le_quantity.setFixedHeight(32)
        le_quantity.setPlaceholderText("Qty.")
        grid_layout.addWidget(le_quantity, 0, 0, 1, 1)

        cb_unit = SmartComboBox(
            list=MEASUREMENT_UNITS, 
            placeholder="Unit"
        )
        grid_layout.addWidget(cb_unit, 0, 1, 1, 1)

        le_ingredient_name = QLineEdit(self)
        le_ingredient_name.setFixedHeight(32)
        le_ingredient_name.setPlaceholderText("Ingredient Name")
        grid_layout.addWidget(le_ingredient_name, 0, 2, 1, 1)

        cb_ingredient_category = SmartComboBox(
            list=INGREDIENT_CATEGORIES, 
            placeholder="Category"
        )
        grid_layout.addWidget(cb_ingredient_category, 0, 3, 1, 1)

        btn_ico_subtract = ToolButtonIcon(
            file_path = INGREDIENT_WIDGET["ICON_SUBTRACT"],
            icon_size = INGREDIENT_WIDGET["ICON_SIZE"],
            variant   = INGREDIENT_WIDGET["DYNAMIC"]
        )
        grid_layout.addWidget(btn_ico_subtract, 0, 4, 1, 1)

        btn_ico_add = ToolButtonIcon(
            file_path = INGREDIENT_WIDGET["ICON_ADD"],
            icon_size = INGREDIENT_WIDGET["ICON_SIZE"],
            variant   = INGREDIENT_WIDGET["DYNAMIC"]
        )
        grid_layout.addWidget(btn_ico_add, 0, 5, 1, 1)

        return ingredient_row 



        
        
def run_test(app):
    """Runs the test window."""
    window = MyTestApp(app)
    return window
