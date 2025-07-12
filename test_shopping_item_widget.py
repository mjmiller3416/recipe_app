"""test_shopping_item_widget.py

Test application for the ShoppingItemWidget with mock data.
Creates a test window with multiple shopping items displayed as they would be in the actual app.
"""

import sys
from typing import Dict, List, Tuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QScrollArea, QVBoxLayout, QWidget,
    QLabel, QPushButton, QHBoxLayout, QFrame
)

# Import the widget we're testing
from app.ui.components.composite.shopping_item import ShoppingItemWidget


# ── Mock Data Classes ────────────────────────────────────────────────────────────────────────
class MockShoppingItem:
    """Mock shopping item that mimics the real ShoppingItem model structure."""

    def __init__(self, id: int, ingredient_name: str, quantity: float, unit: str = None,
                 category: str = None, source: str = "manual", have: bool = False, state_key: str = None):
        self.id = id
        self.ingredient_name = ingredient_name
        self.quantity = quantity
        self.unit = unit
        self.category = category
        self.source = source
        self.have = have
        self.state_key = state_key

    def formatted_quantity(self) -> str:
        """Return formatted quantity string."""
        if self.quantity == int(self.quantity):
            return str(int(self.quantity))
        return f"{self.quantity:.2f}".rstrip('0').rstrip('.')

    def key(self) -> str:
        """Generate a unique key for this shopping item."""
        if self.state_key:
            return self.state_key
        unit_str = self.unit or ""
        return f"{self.ingredient_name.lower().strip()}::{unit_str.lower().strip()}"


class MockShoppingService:
    """Mock shopping service for testing."""

    def __init__(self):
        self.items = {}

    def toggle_item_status(self, item_id: int):
        """Toggle the status of a shopping item."""
        if item_id in self.items:
            self.items[item_id].have = not self.items[item_id].have
            print(f"Toggled item {item_id}: {self.items[item_id].ingredient_name} -> {'✓' if self.items[item_id].have else '○'}")

    def add_item(self, item: MockShoppingItem):
        """Add an item to the service for tracking."""
        self.items[item.id] = item


# ── Test Data Factory ─────────────────────────────────────────────────────────────────────────
def create_mock_shopping_items() -> List[MockShoppingItem]:
    """Create a variety of mock shopping items for testing."""
    items = [
        # Recipe items (checked and unchecked)
        MockShoppingItem(1, "All-purpose Flour", 2.5, "cups", "Baking", "recipe", False),
        MockShoppingItem(2, "Large Eggs", 6.0, "pieces", "Dairy", "recipe", True),
        MockShoppingItem(3, "Whole Milk", 1.0, "cup", "Dairy", "recipe", False),
        MockShoppingItem(4, "Unsalted Butter", 0.5, "cup", "Dairy", "recipe", True),
        MockShoppingItem(5, "Granulated Sugar", 1.25, "cups", "Baking", "recipe", False),
        MockShoppingItem(6, "Vanilla Extract", 2.0, "tsp", "Baking", "recipe", False),
        MockShoppingItem(7, "Baking Powder", 2.0, "tsp", "Baking", "recipe", True),

        # Manual items
        MockShoppingItem(8, "Bananas", 6.0, "pieces", "Produce", "manual", False),
        MockShoppingItem(9, "Greek Yogurt", 1.0, "container", "Dairy", "manual", True),
        MockShoppingItem(10, "Olive Oil", 1.0, "bottle", "Oils", "manual", False),

        # Items without units
        MockShoppingItem(11, "Salt", 1.0, None, "Spices", "recipe", False),
        MockShoppingItem(12, "Black Pepper", 1.0, None, "Spices", "manual", True),

        # Items with decimal quantities
        MockShoppingItem(13, "Heavy Cream", 1.33, "cups", "Dairy", "recipe", False),
        MockShoppingItem(14, "Lemon Juice", 0.25, "cup", "Produce", "recipe", False),

        # Items with long names
        MockShoppingItem(15, "Extra Virgin Olive Oil (Cold Pressed)", 2.0, "tbsp", "Oils", "recipe", False),
        MockShoppingItem(16, "Organic Free-Range Chicken Breast", 1.5, "lbs", "Meat", "manual", True),

        # Items with various units
        MockShoppingItem(17, "Ground Cinnamon", 1.0, "tsp", "Spices", "recipe", False),
        MockShoppingItem(18, "Brown Sugar", 0.75, "cups", "Baking", "recipe", True),  # Fixed: "cups" to match breakdown_map
        MockShoppingItem(19, "Garlic Cloves", 4.0, "cloves", "Produce", "recipe", False),
        MockShoppingItem(20, "Fresh Basil", 0.5, "cup", "Herbs", "manual", False),
    ]
    return items


