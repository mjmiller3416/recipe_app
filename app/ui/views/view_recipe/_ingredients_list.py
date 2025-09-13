"""app/ui/views/view_recipe/ingredients_list.py

A reusable component for displaying a list of recipe ingredients with amounts and names.
"""

# ── Imports ──
from typing import Iterable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.ui.utils import apply_object_name_pattern, create_form_grid_layout


class IngredientList(QWidget):
    """A list widget for displaying recipe ingredients with amounts and names."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("IngredientList")

        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(12)

    def setIngredients(self, ingredient_details: Iterable):
        """Set the ingredients to display."""
        # Clear existing ingredients
        self._clearIngredients()

        # Add new ingredients
        for detail in ingredient_details:
            self._addIngredientItem(detail)

    def _clearIngredients(self):
        """Clear all ingredient items from the layout."""
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _addIngredientItem(self, detail):
        """Add a single ingredient item to the list."""
        # Create ingredient row widget with utility
        item_widget = QWidget()
        apply_object_name_pattern(item_widget, "Ingredient", "Item")

        # Create standardized grid layout
        item_layout = create_form_grid_layout(
            item_widget, margins=(0, 0, 0, 0), spacing=10
        )
        item_layout.setVerticalSpacing(0)

        # Set column stretch: quantity (fixed), unit (fixed), name (expanding)
        item_layout.setColumnStretch(0, 0)  # Quantity column - fixed width
        item_layout.setColumnStretch(1, 0)  # Unit column - fixed width
        item_layout.setColumnStretch(2, 1)  # Name column - expanding

        # Get formatted ingredient details using new DTO properties
        formatted_qty = getattr(detail, 'formatted_quantity', '')
        abbreviated_unit = getattr(detail, 'abbreviated_unit', '')
        ingredient_name = getattr(detail, "ingredient_name", "") or ""

        # Create labels with consistent patterns
        qty_label = self._create_ingredient_label(
            formatted_qty, "Ingredient", "Quantity",
            Qt.AlignRight | Qt.AlignVCenter, fixed_width=60
        )
        unit_label = self._create_ingredient_label(
            abbreviated_unit, "Ingredient", "Unit",
            Qt.AlignLeft | Qt.AlignVCenter, fixed_width=50
        )
        name_label = self._create_ingredient_label(
            ingredient_name, "Ingredient", "Name",
            Qt.AlignLeft | Qt.AlignVCenter
        )

        # Add to grid: row 0, columns 0, 1, 2
        item_layout.addWidget(qty_label, 0, 0)
        item_layout.addWidget(unit_label, 0, 1)
        item_layout.addWidget(name_label, 0, 2)

        # Add to main layout
        self.layout.addWidget(item_widget)

    def _create_ingredient_label(self, text: str, context: str, label_type: str,
                               alignment: Qt.AlignmentFlag, fixed_width: int = None) -> QLabel:
        """Create a standardized ingredient label with consistent styling."""
        label = QLabel(text)
        apply_object_name_pattern(label, context, label_type)
        label.setAlignment(alignment)
        if fixed_width:
            label.setFixedWidth(fixed_width)
        return label
