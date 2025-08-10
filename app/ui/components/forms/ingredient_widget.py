"""app/ui/components/forms/ingredient_widget.py

IngredientWidget for managing individual ingredients in recipes.
"""


# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QGridLayout, QLineEdit, QSizePolicy, QWidget

from app.config import (FLOAT_VALIDATOR, INGREDIENT_CATEGORIES,
                        MEASUREMENT_UNITS, NAME_PATTERN)
from app.style.icon import Name, Type
from app.core.database.db import create_session
from app.core.dtos import IngredientSearchDTO
from app.core.services.ingredient_service import IngredientService
from app.ui.components.inputs import SmartLineEdit
from app.ui.components.widgets import ComboBox, ToolButton
from app.ui.helpers import clear_error_styles, dynamic_validation
from app.ui.helpers.ui_helpers import set_fixed_height_for_layout_widgets

# ── Constants ───────────────────────────────────────────────────────────────────
FIXED_HEIGHT = 45  # fixed height for input fields in the ingredient widget

# ── Class Definition ────────────────────────────────────────────────────────────
class IngredientWidget(QWidget):
    add_ingredient_requested = Signal(QWidget)
    remove_ingredient_requested = Signal(QWidget)
    ingredient_validated = Signal(dict)

    def __init__(self, removable=True, parent=None):
        """
        Initializes the IngredientWidget with a grid layout and sets up UI components.
        The ingredient name input is an editable ComboBox populated with existing
        ingredient names. Selecting an existing ingredient auto-populates its category.

        Args:
            removable (bool): If True, the widget will have a remove button.
            parent (QWidget, optional): Parent widget for this ingredient widget.
        """
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.grid_layout = QGridLayout(self)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setHorizontalSpacing(5)
        self.grid_layout.setVerticalSpacing(5)
        self.setObjectName("IngredientWidget")
        self.setProperty("class", "IngredientWidget")
        # Initialize IngredientService with a new DB session
        self._session = create_session()
        self.ingredient_service = IngredientService(self._session)
        self.exact_match = None
        self._setup_ui()
        self.setup_event_logic()

    def _setup_ui(self):
        """Sets up the UI components and layout for the ingredient widget."""
        self.grid_layout.setAlignment(Qt.AlignTop)

        self.le_quantity = QLineEdit(self)
        self.le_quantity.setPlaceholderText("Qty.")
        self.grid_layout.addWidget(self.le_quantity, 0, 0, 1, 1)

        self.cb_unit = ComboBox(
            list_items  = MEASUREMENT_UNITS,
            placeholder = "Unit"
        )
        self.cb_unit.completer.popup().setObjectName("CompleterPopup")
        self.grid_layout.addWidget(self.cb_unit, 0, 1, 1, 1)

        all_ingredient_names = self.ingredient_service.list_distinct_names()
        self.sle_ingredient_name = SmartLineEdit(
            list_items  = all_ingredient_names,
            placeholder = "Ingredient Name",
        )
        self.sle_ingredient_name.setFixedHeight(FIXED_HEIGHT)
        self.grid_layout.addWidget(self.sle_ingredient_name, 0, 2, 1, 1)

        self.cb_ingredient_category = ComboBox(
            list_items  = INGREDIENT_CATEGORIES,
            placeholder = "Category"
        )
        self.grid_layout.addWidget(self.cb_ingredient_category, 0, 3, 1, 1)

        self.btn_ico_subtract = ToolButton(Type.DEFAULT, Name.SUBTRACT)
        self.btn_ico_subtract.setFixedWidth(FIXED_HEIGHT) # square button
        self.grid_layout.addWidget(self.btn_ico_subtract, 0, 4, 1, 1)

        self.btn_ico_add = ToolButton(Type.DEFAULT, Name.ADD)
        self.btn_ico_add.setFixedWidth(FIXED_HEIGHT)  # square button
        self.grid_layout.addWidget(self.btn_ico_add, 0, 5, 1, 1)

        # set column stretch factors: qty, unit, category = 1; name = 3; buttons = 0
        self.grid_layout.setColumnStretch(0, 1)  # Qty
        self.grid_layout.setColumnStretch(1, 1)  # Unit
        self.grid_layout.setColumnStretch(2, 3)  # Ingredient Name (larger)
        self.grid_layout.setColumnStretch(3, 1)  # Category
        self.grid_layout.setColumnStretch(4, 0)  # Subtract button
        self.grid_layout.setColumnStretch(5, 0)  # Add button

        set_fixed_height_for_layout_widgets(
            layout = self.grid_layout,
            height = FIXED_HEIGHT,
        )

    def setup_event_logic(self):
        """Connects signals to their respective slots for handling ingredient data."""
        self.btn_ico_add.clicked.connect(self.emit_ingredient_data)
        self.btn_ico_subtract.clicked.connect(self.request_removal)
        self.ingredient_validated.connect(self.add_ingredient)

        dynamic_validation(self.le_quantity, FLOAT_VALIDATOR)

        self.sle_ingredient_name.currentTextChanged.connect(self._ingredient_name_changed) # connect new signal

        self.cb_unit.selection_validated.connect(lambda: clear_error_styles(self.cb_unit))
        self.cb_ingredient_category.selection_validated.connect(lambda: clear_error_styles(self.cb_ingredient_category))

    def _ingredient_name_changed(self, text: str):
        """
        Handles changes in the ingredient name field (SmartLineEdit).
        If the entered text matches an existing ingredient (case-insensitive exact match),
        its category is auto-populated and the category ComboBox may be disabled.
        Otherwise, the category ComboBox is enabled for manual input.
        """
        current_text = text.strip()
        self.cb_ingredient_category.setEnabled(True)

        if not current_text:
            self.cb_ingredient_category.setCurrentIndex(-1)
            clear_error_styles(self.sle_ingredient_name)  # SmartLineEdit is now a QLineEdit
            return

        # validate the ingredient name against the NAME_PATTERN
        if not NAME_PATTERN.match(current_text):
            self.sle_ingredient_name.setStyleSheet("border: 1px solid red;")
            return
        else:
            clear_error_styles(self.sle_ingredient_name)

        search_dto = IngredientSearchDTO(search_term=current_text)
        matching_ingredients = self.ingredient_service.find_matching_ingredients(search_dto)

        exact_match = None
        for ingredient in matching_ingredients:
            if ingredient.ingredient_name.lower() == current_text.lower():
                exact_match = ingredient
                self.exact_match = exact_match
                break

        if exact_match:
            category_index = self.cb_ingredient_category.findText(
                exact_match.ingredient_category,
                Qt.MatchFlag.MatchFixedString | Qt.MatchFlag.MatchCaseSensitive,
            )

            if category_index < 0:
                category_index = self.cb_ingredient_category.findText(
                    exact_match.ingredient_category,
                    Qt.MatchFlag.MatchFixedString | Qt.MatchFlag.MatchContains,
                )

            if category_index >= 0:
                self.cb_ingredient_category.setCurrentIndex(category_index)
            else:
                self.cb_ingredient_category.addItem(exact_match.ingredient_category)
                self.cb_ingredient_category.setCurrentText(exact_match.ingredient_category)

            clear_error_styles(self.cb_ingredient_category)
        else:
            self.cb_ingredient_category.setCurrentIndex(-1)
            self.cb_ingredient_category.setEnabled(True)

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
        """Returns a plain dict that matches RecipeIngredientDTO fields"""
        return {
        "ingredient_name": self.sle_ingredient_name.text().strip(),
        "ingredient_category": self.cb_ingredient_category.currentText().strip(),
        "unit": self.cb_unit.currentText().strip(),
        "quantity": float(self.le_quantity.text().strip() or 0),
        "existing_ingredient_id": self.exact_match.id if self.exact_match else None,
        }