def create_mock_breakdown_map() -> Dict[str, List[Tuple[str, float, str]]]:
    """Create mock breakdown mapping for recipe tooltips."""
    return {
        "all-purpose flour::cups": [
            ("Chocolate Chip Cookies", 2.0, "cups"),
            ("Pancakes", 0.5, "cups")
        ],
        "large eggs::pieces": [
            ("Chocolate Chip Cookies", 2.0, "pieces"),
            ("Pancakes", 2.0, "pieces"),
            ("Scrambled Eggs", 2.0, "pieces")
        ],
        "whole milk::cup": [
            ("Pancakes", 1.0, "cup")
        ],
        "unsalted butter::cup": [  # Added for item ID 4
            ("Chocolate Chip Cookies", 0.5, "cup")
        ],
        "granulated sugar::cups": [
            ("Chocolate Chip Cookies", 1.0, "cups"),
            ("Sweet Tea", 0.25, "cups")
        ],
        "vanilla extract::tsp": [
            ("Chocolate Chip Cookies", 1.0, "tsp"),
            ("Vanilla Cake", 1.0, "tsp")
        ],
        "baking powder::tsp": [  # Added for item ID 7
            ("Pancakes", 2.0, "tsp")
        ],
        "heavy cream::cups": [
            ("Alfredo Sauce", 1.0, "cups"),
            ("Whipped Cream", 0.33, "cups")
        ],
        "ground cinnamon::tsp": [
            ("Cinnamon Rolls", 1.0, "tsp")
        ],
        "brown sugar::cups": [  # Fixed: changed from "cup" to "cups"
            ("Chocolate Chip Cookies", 0.5, "cups"),
            ("Brown Sugar Cookies", 0.25, "cups")
        ],
        "garlic cloves::cloves": [
            ("Garlic Bread", 2.0, "cloves"),
            ("Pasta Aglio e Olio", 2.0, "cloves")
        ]
    }


