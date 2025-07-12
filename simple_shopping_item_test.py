"""simple_shopping_item_test.py

A simpler test application for the ShoppingItemWidget.
This version focuses on the core functionality without complex styling.
"""

import sys
from typing import Dict, List, Tuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QScrollArea, QVBoxLayout, QWidget,
    QLabel, QHBoxLayout, QGroupBox
)

# Import the widget we're testing
from app.ui.components.composite.shopping_item import ShoppingItemWidget


# ── Mock Shopping Item ───────────────────────────────────────────────────────────────────────
class MockShoppingItem:
    """Simplified mock shopping item."""

    def __init__(self, id: int, ingredient_name: str, quantity: float,
                 unit: str = None, category: str = None, source: str = "manual", have: bool = False):
        self.id = id
        self.ingredient_name = ingredient_name
        self.quantity = quantity
        self.unit = unit
        self.category = category
        self.source = source
        self.have = have
        self.state_key = f"{ingredient_name.lower()}::{unit or ''}"

    def formatted_quantity(self) -> str:
        """Format quantity as string."""
        if self.quantity == int(self.quantity):
            return str(int(self.quantity))
        return f"{self.quantity:.1f}"

    def key(self) -> str:
        """Generate item key."""
        return self.state_key


# ── Mock Shopping Service ─────────────────────────────────────────────────────────────────────
class MockShoppingService:
    """Simple mock shopping service."""

    def __init__(self):
        self.items = {}

    def toggle_item_status(self, item_id: int):
        """Toggle item status."""
        if item_id in self.items:
            item = self.items[item_id]
            item.have = not item.have
            status = "✓ Completed" if item.have else "○ Pending"
            print(f"Item {item_id} ({item.ingredient_name}): {status}")

    def add_item(self, item: MockShoppingItem):
        """Add item to service."""
        self.items[item.id] = item


# ── Test Window ───────────────────────────────────────────────────────────────────────────────
class SimpleShoppingItemTest(QMainWindow):
    """Simple test window for ShoppingItemWidget."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple ShoppingItemWidget Test")
        self.setGeometry(100, 100, 500, 600)

        # Create test data
        self.setup_test_data()
        self.setup_ui()

    def setup_test_data(self):
        """Create test shopping items."""
        self.shopping_service = MockShoppingService()

        # Create various types of shopping items
        self.items = [
            MockShoppingItem(1, "Milk", 1.0, "gallon", "Dairy", "manual", False),
            MockShoppingItem(2, "Eggs", 12.0, "pieces", "Dairy", "manual", True),
            MockShoppingItem(3, "Flour", 2.5, "cups", "Baking", "recipe", False),
            MockShoppingItem(4, "Sugar", 1.0, "cup", "Baking", "recipe", False),
            MockShoppingItem(5, "Butter", 0.5, "cup", "Dairy", "recipe", True),
            MockShoppingItem(6, "Salt", 1.0, "tsp", "Spices", "recipe", False),
            MockShoppingItem(7, "Bananas", 6.0, "pieces", "Produce", "manual", False),
            MockShoppingItem(8, "Olive Oil", 2.0, "tbsp", "Oils", "recipe", False),
            MockShoppingItem(9, "Garlic", 3.0, "cloves", "Produce", "recipe", True),
            MockShoppingItem(10, "Tomatoes", 4.0, "pieces", "Produce", "manual", False),
        ]

        # Add items to service
        for item in self.items:
            self.shopping_service.add_item(item)

        # Create mock breakdown map for recipe tooltips
        self.breakdown_map = {
            "flour::cups": [("Bread Recipe", 2.0, "cups"), ("Cookies", 0.5, "cups")],
            "sugar::cup": [("Cookies", 1.0, "cup")],
            "butter::cup": [("Cookies", 0.5, "cup")],
            "salt::tsp": [("Bread Recipe", 1.0, "tsp")],
            "olive oil::tbsp": [("Pasta", 2.0, "tbsp")],
            "garlic::cloves": [("Pasta", 3.0, "cloves")],
        }

    def setup_ui(self):
        """Set up the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Title
        title = QLabel("ShoppingItemWidget Test")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        main_layout.addWidget(title)

        # Info
        info = QLabel("Click checkboxes to toggle items. Recipe items show tooltips on hover.")
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet("color: #666; margin-bottom: 10px;")
        main_layout.addWidget(info)

        # Scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Group items by source
        recipe_items = [item for item in self.items if item.source == "recipe"]
        manual_items = [item for item in self.items if item.source == "manual"]

        # Recipe items section
        if recipe_items:
            recipe_group = QGroupBox("Recipe Items")
            recipe_layout = QVBoxLayout(recipe_group)

            for item in recipe_items:
                widget = ShoppingItemWidget(
                    item=item,
                    shopping_svc=self.shopping_service,
                    breakdown_map=self.breakdown_map
                )
                recipe_layout.addWidget(widget)

            scroll_layout.addWidget(recipe_group)

        # Manual items section
        if manual_items:
            manual_group = QGroupBox("Manual Items")
            manual_layout = QVBoxLayout(manual_group)

            for item in manual_items:
                widget = ShoppingItemWidget(
                    item=item,
                    shopping_svc=self.shopping_service,
                    breakdown_map=self.breakdown_map
                )
                manual_layout.addWidget(widget)

            scroll_layout.addWidget(manual_group)

        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)

        # Status info
        status_layout = QHBoxLayout()
        total_items = len(self.items)
        checked_items = sum(1 for item in self.items if item.have)
        recipe_count = len(recipe_items)
        manual_count = len(manual_items)

        status_label = QLabel(f"Total: {total_items} | Checked: {checked_items} | Recipe: {recipe_count} | Manual: {manual_count}")
        status_label.setStyleSheet("color: #555; padding: 5px;")
        status_layout.addWidget(status_label)

        main_layout.addLayout(status_layout)


# ── Main Function ─────────────────────────────────────────────────────────────────────────────
def main():
    """Run the simple test application."""
    app = QApplication(sys.argv)

    # Basic styling
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f8f9fa;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #cccccc;
            border-radius: 5px;
            margin: 5px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        QCheckBox {
            spacing: 5px;
        }
        QLabel {
            padding: 2px;
        }
    """)

    window = SimpleShoppingItemTest()
    window.show()

    print("Simple ShoppingItemWidget Test Started!")
    print("- Recipe items have tooltips (hover to see)")
    print("- Manual items don't have tooltips")
    print("- Click checkboxes to toggle states")
    print("- Watch the console for toggle messages")

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
