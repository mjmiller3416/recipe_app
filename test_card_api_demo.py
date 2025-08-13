"""test_card_api_demo.py

Comprehensive demonstration of the improved Card API.
Shows all the new features and improved functionality.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QLabel, QGroupBox, QHBoxLayout, QScrollArea
)
from PySide6.QtCore import Qt

from app.ui.components.layout.card import Card
from app.ui.helpers.card_utils import add_two_column
from app.style.icon.config import Type, Name


class CardAPIDemo(QMainWindow):
    """Demonstrate the improved Card API."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Improved Card API Demo")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create scroll area for the content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create main content widget
        content_widget = QWidget()
        main_layout = QVBoxLayout(content_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Set up scroll area
        scroll_area.setWidget(content_widget)
        self.setCentralWidget(scroll_area)
        
        self.create_demos(main_layout)
    
    def create_demos(self, layout):
        """Create demonstration sections."""
        
        # Title
        title = QLabel("Improved Card API Demonstration")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        self.demo_constructor_changes()
        self.demo_size_policy_improvements()
        self.demo_button_alignment()
        self.demo_real_world_usage()
        
        # Add stretch at the end for proper spacing
        layout.addStretch()
    
    def demo_constructor_changes(self):
        """Demonstrate the simplified constructor."""
        section = self.create_section("1. Simplified Constructor")
        
        # Old vs New comparison
        comparison = QHBoxLayout()
        
        # New way (simplified)
        new_group = QGroupBox("New Constructor (Simplified)")
        new_layout = QVBoxLayout(new_group)
        
        # Example code label
        code_label = QLabel("""# Simplified constructor:
card = Card(layout="vbox", card_type="Primary")

# Default elevation (ELEVATION_6)
# No need to specify elevation unless needed
# Use setElevation() method for edge cases only""")
        code_label.setStyleSheet("font-family: monospace; background-color: #f0f0f0; padding: 10px;")
        new_layout.addWidget(code_label)
        
        # Actual example
        example_card = Card(card_type="Default")
        example_card.setHeader("Simplified Card")
        example_card.addWidget(QLabel("Created with new simplified constructor"))
        example_card.addButton("Default Button")
        new_layout.addWidget(example_card)
        
        comparison.addWidget(new_group)
        section.addLayout(comparison)
    
    def demo_size_policy_improvements(self):
        """Demonstrate size policy improvements."""
        section = self.create_section("2. Size Policy Improvements")
        
        row_layout = QHBoxLayout()
        
        # Default behavior
        default_group = QGroupBox("Default: Preferred Policy")
        default_layout = QVBoxLayout(default_group)
        
        default_card = Card()
        default_card.setHeader("Default Card")
        default_card.addWidget(QLabel("Uses Preferred size policy\n(was Fixed before)"))
        default_card.addButton("No Cutoff!")
        default_layout.addWidget(default_card)
        
        # Expansion demonstration
        expand_group = QGroupBox("Expansion Control")
        expand_layout = QVBoxLayout(expand_group)
        
        expand_card = Card()
        expand_card.setHeader("Expanding Card")
        expand_card.addWidget(QLabel("This card uses expandWidth(True)\nto grab available space"))
        expand_card.expandWidth(True)  # Test expansion
        expand_card.addButton("Expanded", alignment=Qt.AlignRight)
        expand_layout.addWidget(expand_card)
        
        # Fixed size demonstration
        fixed_card = Card()
        fixed_card.setHeader("Fixed Size Card")
        fixed_card.addWidget(QLabel("This card uses setFixed()\nfor content-based sizing"))
        fixed_card.setFixed()  # Test fixed size
        fixed_card.addButton("Fixed Size")
        expand_layout.addWidget(fixed_card)
        
        row_layout.addWidget(default_group)
        row_layout.addWidget(expand_group)
        section.addLayout(row_layout)
    
    def demo_button_alignment(self):
        """Demonstrate button alignment functionality."""
        section = self.create_section("3. Button Alignment Control")
        
        # Three cards showing different alignments
        alignment_layout = QHBoxLayout()
        
        # Left aligned button
        left_card = Card()
        left_card.setHeader("Left Aligned")
        left_card.addWidget(QLabel("Button aligned to the left"))
        left_card.addButton("Left Button", alignment=Qt.AlignLeft)
        
        # Center aligned button (default)
        center_card = Card()
        center_card.setHeader("Center Aligned")
        center_card.addWidget(QLabel("Button centered (default)"))
        center_card.addButton("Center Button", alignment=Qt.AlignCenter)
        
        # Right aligned button
        right_card = Card()
        right_card.setHeader("Right Aligned")
        right_card.addWidget(QLabel("Button aligned to the right"))
        right_card.addButton("Right Button", alignment=Qt.AlignRight)
        
        # Make cards same height
        left_card.expandHeight(True)
        center_card.expandHeight(True)
        right_card.expandHeight(True)
        
        alignment_layout.addWidget(left_card)
        alignment_layout.addWidget(center_card)
        alignment_layout.addWidget(right_card)
        
        section.addLayout(alignment_layout)
    
    def demo_real_world_usage(self):
        """Show real-world usage example."""
        section = self.create_section("4. Real-World Usage Example")
        
        # Create realistic cards
        recipe_card = Card(card_type="Default")
        recipe_card.setHeader("Recipe Details")
        recipe_card.setSubHeader("Enter your recipe information")
        recipe_card.addWidget(QLabel("Recipe Name: Chocolate Chip Cookies\nTime: 45 mins | Servings: 24"))
        
        # Directions card with left-aligned save button
        directions_card = Card()
        directions_card.setHeader("Directions")
        directions_card.addWidget(QLabel(
            "1. Preheat oven to 375°F\n"
            "2. Mix dry ingredients\n"
            "3. Cream butter and sugars\n"
            "4. Combine wet and dry ingredients\n"
            "5. Bake for 9-11 minutes"
        ))
        directions_card.addButton("Save Recipe", alignment=Qt.AlignLeft)
        
        # Image upload card with right-aligned button
        image_card = Card()
        image_card.setHeader("Recipe Image")
        image_card.addWidget(QLabel("Upload an image of your\nfinished recipe"))
        image_card.addButton("Upload Image", alignment=Qt.AlignRight)
        
        # Layout using shadow-safe utility functions
        section.addWidget(recipe_card)
        
        # Use clean approach - preserves shadow effects
        add_two_column(
            section,  # Add directly to section layout
            directions_card, 
            image_card,
            left_proportion=2,
            right_proportion=1,
            match_heights=True
        )
    
    def create_section(self, title: str) -> QVBoxLayout:
        """Create a demo section with title."""
        # Get the content widget's layout from the scroll area
        content_widget = self.centralWidget().widget()
        content_layout = content_widget.layout()
        
        # Section title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1976d2; margin: 10px 0px;")
        content_layout.addWidget(title_label)
        
        # Section container
        section_widget = QWidget()
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(20, 10, 20, 20)
        section_widget.setStyleSheet("background-color: #fafafa; border: 1px solid #e0e0e0; border-radius: 4px;")
        
        content_layout.addWidget(section_widget)
        return section_layout


def main():
    """Run the Card API demo."""
    app = QApplication(sys.argv)
    
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f5f5f5;
        }
        QGroupBox {
            font-weight: bold;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            color: #333;
        }
        Card {
            border: 1px solid #ddd;
            border-radius: 4px;
            background-color: white;
            margin: 2px;
        }
    """)
    
    demo = CardAPIDemo()
    demo.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())