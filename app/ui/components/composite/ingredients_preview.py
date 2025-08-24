"""app/ui/components/composite/ingredients_preview.py

A simple ingredients preview component with a scrollable 2-column layout.
"""

from typing import Iterable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QVBoxLayout,
    QWidget, QScrollArea)

from app.style import Theme, Qss


class IngredientsPreview(QWidget):
    """Simple scrollable ingredients preview with 2-column layout."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("IngredientsPreview")
        # register for component-specific styling
        Theme.register_widget(self, Qss.MEAL_PLANNER)
        self.ingredient_details = []

        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)

        # Header
        header_label = QLabel("Ingredients")
        header_label.setObjectName("IngredientsHeader")
        self.layout.addWidget(header_label)

        # Scroll area for ingredients
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setObjectName("IngredientsScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setFrameShape(QFrame.NoFrame)

        # Content widget inside scroll area - use horizontal layout with two columns
        self.content_widget = QWidget()
        main_content_layout = QHBoxLayout(self.content_widget)
        main_content_layout.setContentsMargins(8, 8, 8, 8)
        main_content_layout.setSpacing(12)

        # Create two columns
        self.left_column = QVBoxLayout()
        self.right_column = QVBoxLayout()

        self.left_column.setSpacing(6)
        self.right_column.setSpacing(6)
        self.left_column.setAlignment(Qt.AlignTop)
        self.right_column.setAlignment(Qt.AlignTop)

        # Add columns to main layout
        main_content_layout.addLayout(self.left_column, 1)
        main_content_layout.addLayout(self.right_column, 1)

        # Set scroll area content
        self.scroll_area.setWidget(self.content_widget)
        self.layout.addWidget(self.scroll_area)

        # Configure 2-column layout
        self.columns = 2

    def setIngredients(self, ingredient_details: Iterable):
        """Set the ingredients to display."""
        self.ingredient_details = list(ingredient_details)

        # Clear existing content
        self._clearContent()

        # Add ingredients alternating between left and right columns
        for i, detail in enumerate(self.ingredient_details):
            ingredient_widget = self._createIngredientWidget(detail)

            if i % 2 == 0:
                self.left_column.addWidget(ingredient_widget)
            else:
                self.right_column.addWidget(ingredient_widget)

    def _clearContent(self):
        """Clear all content from both columns."""
        # Clear left column
        while self.left_column.count():
            child = self.left_column.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Clear right column
        while self.right_column.count():
            child = self.right_column.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _createIngredientWidget(self, detail):
        """Create a widget for a single ingredient."""
        item_widget = QWidget()
        item_widget.setObjectName("IngredientItem")
        item_widget.setFixedHeight(42)  # Fixed height for consistent spacing

        item_layout = QGridLayout(item_widget)
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setHorizontalSpacing(6)
        item_layout.setVerticalSpacing(0)

        # Set column stretch
        item_layout.setColumnStretch(0, 0)  # Quantity
        item_layout.setColumnStretch(1, 0)  # Unit
        item_layout.setColumnStretch(2, 1)  # Name

        # Get ingredient details
        formatted_qty = getattr(detail, 'formatted_quantity', '')
        abbreviated_unit = getattr(detail, 'abbreviated_unit', '')
        ingredient_name = getattr(detail, "ingredient_name", "") or ""

        # Create labels
        qty_label = QLabel(formatted_qty)
        qty_label.setObjectName("IngredientQuantity")
        qty_label.setMinimumWidth(40)
        qty_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        unit_label = QLabel(abbreviated_unit)
        unit_label.setObjectName("IngredientUnit")
        unit_label.setMinimumWidth(35)
        unit_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        name_label = QLabel(ingredient_name)
        name_label.setObjectName("IngredientName")
        name_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Add to grid
        item_layout.addWidget(qty_label, 0, 0)
        item_layout.addWidget(unit_label, 0, 1)
        item_layout.addWidget(name_label, 0, 2)

        return item_widget