# ── Test Window ───────────────────────────────────────────────────────────────────────────────
class ShoppingItemTestWindow(QMainWindow):
    """Test window for displaying multiple ShoppingItemWidget instances."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ShoppingItemWidget Test App")
        self.setGeometry(100, 100, 600, 800)

        # Create mock data
        self.shopping_items = create_mock_shopping_items()
        self.breakdown_map = create_mock_breakdown_map()
        self.shopping_service = MockShoppingService()

        # Add items to service for tracking
        for item in self.shopping_items:
            self.shopping_service.add_item(item)

        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Title
        title_label = QLabel("ShoppingItemWidget Test App")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Statistics
        stats_layout = QHBoxLayout()
        total_items = len(self.shopping_items)
        checked_items = sum(1 for item in self.shopping_items if item.have)
        recipe_items = sum(1 for item in self.shopping_items if item.source == "recipe")
        manual_items = sum(1 for item in self.shopping_items if item.source == "manual")

        stats_label = QLabel(f"Total: {total_items} | Checked: {checked_items} | Recipe: {recipe_items} | Manual: {manual_items}")
        stats_label.setStyleSheet("color: #666; margin: 5px;")
        stats_layout.addWidget(stats_label)

        # Refresh button
        refresh_btn = QPushButton("Refresh Stats")
        refresh_btn.clicked.connect(self.refresh_stats)
        refresh_btn.setMaximumWidth(100)
        stats_layout.addWidget(refresh_btn)

        main_layout.addLayout(stats_layout)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)

        # Scroll area for shopping items
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Container for shopping items
        scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_widget)
        self.scroll_layout.setAlignment(Qt.AlignTop)

        # Group items by category for better visualization
        self.create_shopping_list()

        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)

    def create_shopping_list(self):
        """Create the shopping list with categorized items."""
        # Group items by category
        categories = {}
        uncategorized = []

        for item in self.shopping_items:
            if item.category:
                if item.category not in categories:
                    categories[item.category] = []
                categories[item.category].append(item)
            else:
                uncategorized.append(item)

        # Add categorized items
        for category, items in sorted(categories.items()):
            self.add_category_section(category, items)

        # Add uncategorized items
        if uncategorized:
            self.add_category_section("Uncategorized", uncategorized)

    def add_category_section(self, category_name: str, items: List[MockShoppingItem]):
        """Add a category section with its items."""
        # Category header
        category_label = QLabel(f"📁 {category_name}")
        category_label.setStyleSheet("""
            font-weight: bold;
            font-size: 14px;
            color: #2c3e50;
            margin: 10px 0 5px 0;
            padding: 5px;
            background-color: #ecf0f1;
            border-radius: 3px;
        """)
        self.scroll_layout.addWidget(category_label)

        # Sort items: unchecked first, then checked
        sorted_items = sorted(items, key=lambda x: (x.have, x.ingredient_name.lower()))

        # Add shopping item widgets
        for item in sorted_items:
            widget = ShoppingItemWidget(
                item=item,
                shopping_svc=self.shopping_service,
                breakdown_map=self.breakdown_map,
                parent=self
            )

            # Add some styling to make it look nice
            widget.setStyleSheet("""
                ShoppingItemWidget {
                    padding: 5px;
                    margin: 2px 0;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    background-color: white;
                }
                ShoppingItemWidget:hover {
                    background-color: #f8f9fa;
                    border-color: #adb5bd;
                }
            """)

            self.scroll_layout.addWidget(widget)

    def refresh_stats(self):
        """Refresh the statistics display."""
        # Find the stats label and update it
        total_items = len(self.shopping_items)
        checked_items = sum(1 for item in self.shopping_items if item.have)
        recipe_items = sum(1 for item in self.shopping_items if item.source == "recipe")
        manual_items = sum(1 for item in self.shopping_items if item.source == "manual")

        # This is a simple refresh - in a real app you might want to rebuild the entire list
        print(f"Current stats - Total: {total_items}, Checked: {checked_items}, Recipe: {recipe_items}, Manual: {manual_items}")


# ── Main Function ─────────────────────────────────────────────────────────────────────────────
def main():
    """Main function to run the test application."""
    app = QApplication(sys.argv)

    # Set application style
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f5f5f5;
        }
        QScrollArea {
            border: none;
            background-color: transparent;
        }
        QCheckBox {
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
        }
        QCheckBox::indicator:unchecked {
            border: 2px solid #ccc;
            background-color: white;
            border-radius: 3px;
        }
        QCheckBox::indicator:checked {
            border: 2px solid #27ae60;
            background-color: #27ae60;
            border-radius: 3px;
        }
        QCheckBox::indicator:checked::before {
            content: "✓";
            color: white;
            font-weight: bold;
        }
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        QPushButton:pressed {
            background-color: #21618c;
        }
    """)

    # Create and show the test window
    window = ShoppingItemTestWindow()
    window.show()

    print("ShoppingItemWidget Test App Started!")
    print("Features demonstrated:")
    print("- ✅ Multiple shopping items with various data")
    print("- ✅ Recipe items vs Manual items")
    print("- ✅ Items with and without units")
    print("- ✅ Checked and unchecked states")
    print("- ✅ Category grouping")
    print("- ✅ Tooltips for recipe items (hover over recipe items)")
    print("- ✅ Interactive checkboxes that toggle states")
    print("- ✅ Responsive styling and layout")
    print("\nClick on checkboxes to toggle item status!")

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
