"""app/ui/views/shopping_list/add_item_form.py

Form widget for manually adding new items to the shopping list.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QLineEdit,
    QWidget,
)

from app.config import INGREDIENT_CATEGORIES, MEASUREMENT_UNITS
from app.ui.components.widgets.combobox import ComboBox
from app.ui.constants import LayoutConstants
from app.ui.utils import set_fixed_height_for_layout_widgets

class AddItemForm(QWidget):
    """Form widget for manually adding new items to the shopping list.

    Provides input fields for item name, quantity, unit, and category.
    Used within the AddItem card on the shopping list view.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the add item form.

        Args:
            parent: Optional parent widget for Qt hierarchy.
        """
        super().__init__(parent)
        self.setObjectName("AddShoppingItem")

        # Configure form layout with grid for responsive design
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(10, 10, 10, 10)
        self._layout.setSpacing(10)

        # Create form controls with labels positioned above inputs for clarity
        self.lbl_item_name = QLabel("Item Name")
        self.le_item_name = QLineEdit()
        self.le_item_name.setPlaceholderText("e.g. Olive Oil")
        self.le_item_name.setObjectName("item_name_line_edit")

        # Qty.
        self.lbl_item_qty = QLabel("Qty.")
        self.le_item_qty = QLineEdit()
        self.le_item_qty.setPlaceholderText("e.g. 2")
        self.le_item_qty.setObjectName("quantity_line_edit")

        # Unit
        self.lbl_item_unit = QLabel("Unit")
        self.cb_item_unit = ComboBox(list_items=MEASUREMENT_UNITS, placeholder="e.g. bottle")
        self.cb_item_unit.setObjectName("unit_combo_box")
        self.cb_item_unit.setProperty("context", "shopping_item")

        # Category
        self.lbl_item_category = QLabel("Category")
        self.cb_item_category = ComboBox(list_items=INGREDIENT_CATEGORIES, placeholder="Select category")
        self.cb_item_category.setObjectName("category_combo_box")
        self.cb_item_category.setProperty("context", "shopping_item")

        # Arrange form controls in grid layout for optimal space usage
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
            height = LayoutConstants.FIXED_INPUT_HEIGHT,
            skip   = (QLabel,)
        )
