# Package: app.widgets.ingredient_widget

# Description: This file contains the IngredientWidget class, which is a custom widget that represents an ingredient in the 
# AddRecipe window. It allows users to input the quantity, unit, name, and category of an ingredient. It also provides buttons 
# to add or remove the ingredient widget. The IngredientWidget class emits signals to notify the AddRecipe window of changes 
# to the ingredient data, as well as requests to add or remove the ingredient widget.

#🔸Third-party Imports 
from helpers.qt_imports import (QWidget, Signal) # Importing necessary classes from PyQt

#🔸Local Imports
from .ui_ingredient_widget import Ui_IngredientWidget
from helpers import DebugLogger
from helpers.config import INGREDIENT_CATEGORIES, MEASUREMENT_UNITS, FLOAT, NAME
from helpers.ui_helpers import clear_error_styles, dynamic_validation

class IngredientWidget(QWidget):
    """
    IngredientWidget represents a single ingredient input row.

    This widget allows users to:
    - Enter ingredient details (name, quantity, unit, category)
    - Dynamically add or remove ingredients
    - Send real-time updates to AddRecipe via signals

    Signals:
        add_ingredient_requested (QWidget): Sent when the "Add" button is clicked.
        remove_ingredient_requested (QWidget): Sent when the "Remove" button is clicked.
        ingredient_updated (dict): Sent whenever ingredient data changes.
    """

    #🔹SIGNALS
    add_ingredient_requested = Signal(QWidget) # Emits a request to add an ingredient
    remove_ingredient_requested = Signal(QWidget) # Emits request to remove an ingredient
    ingredient_validated = Signal(dict)  # Emits validated ingredient data

    def __init__(self, removable=True, parent=None):
        super().__init__(parent)

        # Initialize UI
        self.ui = Ui_IngredientWidget() 
        self.ui.setupUi(self)

        self.setObjectName("IngredientWidget")

        # Populate comboboxes
        self.populate_comboboxes()

        # Connect UI events to methods
        self.setup_event_logic()

        # Apply hover effects
        self.apply_styles()

    @property
    def ingredient_data(self):
        """Returns the current ingredient data as a dictionary."""
        return {
            "le_quantity": self.ui.le_quantity,  
            "cb_unit": self.ui.cb_unit,  
            "le_ingredient_name": self.ui.le_ingredient_name,  
            "cb_ingredient_category": self.ui.cb_ingredient_category,  
        }

    def setup_event_logic(self):
        """Connects UI events to corresponding methods."""
        self.ui.btn_add.clicked.connect(self.validate_and_format)
        self.ingredient_validated.connect(self.add_ingredient) 
        self.ui.btn_subtract.clicked.connect(self.request_removal)

        # Dynamic validation for QLineEdit fields
        dynamic_validation(self.ui.le_quantity, FLOAT)
        dynamic_validation(self.ui.le_ingredient_name, NAME)

        # Dynamic (positive) validation for QComboBox fields
        self.ui.cb_unit.cb_validated.connect(lambda:clear_error_styles(self.ui.cb_unit))  
        self.ui.cb_ingredient_category.cb_validated.connect(lambda:clear_error_styles(self.ui.cb_ingredient_category))  

    def validate_and_format(self):
        """
        Validates and formats ingredient data.
        - If validation fails, applies error styles to the specific field.
        - If valid, clears error styles and emits formatted data.
        """
        from app.database.db_formatters import format_ingredient_data #🔸Lazy imports to avoid circular dependency
        from app.database.db_validators import validate_data_fields #🔸Lazy imports to avoid circular dependency


        # Step 1️⃣: Get data
        ingredient_data = self.ingredient_data

        # Step 2️⃣: Validate data
        if validate_data_fields(ingredient_data):
            DebugLogger().log("🔵 Ingredient Validation Passed", "info")

            # Step 3️⃣3️: Format data
            formatted_data = format_ingredient_data(**ingredient_data)
            DebugLogger().log("🟢 Ingredient Formatted: {formatted_data}", "debug")

            # Step 4️⃣: Emit data
            DebugLogger().log("🔵 Emitting Ingredient Data 🔵\n", "info")
            self.ingredient_validated.emit(formatted_data)
        else:
            DebugLogger().log("🔴 Ingredient Validation Failed", "error")

    def add_ingredient(self):
        """Handles the addition of a new ingredient widget."""
        self.add_ingredient_requested.emit(self)

    def request_removal(self):
        """Emit signal to remove this widget, unless it's the last one."""
        if self.parent() and len(self.parent().findChildren(IngredientWidget)) > 1:
            self.remove_ingredient_requested.emit(self)

    def populate_comboboxes(self):
        """Populates ingredient category and unit comboboxes."""

        from app.helpers.app_helpers import populate_combobox #🔸Lazy import to avoid circular dependency

        populate_combobox(self.ui.cb_ingredient_category, INGREDIENT_CATEGORIES)
        populate_combobox(self.ui.cb_unit, MEASUREMENT_UNITS)

    def apply_styles(self):
        """Applies custom styles, including button hover effects."""
        from style_manager import StyleManager #🔸Lazy imports to avoid circular dependency

        StyleManager.apply_hover_effects(self.ui.btn_add, (12, 12)) 

#🔸END
        

        
 