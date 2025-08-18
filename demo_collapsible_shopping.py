"""Demo app for testing CollapsibleCard with shopping list items.

This demo simulates the primary use case of collapsible cards as ingredient
category containers in the Shopping List view, with shopping items grouped
by their respective categories.
"""

import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QScrollArea, QLabel
from PySide6.QtCore import Qt

from app.style.theme_controller import Theme, Mode
# Mock shopping item data for testing
MOCK_SHOPPING_DATA = {
    "Produce": [
        {"name": "Tomatoes", "quantity": "3", "unit": "large", "have": False},
        {"name": "Onions", "quantity": "2", "unit": "medium", "have": True},
        {"name": "Bell Peppers", "quantity": "1", "unit": "red", "have": False},
        {"name": "Garlic", "quantity": "4", "unit": "cloves", "have": False},
    ],
    "Dairy & Eggs": [
        {"name": "Eggs", "quantity": "1", "unit": "dozen", "have": True},
        {"name": "Milk", "quantity": "1", "unit": "gallon", "have": False},
        {"name": "Cheddar Cheese", "quantity": "8", "unit": "oz", "have": False},
    ],
    "Pantry": [
        {"name": "Olive Oil", "quantity": "1", "unit": "bottle", "have": True},
        {"name": "Salt", "quantity": "1", "unit": "container", "have": True},
        {"name": "Black Pepper", "quantity": "1", "unit": "container", "have": False},
        {"name": "Pasta", "quantity": "1", "unit": "lb", "have": False},
    ],
    "Meat & Seafood": [
        {"name": "Ground Beef", "quantity": "1", "unit": "lb", "have": False},
        {"name": "Chicken Breast", "quantity": "2", "unit": "lbs", "have": False},
    ]
}


class MockShoppingItemWidget(QWidget):
    """Mock shopping item widget for demo purposes."""

    def __init__(self, item_data, parent=None):
        super().__init__(parent)
        self.item_data = item_data
        self.setup_ui()

    def setup_ui(self):
        from PySide6.QtWidgets import QCheckBox, QHBoxLayout

        layout = QHBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)

        # Checkbox
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(self.item_data["have"])

        # Item label
        unit_display = f" {self.item_data['unit']}" if self.item_data['unit'] else ""
        item_text = f"{self.item_data['name']}: {self.item_data['quantity']}{unit_display}"

        self.label = QLabel(item_text)
        if self.item_data["have"]:
            self.label.setText(f"<s>{item_text}</s>")

        layout.addWidget(self.checkbox)
        layout.addWidget(self.label)
        layout.addStretch()

        self.setLayout(layout)

        # Connect checkbox to update label style
        self.checkbox.stateChanged.connect(self._update_label)

    def _update_label(self, state):
        """Update label style based on checkbox state."""
        unit_display = f" {self.item_data['unit']}" if self.item_data['unit'] else ""
        item_text = f"{self.item_data['name']}: {self.item_data['quantity']}{unit_display}"

        if self.checkbox.isChecked():
            self.label.setText(f"<s>{item_text}</s>")
        else:
            self.label.setText(item_text)


class CollapsibleShoppingDemo(QWidget):
    """Demo application for testing CollapsibleCard with shopping list items."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Collapsible Shopping List Demo")
        self.setGeometry(100, 100, 800, 600)
        self.setup_ui()

    def setup_ui(self):
        """Setup the demo UI with collapsible cards for each category."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(10)

        # Title
        title = QLabel("Shopping List - Collapsible Categories Demo")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title)

        # Instructions
        instructions = QLabel(
            "Click the arrow buttons to collapse/expand each category. "
            "This simulates how ingredient categories would work in the shopping list view."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; margin-bottom: 15px;")
        main_layout.addWidget(instructions)

        # Scrollable area for shopping categories
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setAlignment(Qt.AlignTop)
        scroll_layout.setSpacing(12)

        # Create collapsible cards for each category
        self._create_category_cards(scroll_layout)

        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)

        self.setLayout(main_layout)

    def _create_category_cards(self, parent_layout):
        """Create collapsible cards for each shopping category."""
        from app.ui.components.layout.collapsible_card import CollapsibleCard
        from app.style.icon import Name

        # Define category icons (you can modify these based on available icons)
        category_icons = {
            "Produce": Name.APPLE,
            "Dairy & Eggs": Name.EGG,
            "Pantry": Name.CABINET,
            "Meat & Seafood": Name.FISH
        }

        for category, items in MOCK_SHOPPING_DATA.items():
            # Create collapsible card for this category
            card = CollapsibleCard()
            card.setAnimationDuration(250)  # Slightly faster animation for demo

            # Set header with category name and icon
            icon = category_icons.get(category, Name.FOLDER)
            card.setHeader(f"{category} ({len(items)} items)", icon)

            # Add shopping items to the card
            for item_data in items:
                item_widget = MockShoppingItemWidget(item_data)
                card.addWidget(item_widget)

            # Add some categories collapsed by default to show the functionality
            if category in ["Pantry", "Meat & Seafood"]:
                card.setExpanded(False, animate=False)

            parent_layout.addWidget(card)


def main():
    """Run the collapsible shopping list demo."""
    app = QApplication(sys.argv)

    # Apply basic styling
    Theme.setCustomColorMap("material-theme.json", Mode.DARK)

    demo = CollapsibleShoppingDemo()
    demo.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
