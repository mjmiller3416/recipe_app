"""app/ui/views/shopping_list/_add_item_form.py

This module defines the AddItemForm class, which provides a user interface for adding
new items to the shopping list. It includes fields for item name, quantity, unit, and
category, and is designed to be used within the shopping list view.
"""

# ── Imports ──
from PySide6.QtWidgets import QGridLayout, QLabel, QLineEdit, QWidget

from app.config import INGREDIENT_CATEGORIES, MEASUREMENT_UNITS, AppConfig
from app.ui.components.widgets.combobox import ComboBox
from app.ui.utils import set_fixed_height_for_layout_widgets


class AddItemForm(QWidget):
    """Form for manually adding new items to the shopping list."""
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("AddShoppingItem")

        # Create Layout
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(10, 10, 10, 10)
        self._layout.setSpacing(10)

        # Create labels and inputs for shopping item details - labels above inputs
        # Item Name
        self.lbl_item_name = QLabel("Item Name")
        self.le_item_name = QLineEdit()
        self.le_item_name.setPlaceholderText("e.g. Olive Oil")
        self.le_item_name.setObjectName("ItemNameLineEdit")

        # Qty.
        self.lbl_item_qty = QLabel("Qty.")
        self.le_item_qty = QLineEdit()
        self.le_item_qty.setPlaceholderText("e.g. 2")
        self.le_item_qty.setObjectName("QtyLineEdit")

        # Unit
        self.lbl_item_unit = QLabel("Unit")
        self.cb_item_unit = ComboBox(list_items=MEASUREMENT_UNITS, placeholder="e.g. bottle")
        self.cb_item_unit.setObjectName("ComboBox")
        self.cb_item_unit.setProperty("context", "shopping_item")

        # Category
        self.lbl_item_category = QLabel("Category")
        self.cb_item_category = ComboBox(list_items=INGREDIENT_CATEGORIES, placeholder="Select category")
        self.cb_item_category.setObjectName("ComboBox")
        self.cb_item_category.setProperty("context", "shopping_item")

        # add labels and widgets to the form layout - two column layout with labels above inputs
        # Row 0: Item Name (full width)
        self._layout.addWidget(self.lbl_item_name, 0, 0, 1, 2)
        self._layout.addWidget(self.le_item_name, 1, 0, 1, 2)

        # Row 2-3: Item Quantity (left) and Item Unit (right)
        self._layout.addWidget(self.lbl_item_qty, 2, 0, 1, 1)
        self._layout.addWidget(self.le_item_qty, 3, 0, 1, 1)
        self._layout.addWidget(self.lbl_item_unit, 2, 1, 1, 1)
        self._layout.addWidget(self.cb_item_unit, 3, 1, 1, 1)

        # Row 4-5: Item Category (left) and Item Unit (right)
        self._layout.addWidget(self.lbl_item_category, 4, 0, 1, 2)
        self._layout.addWidget(self.cb_item_category, 5, 0, 1, 2)

        set_fixed_height_for_layout_widgets(
            layout = self._layout,
            height = AppConfig.FIXED_INPUT_HEIGHT,
            skip   = (QLabel,)
        )
