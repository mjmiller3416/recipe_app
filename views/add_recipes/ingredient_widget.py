"""views/add_recipes/ingredient_widget.py

IngredientWidget for managing individual ingredients in recipes.
"""


# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Signal, Qt 
from PySide6.QtWidgets import QGridLayout, QLineEdit, QWidget

from config import (FLOAT_VALIDATOR, INGREDIENT_CATEGORIES, INGREDIENT_WIDGET,
                    MEASUREMENT_UNITS, NAME_PATTERN)
from ui.components.inputs import SmartComboBox
from ui.iconkit import ToolButtonIcon
from ui.tools import clear_error_styles, dynamic_validation
from services.ingredient_service import IngredientService
from services.dtos.ingredient_dtos import IngredientSearchDTO

# ── Constants ───────────────────────────────────────────────────────────────────
FIXED_HEIGHT = 32  # fixed height for input fields in the ingredient widget

# ── Class Definition ────────────────────────────────────────────────────────────
class IngredientWidget(QWidget):
    add_ingredient_requested = Signal(QWidget)
    remove_ingredient_requested = Signal(QWidget)
    ingredient_validated = Signal(dict)

    def __init__(self, removable=True, parent=None):
        """
        Initializes the IngredientWidget with a grid layout and sets up UI components.
        The ingredient name input is an editable SmartComboBox populated with existing
        ingredient names. Selecting an existing ingredient auto-populates its category.

        Args:
            removable (bool): If True, the widget will have a remove button.
            parent (QWidget, optional): Parent widget for this ingredient widget.
        """
        super().__init__(parent)
        self.setObjectName("IngredientWidget")
        self.ingredient_service = IngredientService() # instantiate IngredientService
        self._setup_ui()
        self.setup_event_logic()
        self.exact_match = None

    def _setup_ui(self):
        """Sets up the UI components and layout for the ingredient widget."""
        self.grid_layout = QGridLayout(self)
        self.setLayout(self.grid_layout)

        self.le_quantity = QLineEdit(self)
        self.le_quantity.setPlaceholderText("Qty.")
        self.grid_layout.addWidget(self.le_quantity, 0, 0, 1, 1)

        self.scb_unit = SmartComboBox(
            list = MEASUREMENT_UNITS,
            placeholder = "Unit"
        )
        self.grid_layout.addWidget(self.scb_unit, 0, 1, 1, 1)

        # Replace QLineEdit with SmartComboBox for ingredient name
        all_ingredient_names = self.ingredient_service.list_all_ingredient_names()
        self.scb_ingredient_name = SmartComboBox(
            list=all_ingredient_names,
            placeholder="Ingredient Name",
            editable=True  # Make the SmartComboBox editable
        )
        self.grid_layout.addWidget(self.scb_ingredient_name, 0, 2, 1, 1)

        self.scb_ingredient_category = SmartComboBox(
            list = INGREDIENT_CATEGORIES,
            placeholder = "Category"
        )
        self.grid_layout.addWidget(self.scb_ingredient_category, 0, 3, 1, 1)

        self.btn_ico_subtract = ToolButtonIcon(
            file_path = INGREDIENT_WIDGET["ICON_SUBTRACT"],
            icon_size = INGREDIENT_WIDGET["ICON_SIZE"],
            variant   = INGREDIENT_WIDGET["DYNAMIC"]
        )
        self.btn_ico_subtract.setFixedWidth(FIXED_HEIGHT) # square button
        self.grid_layout.addWidget(self.btn_ico_subtract, 0, 4, 1, 1)

        self.btn_ico_add = ToolButtonIcon(
            file_path = INGREDIENT_WIDGET["ICON_ADD"],
            icon_size = INGREDIENT_WIDGET["ICON_SIZE"],
            variant   = INGREDIENT_WIDGET["DYNAMIC"]
        )
        self.btn_ico_add.setFixedWidth(FIXED_HEIGHT)  # square button
        self.grid_layout.addWidget(self.btn_ico_add, 0, 5, 1, 1)

        # set column stretch factors: qty, unit, category = 1; name = 3; buttons = 0
        self.grid_layout.setColumnStretch(0, 1)  # Qty
        self.grid_layout.setColumnStretch(1, 1)  # Unit
        self.grid_layout.setColumnStretch(2, 3)  # Ingredient Name (larger)
        self.grid_layout.setColumnStretch(3, 1)  # Category
        self.grid_layout.setColumnStretch(4, 0)  # Subtract button
        self.grid_layout.setColumnStretch(5, 0)  # Add button

        for i in range(self.grid_layout.count()):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.setFixedHeight(FIXED_HEIGHT)

    def setup_event_logic(self):
        """Connects signals to their respective slots for handling ingredient data."""
        self.btn_ico_add.clicked.connect(self.emit_ingredient_data)
        self.btn_ico_subtract.clicked.connect(self.request_removal)
        self.ingredient_validated.connect(self.add_ingredient)

        dynamic_validation(self.le_quantity, FLOAT_VALIDATOR)
        # dynamic_validation(self.le_ingredient_name, NAME) # Removed for SmartComboBox

        self.scb_ingredient_name.currentTextChanged.connect(self._ingredient_name_changed) # Connect new signal
        # Ensure validation signal from SmartComboBox is handled if needed for styling, or rely on internal validation.
        # self.scb_ingredient_name.selection_validated.connect(lambda: clear_error_styles(self.scb_ingredient_name))

        self.scb_unit.selection_validated.connect(lambda: clear_error_styles(self.scb_unit))
        self.scb_ingredient_category.selection_validated.connect(lambda: clear_error_styles(self.scb_ingredient_category))

    def _ingredient_name_changed(self, text: str):
        """
        Handles changes in the ingredient name SmartComboBox.
        If the entered text matches an existing ingredient (case-insensitive exact match),
        its category is auto-populated and the category ComboBox might be disabled.
        Otherwise, the category ComboBox is enabled for manual input.
        """
        current_text = text.strip()
        self.scb_ingredient_category.setEnabled(True) # Default to enabled

        if not current_text:
            self.scb_ingredient_category.setCurrentIndex(-1) # Clear category
            clear_error_styles(self.scb_ingredient_name) # Clear any error style on name
            return

        # Validate ingredient name format (e.g., if it should not be empty after stripping)
        # This could be a simple check or use a regex from config if available
        if not NAME_PATTERN.match(current_text):
            self.scb_ingredient_name.setStyleSheet("border: 1px solid red;") # Example error style
            # self.cb_ingredient_category.setCurrentIndex(-1) # Optionally clear category on name error
            return
        else:
            clear_error_styles(self.scb_ingredient_name) # Clear error style if valid

        search_dto = IngredientSearchDTO(search_term=current_text)
        # Assuming find_matching_ingredients uses a connection managed by the service or ModelBase
        matching_ingredients = self.ingredient_service.find_matching_ingredients(search_dto)

        exact_match = None
        for ingredient in matching_ingredients:
            if ingredient.ingredient_name.lower() == current_text.lower():
                exact_match = ingredient
                self.exact_match = exact_match  # Store the exact match in self.exact_match
                break
        if exact_match:
            # Exact match found, auto-populate category
            category_index = self.scb_ingredient_category.findText(exact_match.ingredient_category, Qt.MatchFlag.MatchFixedString | Qt.MatchFlag.MatchCaseSensitive)
            # Try case-insensitive if sensitive fails or if that's preferred
            if category_index < 0:
                 category_index = self.scb_ingredient_category.findText(exact_match.ingredient_category, Qt.MatchFlag.MatchFixedString | Qt.MatchFlag.MatchContains) # Broader match if needed

            if category_index >= 0:
                self.scb_ingredient_category.setCurrentIndex(category_index)
                # self.scb_ingredient_category.setEnabled(False) # Optionally disable category selection
            else:
                # Category from DB not in standard list, add it, select, and then optionally disable
                self.scb_ingredient_category.addItem(exact_match.ingredient_category)
                self.scb_ingredient_category.setCurrentText(exact_match.ingredient_category)
                # self.scb_ingredient_category.setEnabled(False) # Optionally disable category selection
            clear_error_styles(self.scb_ingredient_category) # Clear error style on successful auto-population
        else:
            # No exact match, clear category and ensure it's enabled for manual input
            self.scb_ingredient_category.setCurrentIndex(-1)
            self.scb_ingredient_category.setEnabled(True)

    def emit_ingredient_data(self):
        """Emits the ingredient data as a dictionary when the add button is clicked."""
        payload = self.to_payload()
        self.ingredient_validated.emit(payload)

    def add_ingredient(self):
        """Emits a signal to request adding a new ingredient widget."""
        self.add_ingredient_requested.emit(self)

    def request_removal(self):
        """Emits a signal to request removal of this ingredient widget."""
        if self.parent() and len(self.parent().findChildren(IngredientWidget)) > 1:
            self.remove_ingredient_requested.emit(self)
    
    def to_payload(self) -> dict:
        """Returns a plain dict that matches RecipeIngredientInputDTO fields"""
        return {
        "ingredient_name": self.scb_ingredient_name.currentText().strip(),
        "ingredient_category": self.scb_ingredient_category.currentText().strip(),
        "unit": self.scb_unit.currentText().strip(),
        "quantity": float(self.le_quantity.text().strip() or 0),
        "existing_ingredient_id": self.exact_match.id if self.exact_match else None,
        }

