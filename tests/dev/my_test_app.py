"""Test script for MyTestApp."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QGridLayout, QLineEdit, QMainWindow,
                               QPushButton, QVBoxLayout, QWidget)

from config import INGREDIENT_CATEGORIES, INGREDIENT_WIDGET, MEASUREMENT_UNITS
from ui.components.dialogs.dialog_window import DialogWindow
from ui.components.inputs import SmartComboBox
from ui.components.widget_frame import WidgetFrame
from ui.iconkit import ToolButtonIcon
from views.add_recipes.upload_recipe import UploadRecipeImage
from views.add_recipes.ingredient_widget import IngredientWidget


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
        self.build_ingredient_test()
        #self.build_smart_combobox_test()

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

    def build_ingredient_test(self):
        """Creates and returns an ingredient row widget."""
        ingredient_widget = IngredientWidget(
            removable=False,
        )
        ingredient_widget.setFixedHeight(32)
        self.central_layout.addWidget(ingredient_widget)
 
    def build_smart_combobox_test(self):
        """Creates and returns a SmartComboBox widget."""
        smart_combobox = SmartComboBox(
            list=["Item 1", "Item 2", "Item 3"],
            placeholder="Select an item"
        )
        smart_combobox.setFixedHeight(32)
        self.central_layout.addWidget(smart_combobox)
        
def run_test(app):
    """Runs the test window."""
    window = MyTestApp(app)
    return window
