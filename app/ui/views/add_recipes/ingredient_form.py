"""app/ui/views/add_recipes/ingredient_form.py

Contains the IngredientForm widget for adding/editing individual ingredients in the AddRecipes view.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QWidget

from _dev_tools import DebugLogger
from app.config import (
    FLOAT_VALIDATOR,
    INGREDIENT_CATEGORIES,
    MEASUREMENT_UNITS,
    NAME_PATTERN,
)
from app.style import Name, Qss, Theme
from app.ui.components.inputs.smart_line_edit import SmartLineEdit
from app.ui.components.widgets.button import ToolButton, Type
from app.ui.components.widgets.combobox import ComboBox
from app.ui.utils.form_utils import clear_error_styles, dynamic_validation
class IngredientForm(QWidget):
    
    # ── Signals ──────────────────────────────────────────────────────────────────────────────────────────────
    add_ingredient_requested = Signal(QWidget)
    remove_ingredient_requested = Signal(QWidget)
    ingredient_validated = Signal(dict)
    ingredient_data_changed = Signal()  # New signal for data changes

    def __init__(self, ingredient_view_model=None, removable=True, parent=None):
        """
        Initializes the IngredientForm with a grid layout and sets up UI components.
        The ingredient name input is an editable ComboBox populated with existing
        ingredient names. Selecting an existing ingredient auto-populates its category.

        Args:
            ingredient_view_model (IngredientViewModel): ViewModel for ingredient operations
            removable (bool): If True, the widget will have a remove button.
            parent (QWidget, optional): Parent widget for this ingredient widget.
        """
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)

        # Register with Theme API for Material3 styling
        Theme.register_widget(self, Qss.INGREDIENT_WIDGET)

        # Create horizontal layout for row-based design
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(18, 18, 18, 18)
        self.main_layout.setSpacing(12)
        self.setObjectName("IngredientForm")

        # Store ViewModel reference - no direct Core service access
        self.ingredient_view_model = ingredient_view_model
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
        self.cb_unit.setObjectName("UnitField")
        self.main_layout.addWidget(self.cb_unit)

        # Get the ComboBox height to use for other fields
        combobox_height = self.cb_unit.sizeHint().height()

        # Quantity field - compact
        self.le_quantity = QLineEdit(self)
        self.le_quantity.setPlaceholderText("Qty")
        self.le_quantity.setObjectName("QuantityField")
        self.le_quantity.setFixedHeight(combobox_height)
        self.main_layout.addWidget(self.le_quantity)

        # Ingredient name field - expandable with lazy loading optimization
        # Performance optimization: start with empty list, populate on first focus
        self.sle_ingredient_name = SmartLineEdit(
            list_items=[],  # Start empty for faster initialization
            placeholder="Ingredient Name"
        )

        # Set up lazy loading for autocomplete data
        self._autocomplete_loaded = False
        self.sle_ingredient_name.setObjectName("NameField")
        self.sle_ingredient_name.setFixedHeight(combobox_height)
        self.main_layout.addWidget(self.sle_ingredient_name)

        # Category field - medium width
        self.cb_ingredient_category = ComboBox(
            list_items=INGREDIENT_CATEGORIES,
            placeholder="Category"
        )
        self.cb_ingredient_category.setObjectName("CategoryField")
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

        # Performance optimization: lazy load autocomplete data on first focus
        self.sle_ingredient_name.focusInEvent = self._on_ingredient_name_focus_in

        # Connect real-time validation through ViewModel
        self.sle_ingredient_name.currentTextChanged.connect(self._ingredient_name_changed)
        if self.ingredient_view_model:
            self.sle_ingredient_name.textChanged.connect(
                lambda text: self.ingredient_view_model.validate_ingredient_name_real_time(text)
            )
            # TODO: Fix validation styling conflicts - validation applies inline styles that override QSS theme styling
            # self.cb_ingredient_category.currentTextChanged.connect(
            #     lambda text: self.ingredient_view_model.validate_ingredient_category_real_time(text)
            # )
            self.le_quantity.textChanged.connect(
                lambda text: self.ingredient_view_model.validate_ingredient_quantity_real_time(text)
            )

            # Connect ViewModel validation signals to UI updates
            self.ingredient_view_model.ingredient_name_validation_changed.connect(self._on_name_validation_changed)
            self.ingredient_view_model.ingredient_category_validation_changed.connect(self._on_category_validation_changed)
            self.ingredient_view_model.ingredient_quantity_validation_changed.connect(self._on_quantity_validation_changed)

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
            clear_error_styles(self.sle_ingredient_name)
            self.exact_match = None
            self.ingredient_data_changed.emit()
            return

        # validate the ingredient name against the NAME_PATTERN
        if not NAME_PATTERN.match(current_text):
            self.sle_ingredient_name.setStyleSheet("border: 2px solid #f44336;")
            self.exact_match = None
            self.ingredient_data_changed.emit()
            return
        else:
            clear_error_styles(self.sle_ingredient_name)

        # Use ViewModel for ingredient matching if available
        if self.ingredient_view_model:
            match_result = self.ingredient_view_model.find_ingredient_matches(current_text)

            if match_result.exact_match:
                self.exact_match = match_result.exact_match
                category = match_result.exact_match.ingredient_category

                # Find and set category in ComboBox
                category_index = self.cb_ingredient_category.findText(
                    category,
                    Qt.MatchFlag.MatchFixedString | Qt.MatchFlag.MatchCaseSensitive,
                )

                if category_index < 0:
                    category_index = self.cb_ingredient_category.findText(
                        category,
                        Qt.MatchFlag.MatchFixedString | Qt.MatchFlag.MatchContains,
                    )

                if category_index >= 0:
                    self.cb_ingredient_category.setCurrentIndex(category_index)
                else:
                    self.cb_ingredient_category.addItem(category)
                    self.cb_ingredient_category.setCurrentText(category)

                clear_error_styles(self.cb_ingredient_category)
            else:
                self.exact_match = None
                # Suggest category if available
                if match_result.suggested_category:
                    category_index = self.cb_ingredient_category.findText(
                        match_result.suggested_category,
                        Qt.MatchFlag.MatchFixedString | Qt.MatchFlag.MatchCaseSensitive,
                    )
                    if category_index >= 0:
                        self.cb_ingredient_category.setCurrentIndex(category_index)
                else:
                    self.cb_ingredient_category.setCurrentIndex(-1)

                self.cb_ingredient_category.setEnabled(True)
        else:
            # Fallback when no ViewModel is available
            self.exact_match = None
            self.cb_ingredient_category.setCurrentIndex(-1)
            self.cb_ingredient_category.setEnabled(True)

        # Emit signal to notify parent of data changes
        self.ingredient_data_changed.emit()

    def _on_ingredient_name_focus_in(self, event):
        """Handle focus in event for ingredient name field with lazy loading."""
        # Performance optimization: load autocomplete data only when needed
        if not self._autocomplete_loaded and self.ingredient_view_model:
            try:
                # Load autocomplete cache if not already loaded
                if not self.ingredient_view_model._cache_loaded:
                    self.ingredient_view_model._load_autocomplete_cache()

                # Update SmartLineEdit with autocomplete data
                ingredient_names = self.ingredient_view_model._autocomplete_cache
                if ingredient_names:
                    self.sle_ingredient_name.source.setStringList(ingredient_names)
                    self._autocomplete_loaded = True
                    DebugLogger.log(f"Loaded {len(ingredient_names)} ingredient names for autocomplete", "debug")

            except Exception as e:
                DebugLogger.log(f"Failed to lazy load ingredient names: {e}", "warning")

        # Call original focus in event
        from PySide6.QtWidgets import QLineEdit
        QLineEdit.focusInEvent(self.sle_ingredient_name, event)

    def get_ingredient_data(self) -> dict:
        """Returns the ingredient data as a dictionary for external collection."""
        return self._to_payload()

    def request_removal(self):
        """Emits a signal to request removal of this ingredient widget."""
        if self.parent() and len(self.parent().findChildren(IngredientForm)) > 1:
            self.remove_ingredient_requested.emit(self)

    def _to_payload(self) -> dict:
        """Returns a plain dict that matches RecipeIngredientDTO fields"""
        # Import here to avoid circular imports
        from app.core.utils.conversion_utils import safe_float_conversion
        from app.core.utils.text_utils import sanitize_form_input

        return {
            "ingredient_name": sanitize_form_input(self.sle_ingredient_name.text()),
            "ingredient_category": sanitize_form_input(self.cb_ingredient_category.currentText()),
            "unit": sanitize_form_input(self.cb_unit.currentText()),
            "quantity": safe_float_conversion(self.le_quantity.text().strip()),
            "existing_ingredient_id": self.exact_match.id if self.exact_match else None,
        }

    # ── Validation Event Handlers ───────────────────────────────────────────────────────────────────────────────
    def _on_name_validation_changed(self, is_valid: bool, error_message: str):
        """Handle ingredient name validation changes."""
        if is_valid:
            self.sle_ingredient_name.setStyleSheet("")
            self.sle_ingredient_name.setToolTip("")
        else:
            self.sle_ingredient_name.setStyleSheet("border: 2px solid #f44336;")
            self.sle_ingredient_name.setToolTip(error_message)

    def _on_category_validation_changed(self, is_valid: bool, error_message: str):
        """Handle ingredient category validation changes."""
        if is_valid:
            self.cb_ingredient_category.setStyleSheet("")
            self.cb_ingredient_category.setToolTip("")
        else:
            self.cb_ingredient_category.setStyleSheet("border: 2px solid #f44336;")
            self.cb_ingredient_category.setToolTip(error_message)

    def _on_quantity_validation_changed(self, is_valid: bool, error_message: str):
        """Handle ingredient quantity validation changes."""
        if is_valid:
            self.le_quantity.setStyleSheet("")
            self.le_quantity.setToolTip("" if not error_message else error_message)  # Keep warnings as tooltips
        else:
            self.le_quantity.setStyleSheet("border: 2px solid #f44336;")
            self.le_quantity.setToolTip(error_message)

    def cleanup(self):
        """Clean up resources to prevent memory leaks."""
        try:
            # Disconnect signals to prevent lingering connections
            if self.ingredient_view_model:
                self.ingredient_view_model.ingredient_name_validation_changed.disconnect()
                self.ingredient_view_model.ingredient_category_validation_changed.disconnect()
                self.ingredient_view_model.ingredient_quantity_validation_changed.disconnect()

            # Clear autocomplete data to free memory
            if hasattr(self, 'sle_ingredient_name') and self.sle_ingredient_name.source:
                self.sle_ingredient_name.source.setStringList([])

            # Clear references
            self.ingredient_view_model = None
            self.exact_match = None

            DebugLogger.log("IngredientForm cleaned up successfully", "debug")

        except Exception as e:
            DebugLogger.log(f"Error during IngredientForm cleanup: {e}", "warning")
