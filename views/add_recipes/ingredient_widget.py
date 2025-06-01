"""views/add_recipes/ingredient_widget.py

IngredientWidget for managing individual ingredients in recipes.
"""


# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import QGridLayout, QLineEdit, QSizePolicy, QWidget

from config import (FLOAT, INGREDIENT_CATEGORIES, INGREDIENT_WIDGET,
                    MEASUREMENT_UNITS, NAME, STYLES)
from services.ingredient_service import IngredientService
from style_manager import WidgetLoader
from ui.components.inputs import SmartComboBox
from ui.iconkit import ToolButtonIcon
from ui.tools import clear_error_styles, dynamic_validation

# ── Constants ───────────────────────────────────────────────────────────────────
FIXED_HEIGHT = 32  # Fixed height for input fields in the ingredient widget

# ── Class Definition ────────────────────────────────────────────────────────────
class IngredientWidget(QWidget):
    add_ingredient_requested = Signal(QWidget)
    remove_ingredient_requested = Signal(QWidget)
    ingredient_validated = Signal(dict)

    def __init__(self, removable=True, parent=None):
        """
        Initializes the IngredientWidget with a grid layout and sets up UI components.

        Args:
            removable (bool): If True, the widget will have a remove button.
            parent (QWidget, optional): Parent widget for this ingredient widget.
        """
        super().__init__(parent)
        # ── Initialize Widget ──
        self.setObjectName("IngredientWidget")
        #WidgetLoader.apply_widget_style(self, STYLES["INGREDIENT_WIDGET"])
        self._setup_ui()
        self.setup_event_logic()

    def _setup_ui(self):
        self.grid_layout = QGridLayout(self)  # Create and set layout for the QWidget
        self.setLayout(self.grid_layout)

        self.le_quantity = QLineEdit(self)
        self.le_quantity.setPlaceholderText("Qty.")
        self.grid_layout.addWidget(self.le_quantity, 0, 0, 1, 1)

        self.cb_unit = SmartComboBox(
            list = MEASUREMENT_UNITS, 
            placeholder = "Unit"
        )
        self.grid_layout.addWidget(self.cb_unit, 0, 1, 1, 1)

        self.le_ingredient_name = QLineEdit(self)
        self.le_ingredient_name.setPlaceholderText("Ingredient Name")
        self.grid_layout.addWidget(self.le_ingredient_name, 0, 2, 1, 1)

        self.cb_ingredient_category = SmartComboBox(
            list = INGREDIENT_CATEGORIES, 
            placeholder = "Category"
        )
        self.grid_layout.addWidget(self.cb_ingredient_category, 0, 3, 1, 1)

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
        self.btn_ico_add.clicked.connect(self.emit_ingredient_data)
        self.btn_ico_subtract.clicked.connect(self.request_removal)
        self.ingredient_validated.connect(self.add_ingredient)

        dynamic_validation(self.le_quantity, FLOAT)
        dynamic_validation(self.le_ingredient_name, NAME)

        self.cb_unit.selection_validated.connect(lambda: clear_error_styles(self.cb_unit))
        self.cb_ingredient_category.selection_validated.connect(lambda: clear_error_styles(self.cb_ingredient_category))

    def emit_ingredient_data(self):
        payload = IngredientService.build_payload_from_widget(self)
        self.ingredient_validated.emit(payload)

    def add_ingredient(self):
        self.add_ingredient_requested.emit(self)

    def request_removal(self):
        if self.parent() and len(self.parent().findChildren(IngredientWidget)) > 1:
            self.remove_ingredient_requested.emit(self)

