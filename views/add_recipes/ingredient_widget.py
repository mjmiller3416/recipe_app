"""views/add_recipes/ingredient_widget.py

IngredientWidget for managing individual ingredients in recipes.
"""


# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QGridLayout, QLineEdit, QWidget

from config import (FLOAT_VALIDATOR, INGREDIENT_CATEGORIES, INGREDIENT_WIDGET,
                    MEASUREMENT_UNITS, NAME_PATTERN)
from services.dtos.ingredient_dtos import IngredientSearchDTO
from services.ingredient_service import IngredientService
from ui.components.inputs import CustomComboBox
from ui.iconkit import ToolButtonIcon
from ui.tools import clear_error_styles, dynamic_validation

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
        The ingredient name input is an editable CustomComboBox populated with existing
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

        self.scb_unit = CustomComboBox(
            list_items  = MEASUREMENT_UNITS,
            placeholder = "Unit"
        )
        self.grid_layout.addWidget(self.scb_unit, 0, 1, 1, 1)

        all_ingredient_names = self.ingredient_service.list_all_ingredient_names()
        self.scb_ingredient_name = CustomComboBox(
            list_items  = all_ingredient_names,
            placeholder = "Ingredient Name",
            editable    = True  # make the CustomComboBox editable
        )
        self.grid_layout.addWidget(self.scb_ingredient_name, 0, 2, 1, 1)

        self.scb_ingredient_category = CustomComboBox(
            list_items  = INGREDIENT_CATEGORIES,
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

        self.scb_ingredient_name.currentTextChanged.connect(self._ingredient_name_changed) # connect new signal

        self.scb_unit.selection_validated.connect(lambda: clear_error_styles(self.scb_unit))
        self.scb_ingredient_category.selection_validated.connect(lambda: clear_error_styles(self.scb_ingredient_category))

    def _ingredient_name_changed(self, text: str):
        """
        Handles changes in the ingredient name CustomComboBox.
        If the entered text matches an existing ingredient (case-insensitive exact match),
        its category is auto-populated and the category ComboBox might be disabled.
        Otherwise, the category ComboBox is enabled for manual input.
        """
        current_text = text.strip()
        self.scb_ingredient_category.setEnabled(True) # default to enabled

        if not current_text:
            self.scb_ingredient_category.setCurrentIndex(-1) # clear category
            clear_error_styles(self.scb_ingredient_name) # clear any error style on name
            return

        # validate the ingredient name against the NAME_PATTERN
        if not NAME_PATTERN.match(current_text):
            self.scb_ingredient_name.setStyleSheet("border: 1px solid red;") # error style
            return
        else:
            clear_error_styles(self.scb_ingredient_name) # clear error style if valid

        search_dto = IngredientSearchDTO(search_term=current_text)
        matching_ingredients = self.ingredient_service.find_matching_ingredients(search_dto)

        exact_match = None
        for ingredient in matching_ingredients:
            if ingredient.ingredient_name.lower() == current_text.lower():
                exact_match = ingredient
                self.exact_match = exact_match  # store the exact match in self.exact_match
                break
        if exact_match:
            # exact match found, auto-populate category
            category_index = self.scb_ingredient_category.findText(exact_match.ingredient_category, Qt.MatchFlag.MatchFixedString | Qt.MatchFlag.MatchCaseSensitive)
            # try case-insensitive if sensitive fails 
            if category_index < 0:
                 category_index = self.scb_ingredient_category.findText(exact_match.ingredient_category, Qt.MatchFlag.MatchFixedString | Qt.MatchFlag.MatchContains) # Broader match if needed

            if category_index >= 0:
                self.scb_ingredient_category.setCurrentIndex(category_index)
            else:
                self.scb_ingredient_category.addItem(exact_match.ingredient_category)
                self.scb_ingredient_category.setCurrentText(exact_match.ingredient_category)
            clear_error_styles(self.scb_ingredient_category) # clear error style on successful auto-population
        else:
            # no exact match, clear category and ensure it's enabled for manual input
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

