"""app/ui/views/add_recipes/_ingredient_form.py

This module defines the IngredientForm class, which provides a UI component
for entering and managing individual ingredient details within a recipe.
It includes fields for ingredient name, quantity, unit, and category, along
with buttons for reordering and removing the ingredient entry.
"""

# ── Imports ──
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QWidget

from app.config import INGREDIENT_CATEGORIES, MEASUREMENT_UNITS, FLOAT_VALIDATOR, NAME_PATTERN
from app.core.database import create_session
from app.core.services import IngredientService
from app.core.dtos import IngredientSearchDTO
from app.style import Type, Name, Theme, Qss
from app.ui.components.widgets.combobox import ComboBox
from app.ui.components.inputs.smart_line_edit import SmartLineEdit
from app.ui.components.widgets.button import ToolButton
from app.core.utils import sanitize_form_input, safe_float_conversion
from app.ui.utils import clear_error_styles, dynamic_validation


class IngredientForm(QWidget):
    add_ingredient_requested = Signal(QWidget)
    remove_ingredient_requested = Signal(QWidget)
    ingredient_validated = Signal(dict)

    def __init__(self, removable=True, parent=None):
        """
        Initializes the IngredientForm with a grid layout and sets up UI components.
        The ingredient name input is an editable ComboBox populated with existing
        ingredient names. Selecting an existing ingredient auto-populates its category.

        Args:
            removable (bool): If True, the widget will have a remove button.
            parent (QWidget, optional): Parent widget for this ingredient widget.
        """
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)

        # Register with Theme API for Material3 styling
        # Theme.register_widget(self, Qss.INGREDIENT_WIDGET)

        # Create horizontal layout for row-based design
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(18, 18, 18, 18)
        self.main_layout.setSpacing(12)
        self.setObjectName("IngredientForm")
        # Initialize IngredientService with a new DB session
        self._session = create_session()
        self.ingredient_service = IngredientService(self._session)
        self.exact_match = None
        self._build_ui()
        self.setup_event_logic()

    def _build_ui(self):
        """Sets up the UI components and layout for the ingredient widget."""

        # Drag handle for reordering
        self.drag_handle = ToolButton(Type.DEFAULT, Name.GRIP_DOTS)
        self.drag_handle.setObjectName("DragHandle")
        self.drag_handle.setIconSize(24, 24)
        self.drag_handle.setStateDefault("on_surface")
        self.drag_handle.setStateHover("tertiary")
        self.main_layout.addWidget(self.drag_handle)

        # Unit field - compact (create first to get reference height)
        self.cb_unit = ComboBox(
            list_items=MEASUREMENT_UNITS,
            placeholder="Unit"
        )
        self.cb_unit.setObjectName("ComboBox UnitField")
        self.main_layout.addWidget(self.cb_unit)

        # Get the ComboBox height to use for other fields
        combobox_height = self.cb_unit.sizeHint().height()

        # Quantity field - compact
        self.le_quantity = QLineEdit(self)
        self.le_quantity.setPlaceholderText("Qty")
        self.le_quantity.setObjectName("QuantityField")
        self.le_quantity.setFixedHeight(combobox_height)
        self.main_layout.addWidget(self.le_quantity)

        # Ingredient name field - expandable
        all_ingredient_names = self.ingredient_service.list_distinct_names()
        self.sle_ingredient_name = SmartLineEdit(
            list_items=all_ingredient_names,
            placeholder="Ingredient Name"
        )
        self.sle_ingredient_name.setObjectName("NameField")
        self.sle_ingredient_name.setFixedHeight(combobox_height)
        self.main_layout.addWidget(self.sle_ingredient_name)

        # Category field - medium width
        self.cb_ingredient_category = ComboBox(
            list_items=INGREDIENT_CATEGORIES,
            placeholder="Category"
        )
        self.cb_ingredient_category.setObjectName("ComboBox CategoryField")
        self.main_layout.addWidget(self.cb_ingredient_category)

        # Delete button - replaces subtract/add buttons
        self.btn_delete = ToolButton(Type.DEFAULT, Name.TRASH)
        self.btn_delete.setObjectName("DeleteButton")
        self.btn_delete.setIconSize(32, 32)
        self.btn_delete.setStateDefault("on_surface")
        self.btn_delete.setStateHover("tertiary")
        self.main_layout.addWidget(self.btn_delete)

        # Set stretch factors for proper proportions
        self.main_layout.setStretchFactor(self.drag_handle, 0)
        self.main_layout.setStretchFactor(self.cb_unit, 0)  # Fixed width
        self.main_layout.setStretchFactor(self.le_quantity, 0)  # Fixed width
        self.main_layout.setStretchFactor(self.sle_ingredient_name, 3)  # Expandable
        self.main_layout.setStretchFactor(self.cb_ingredient_category, 0)  # Fixed width
        self.main_layout.setStretchFactor(self.btn_delete, 0)

    def setup_event_logic(self):
        """Connects signals to their respective slots for handling ingredient data."""
        self.btn_delete.clicked.connect(self.request_removal)
        # Note: Add ingredient functionality will be handled at container level

        dynamic_validation(self.le_quantity, FLOAT_VALIDATOR)

        self.sle_ingredient_name.currentTextChanged.connect(self._ingredient_name_changed) # connect new signal

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

    def get_ingredient_data(self) -> dict:
        """Returns the ingredient data as a dictionary for external collection."""
        return self.to_payload()

    def request_removal(self):
        """Emits a signal to request removal of this ingredient widget."""
        if self.parent() and len(self.parent().findChildren(IngredientForm)) > 1:
            self.remove_ingredient_requested.emit(self)

    def to_payload(self) -> dict:
        """Returns a plain dict that matches RecipeIngredientDTO fields"""
        return {
        "ingredient_name": sanitize_form_input(self.sle_ingredient_name.text()),
        "ingredient_category": sanitize_form_input(self.cb_ingredient_category.currentText()),
        "unit": sanitize_form_input(self.cb_unit.currentText()),
        "quantity": safe_float_conversion(self.le_quantity.text().strip()),
        "existing_ingredient_id": self.exact_match.id if self.exact_match else None,
        }
