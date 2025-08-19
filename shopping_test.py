"""
Standalone demo for collapsible category widgets.

This demo creates a complete working example that doesn't depend on your app's
infrastructure. Run this file directly to test the collapsible functionality.

Requirements: PySide6 (pip install PySide6)
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QCheckBox, QFrame, QPushButton, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Signal
from PySide6.QtGui import QFont

from app.style.theme_controller import Theme, Mode
from app.style.effects.effects import Effects
from app.ui.components.layout.card import BaseCard
from app.ui.views.shopping_list import CollapsibleCategory

class ShoppingListDemo(QMainWindow):
    """Main demo window for testing collapsible categories."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Collapsible Categories Demo")
        self.setGeometry(100, 100, 500, 700)

        # Dark theme for the whole window
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QPushButton {
                background-color: #404040;
                border: 1px solid #606060;
                border-radius: 4px;
                color: #ffffff;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #606060;
            }
            QScrollArea {
                border: none;
                background-color: #1e1e1e;
            }
            QLabel {
                color: #ffffff;
            }
        """)

        self._setup_ui()
        self._create_demo_data()
        self._connect_signals()

    def _setup_ui(self):
        """Setup the main UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Title
        title = QLabel("Auto-Generated Ingredients")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        """)
        main_layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("From your meal plan this week.")
        subtitle.setStyleSheet("""
            font-size: 14px;
            color: #b0b0b0;
            margin-bottom: 20px;
        """)
        main_layout.addWidget(subtitle)

        # Control buttons
        controls_widget = QWidget()
        controls_layout = QHBoxLayout(controls_widget)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(10)

        self.expand_all_btn = QPushButton("Expand All")
        self.collapse_all_btn = QPushButton("Collapse All")
        self.check_all_btn = QPushButton("Check All")
        self.uncheck_all_btn = QPushButton("Uncheck All")

        controls_layout.addWidget(self.expand_all_btn)
        controls_layout.addWidget(self.collapse_all_btn)
        controls_layout.addWidget(self.check_all_btn)
        controls_layout.addWidget(self.uncheck_all_btn)
        controls_layout.addStretch()

        main_layout.addWidget(controls_widget)

        # Scrollable area for categories
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        #scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        #scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarNever)

        self.scroll_content = QWidget()
        self.categories_layout = QVBoxLayout(self.scroll_content)
        self.categories_layout.setContentsMargins(0, 0, 0, 0)
        self.categories_layout.setSpacing(12)

        scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(scroll_area)

        # Status area
        self.status_label = QLabel("Ready - Click categories to expand/collapse")
        self.status_label.setStyleSheet("""
            padding: 8px;
            background-color: #2b2b2b;
            border: 1px solid #404040;
            border-radius: 4px;
            font-size: 12px;
        """)
        main_layout.addWidget(self.status_label)

        self._categories = []

    def _create_demo_data(self):
        """Create demo categories and items."""
        # Sample data matching your screenshots
        categories_data = {
            "Produce": ["Avocado", "Garlic", "Lemon"],
            "Dairy": ["Large eggs", "Pecorino cheese"],
            "Meat": ["Ground beef", "Chicken breast", "Salmon fillet"],
            "Pantry": ["Olive oil", "Sea salt", "Black pepper", "Pasta"]
        }

        for category_name, items in categories_data.items():
            category = CollapsibleCategory(category_name, start_expanded=False)

            for item in items:
                category.add_item(item)

            self._categories.append(category)
            self.categories_layout.addWidget(category)

        # Add some spacing at the bottom
        self.categories_layout.addStretch()

    def _connect_signals(self):
        """Connect all the signals."""
        # Control button signals
        self.expand_all_btn.clicked.connect(self.expand_all)
        self.collapse_all_btn.clicked.connect(self.collapse_all)
        self.check_all_btn.clicked.connect(self.check_all)
        self.uncheck_all_btn.clicked.connect(self.uncheck_all)

        # Category signals
        for category in self._categories:
            category.toggled.connect(self.on_category_toggled)
            category.itemChecked.connect(self.on_item_checked)

    def expand_all(self):
        """Expand all categories."""
        for category in self._categories:
            category.expand()
        self.status_label.setText("All categories expanded")

    def collapse_all(self):
        """Collapse all categories."""
        for category in self._categories:
            category.collapse()
        self.status_label.setText("All categories collapsed")

    def check_all(self):
        """Check all items."""
        total_items = 0
        for category in self._categories:
            category.set_all_items_checked(True)
            total_items += len(category._items)
        self.status_label.setText(f"All {total_items} items checked")

    def uncheck_all(self):
        """Uncheck all items."""
        total_items = 0
        for category in self._categories:
            category.set_all_items_checked(False)
            total_items += len(category._items)
        self.status_label.setText(f"All {total_items} items unchecked")

    def on_category_toggled(self, is_expanded):
        """Handle category toggle."""
        # Find which category was toggled
        sender = self.sender()
        if sender:
            action = "expanded" if is_expanded else "collapsed"
            self.status_label.setText(f"Category '{sender.category_name}' {action}")

    def on_item_checked(self, item_name, is_checked):
        """Handle item check/uncheck."""
        action = "checked" if is_checked else "unchecked"
        self.status_label.setText(f"Item '{item_name}' {action}")

        # Show summary of checked items
        self.show_checked_summary()

    def show_checked_summary(self):
        """Show summary of checked items in window title."""
        total_checked = 0
        for category in self._categories:
            total_checked += len(category.get_checked_items())

        self.setWindowTitle(f"Collapsible Categories Demo - {total_checked} items checked")

def main():
    """Run the demo application."""
    app = QApplication(sys.argv)

    # Set application style
    Theme.setCustomColorMap("material-theme.json", Mode.DARK)

    # Create and show the demo window
    demo = ShoppingListDemo()
    demo.show()

    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
