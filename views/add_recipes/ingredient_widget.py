import sys

from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import QApplication, QGridLayout, QLineEdit, QWidget

from config import (FLOAT, INGREDIENT_CATEGORIES, INGREDIENT_WIDGET,
                    MEASUREMENT_UNITS, NAME)
from ui.components.inputs import SmartComboBox
from ui.iconkit import ToolButtonIcon
from ui.tools import clear_error_styles, dynamic_validation, populate_combobox
from ui.tools.form_utilities import populate_combobox
from services.ingredient_service import IngredientService


class IngredientWidget(QWidget):
    add_ingredient_requested = Signal(QWidget)
    remove_ingredient_requested = Signal(QWidget)
    ingredient_validated = Signal(dict)

    def __init__(self, removable=True, parent=None):
        super().__init__(parent)
        self.setObjectName("IngredientWidget")
        self._setup_ui()
        self.populate_comboboxes()
        self.setup_event_logic()

    def _setup_ui(self):
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)

        self.le_quantity = QLineEdit(self)
        self.le_quantity.setMaximumSize(QSize(35, 16777215))
        self.le_quantity.setPlaceholderText("Qty.")
        self.gridLayout.addWidget(self.le_quantity, 0, 0, 1, 1)

        self.cb_unit = SmartComboBox(self)
        self.cb_unit.setPlaceholderText("Unit")
        self.gridLayout.addWidget(self.cb_unit, 0, 1, 1, 1)

        self.le_ingredient_name = QLineEdit(self)
        self.le_ingredient_name.setPlaceholderText("Ingredient Name")
        self.gridLayout.addWidget(self.le_ingredient_name, 0, 2, 1, 1)

        self.cb_ingredient_category = SmartComboBox(self)
        self.cb_ingredient_category.setPlaceholderText("Category")
        self.gridLayout.addWidget(self.cb_ingredient_category, 0, 3, 1, 1)

        self.btn_ico_subtract = ToolButtonIcon(
            file_path=INGREDIENT_WIDGET["ICON_SUBTRACT"],
            size=INGREDIENT_WIDGET["ICON_SIZE"],
            variant=INGREDIENT_WIDGET["DYNAMIC"]
        )
        self.gridLayout.addWidget(self.btn_ico_subtract, 0, 4, 1, 1)

        self.btn_ico_add = ToolButtonIcon(
            file_path=INGREDIENT_WIDGET["ICON_ADD"],
            size=INGREDIENT_WIDGET["ICON_SIZE"],
            variant=INGREDIENT_WIDGET["DYNAMIC"]
        )
        self.gridLayout.addWidget(self.btn_ico_add, 0, 5, 1, 1)

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

    def populate_comboboxes(self):
        populate_combobox(self.cb_ingredient_category, INGREDIENT_CATEGORIES)
        populate_combobox(self.cb_unit, MEASUREMENT_UNITS)

if __name__ == "__main__":   
    app = QApplication(sys.argv)
    test_widget = IngredientWidget()
    test_widget.show()
    sys.exit(app.exec())
