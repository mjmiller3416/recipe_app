"""Test script for MyTestApp."""
import math

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QGridLayout, QLineEdit, QMainWindow,
                               QPushButton, QVBoxLayout, QWidget)
from views.add_recipes.ingredient_widget import IngredientWidget
from views.add_recipes.upload_recipe import UploadRecipeImage

from app.config import (INGREDIENT_CATEGORIES, INGREDIENT_WIDGET,
                        MEASUREMENT_UNITS, STYLES)
from app.ui.components.dialogs.dialog_window import DialogWindow
from app.ui.components.inputs import CustomComboBox, SmartLineEdit
from app.ui.components.widget_frame import WidgetFrame
from app.ui.iconkit import ToolButtonIcon

INGREDIENTS = [
            "Almond milk", "Bacon", "Baking powder", "Baking soda", "BBQ sauce", "Bell pepper",
            "Black beans", "Bread", "Broccoli", "Brown sugar", "Butter", "Carrot", "Cauliflower",
            "Cheddar", "Chicken breast", "Chickpeas", "Chili flakes", "Cinnamon", "Corn",
            "Couscous", "Crackers", "Cucumber", "Eggs", "Feta", "Flour", "Garlic", "Green beans",
            "Ground beef", "Ground turkey", "Ham", "Heavy cream", "Honey", "Hot sauce", "Hummus",
            "Jam", "Kale", "Ketchup", "Kidney beans", "Lettuce", "Maple syrup", "Mayonnaise",
            "Milk", "Mozzarella", "Mushrooms", "Mustard", "Noodles", "Oat milk", "Oats",
            "Olive Oil", "Onion", "Parmesan", "Pasta", "Peanut butter", "Pepper", "Pickles",
            "Pita", "Pork chops", "Quinoa", "Relish", "Rice", "Salmon", "Salt", "Salsa",
            "Sausage", "Shrimp", "Soy sauce", "Sour cream", "Spinach", "Sugar", "Sweet potato",
            "Tempeh", "Tofu", "Tomato", "Tortilla", "Turkey", "Tuna", "Vinegar", "Vegetable oil",
            "Yogurt", "Zucchini"
        ]

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

        #self.build_upload_test()
        #self.build_dialog_test()
        #self.build_ingredient_test()
        self.build_custom_combobox_test()

    def build_dialog_test(self):
        def show_custom_dialog(self):
            dialog = DialogWindow(
                width=800, 
                height=600,
                title="Custom Dialog"
            )
            dialog.exec()

        self.button = QPushButton("Open Dialog", self)
        self.button.setGeometry(80, 80, 140, 40)
        self.button.clicked.connect(show_custom_dialog)

        # add to the central layout
        self.central_layout.addWidget(self.button)
      
    def build_upload_test(self):
        """Builds the UI components."""
        # Create widget frame, with embedded layout
        self.btn = UploadRecipeImage(self)
        self.central_layout.addWidget(self.btn)

    def build_smart_line_edit_test(self):
        """Creates and returns an ingredient row widget."""

        scb = SmartLineEdit(
            list_items=INGREDIENTS,
            placeholder="Search...",
            editable=True
        )
        scb.setFixedHeight(32)
        self.central_layout.addWidget(scb, alignment=Qt.AlignCenter)
 
    def build_custom_combobox_test(self):
        """Creates and returns a CustomComboBox widget."""
        custom_combobox = CustomComboBox(
            list_items=INGREDIENTS,
            placeholder="Select an item",
        )
        custom_combobox.setFixedHeight(32)
        custom_combobox.setFixedWidth(200)
        self.central_layout.addWidget(custom_combobox, alignment=Qt.AlignCenter)

    def build_ingredient_widget_test(self):
        """Creates and returns an IngredientWidget."""
        ingredient_widget = IngredientWidget(
            categories=INGREDIENT_CATEGORIES,
            units=MEASUREMENT_UNITS,
            style_path=INGREDIENT_WIDGET["STYLE_PATH"]
        )
        self.central_layout.addWidget(ingredient_widget)
    
  
def run_test(app):
    """Runs the test window."""
    window = MyTestApp(app)
    return window
