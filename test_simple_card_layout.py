"""test_simple_card_layout.py

Simple test of the utility-based approach to card layouts.
This should solve the cutoff and indentation issues.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QLabel
)
from PySide6.QtCore import Qt

from app.ui.components.layout.card import Card
from app.ui.components.layout.card_utils import (
    create_card_row, create_card_column, two_column_layout,
    match_card_heights
)


class SimpleCard(Card):
    """Simple card for testing."""
    
    def __init__(self, title: str, content: str = "", color: str = None, button_text: str = None, button_align=None):
        super().__init__()  # Updated constructor - no elevation parameter
        self.setHeader(title)
        
        if content:
            content_label = QLabel(content)
            content_label.setWordWrap(True)
            self.addWidget(content_label)
        
        if button_text:
            from PySide6.QtCore import Qt
            alignment = button_align if button_align else Qt.AlignCenter
            self.addButton(button_text, alignment=alignment)
        
        if color:
            self.setStyleSheet(f"background-color: {color};")


class SimpleCardLayoutTest(QMainWindow):
    """Test the simple utility-based approach."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Card Layout Test")
        self.setGeometry(100, 100, 1000, 600)
        
        # Create main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Main layout
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        self.create_tests(main_layout)
    
    def create_tests(self, layout):
        """Create test layouts."""
        
        # Test 1: Full-width cards (should align perfectly)
        card1 = SimpleCard("Recipe Info", "Basic recipe information", "#e3f2fd")
        card2 = SimpleCard("Ingredients", "List of ingredients", "#f3e5f5")
        
        layout.addWidget(card1)
        layout.addWidget(card2)
        
        # Test 2: Two-column layout with button alignment test
        directions_card = SimpleCard(
            "Directions", 
            "1. Step one\n2. Step two\n3. Step three\n4. Step four", 
            "#e8f5e8",
            "Save Recipe",
            Qt.AlignLeft  # Left-aligned button
        )
        image_card = SimpleCard(
            "Recipe Image", 
            "Image upload area", 
            "#fff3e0",
            "Upload",
            Qt.AlignRight  # Right-aligned button
        )
        
        # Using utility function - should be clean and simple
        bottom_row = two_column_layout(
            directions_card, 
            image_card, 
            left_proportion=2, 
            right_proportion=1,
            match_heights=True
        )
        
        layout.addWidget(bottom_row)
        
        # Test 3: Button alignment demonstration
        card_a = SimpleCard("Left Button", "Card with left-aligned button", "#ffebee", "Left", Qt.AlignLeft)
        card_b = SimpleCard("Center Button", "Card with center-aligned button", "#e8eaf6", "Center", Qt.AlignCenter) 
        card_c = SimpleCard("Right Button", "Card with right-aligned button", "#e0f2f1", "Right", Qt.AlignRight)
        
        # Match heights manually
        match_card_heights([card_a, card_b, card_c])
        
        three_card_row = create_card_row(
            [card_a, card_b, card_c],
            proportions=[1, 2, 1],  # 1:2:1 ratio
            match_heights=True
        )
        
        layout.addWidget(three_card_row)


def main():
    """Run the simple test."""
    app = QApplication(sys.argv)
    
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f5f5f5;
        }
        Card {
            border: 1px solid #ddd;
            border-radius: 4px;
            background-color: white;
            margin: 2px;
        }
    """)
    
    test = SimpleCardLayoutTest()
    test.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())