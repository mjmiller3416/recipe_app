"""test_card_layout_demo.py

Comprehensive demonstration of CardLayout API and features.
Shows all capabilities including proportions, height modes, alignment, and grouping.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QPushButton, QTextEdit, QScrollArea,
    QGroupBox, QComboBox, QSpinBox, QCheckBox
)
from PySide6.QtCore import Qt

from app.ui.components.layout.card import Card
from app.ui.components.layout.card_layout import (
    CardLayout, Direction, HeightMode, AlignmentMode,
    HorizontalCardLayout, VerticalCardLayout
)


class DemoCard(Card):
    """Demo card with customizable content for testing."""
    
    def __init__(self, title: str, content: str = "", height: int = None, color: str = None):
        super().__init__()
        self.setHeader(title)
        
        # Add content
        if content:
            content_label = QLabel(content)
            content_label.setWordWrap(True)
            self.addWidget(content_label)
        
        # Set fixed height if specified
        if height:
            self.setFixedHeight(height)
        
        # Set background color for visual distinction
        if color:
            self.setStyleSheet(f"background-color: {color};")


class CardLayoutDemo(QMainWindow):
    """Main demo application showing CardLayout capabilities."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CardLayout API Demo")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Create scroll area for the demos
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create demo container
        demo_widget = QWidget()
        self.demo_layout = QVBoxLayout(demo_widget)
        self.demo_layout.setSpacing(30)
        self.demo_layout.setContentsMargins(20, 20, 20, 20)
        
        scroll.setWidget(demo_widget)
        
        main_layout = QVBoxLayout(main_widget)
        main_layout.addWidget(scroll)
        
        self.create_demos()
    
    def create_demos(self):
        """Create all demo sections."""
        
        # Title
        title = QLabel("CardLayout API Demonstration")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignCenter)
        self.demo_layout.addWidget(title)
        
        self.demo_basic_usage()
        self.demo_proportional_sizing()
        self.demo_height_modes()
        self.demo_mixed_layouts()
        self.demo_interactive_controls()
        self.demo_real_world_example()
        
        self.demo_layout.addStretch()
    
    def demo_basic_usage(self):
        """Demonstrate basic CardLayout usage."""
        section = self.create_section("1. Basic Usage")
        
        # Horizontal layout
        h_group = QGroupBox("Horizontal Layout")
        h_layout = QVBoxLayout(h_group)
        
        card_layout = HorizontalCardLayout()
        card_layout.addCard(DemoCard("Card 1", "Content for card 1", color="#e3f2fd"))
        card_layout.addCard(DemoCard("Card 2", "Content for card 2", color="#f3e5f5"))
        card_layout.addCard(DemoCard("Card 3", "Content for card 3", color="#e8f5e8"))
        
        container = card_layout.createContainer()
        container.setMinimumHeight(200)  # Ensure adequate height  
        h_layout.addWidget(container)
        
        # Vertical layout
        v_group = QGroupBox("Vertical Layout")
        v_layout = QVBoxLayout(v_group)
        
        card_layout_v = VerticalCardLayout()
        card_layout_v.addCard(DemoCard("Card A", "First vertical card", color="#fff3e0"))
        card_layout_v.addCard(DemoCard("Card B", "Second vertical card", color="#fce4ec"))
        
        container_v = card_layout_v.createContainer()
        container_v.setMinimumHeight(200)  # Ensure adequate height
        v_layout.addWidget(container_v)
        
        demo_layout = QHBoxLayout()
        demo_layout.addWidget(h_group)
        demo_layout.addWidget(v_group)
        
        section.addLayout(demo_layout)
    
    def demo_proportional_sizing(self):
        """Demonstrate proportional sizing features."""
        section = self.create_section("2. Proportional Sizing")
        
        # Method 1: Individual proportions
        group1 = QGroupBox("Individual Proportions - addCard(card, proportion=X)")
        layout1 = QVBoxLayout(group1)
        
        card_layout1 = HorizontalCardLayout()
        card_layout1.addCard(DemoCard("2x", "Takes 2/4 space"), proportion=2)
        card_layout1.addCard(DemoCard("1x", "Takes 1/4 space"), proportion=1)
        card_layout1.addCard(DemoCard("1x", "Takes 1/4 space"), proportion=1)
        
        container1 = QWidget()
        container1.setLayout(card_layout1)
        layout1.addWidget(container1)
        
        # Method 2: Batch proportions
        group2 = QGroupBox("Batch Proportions - setProportions(3, 2, 1)")
        layout2 = QVBoxLayout(group2)
        
        card_layout2 = HorizontalCardLayout()
        card_layout2.addCard(DemoCard("3x", "Takes 3/6 space", color="#ffebee"))
        card_layout2.addCard(DemoCard("2x", "Takes 2/6 space", color="#e8eaf6"))
        card_layout2.addCard(DemoCard("1x", "Takes 1/6 space", color="#e0f2f1"))
        card_layout2.setProportions(3, 2, 1)
        
        container2 = QWidget()
        container2.setLayout(card_layout2)
        layout2.addWidget(container2)
        
        section.addWidget(group1)
        section.addWidget(group2)
    
    def demo_height_modes(self):
        """Demonstrate different height modes."""
        section = self.create_section("3. Height Modes")
        
        height_layout = QHBoxLayout()
        
        # Content height
        group1 = QGroupBox("HeightMode.CONTENT")
        layout1 = QVBoxLayout(group1)
        
        card_layout1 = HorizontalCardLayout()
        card_layout1.setHeightMode(HeightMode.CONTENT)
        card_layout1.addCard(DemoCard("Short", "Small content", color="#f1f8e9"))
        card_layout1.addCard(DemoCard("Tall", "Much longer content that spans multiple lines and creates a taller card to demonstrate content-based height", color="#f3e5f5"))
        card_layout1.addCard(DemoCard("Medium", "Medium amount of content here", color="#e3f2fd"))
        
        container1 = QWidget()
        container1.setLayout(card_layout1)
        layout1.addWidget(container1)
        
        # Matched height
        group2 = QGroupBox("HeightMode.MATCH")
        layout2 = QVBoxLayout(group2)
        
        card_layout2 = HorizontalCardLayout()
        card_layout2.setHeightMode(HeightMode.MATCH)
        card_layout2.addCard(DemoCard("Short", "Small content", color="#f1f8e9"))
        card_layout2.addCard(DemoCard("Tall", "Much longer content that spans multiple lines and creates a taller card, but all cards match this height", color="#f3e5f5"))
        card_layout2.addCard(DemoCard("Medium", "Medium amount of content here", color="#e3f2fd"))
        
        container2 = QWidget()
        container2.setLayout(card_layout2)
        layout2.addWidget(container2)
        
        height_layout.addWidget(group1)
        height_layout.addWidget(group2)
        section.addLayout(height_layout)
    
    def demo_mixed_layouts(self):
        """Demonstrate complex nested layouts."""
        section = self.create_section("4. Mixed & Nested Layouts")
        
        # Create main horizontal layout
        main_card_layout = HorizontalCardLayout()
        
        # Left side - vertical stack
        left_layout = VerticalCardLayout()
        left_layout.addCard(DemoCard("Top Left", "First card in left column", color="#e8f5e8"))
        left_layout.addCard(DemoCard("Bottom Left", "Second card in left column", color="#e8f5e8"))
        
        left_container = QWidget()
        left_container.setLayout(left_layout)
        left_card = Card()
        left_card.setHeader("Left Column")
        left_card.addWidget(left_container)
        
        # Right side - single large card
        right_card = DemoCard(
            "Right Side", 
            "This is a larger card that takes up more space on the right side of the layout. "
            "It demonstrates how different card sizes can work together in the same layout.",
            color="#fff3e0"
        )
        
        # Add to main layout with proportions
        main_card_layout.addCard(left_card, proportion=1)
        main_card_layout.addCard(right_card, proportion=2)
        main_card_layout.setHeightMode(HeightMode.MATCH)
        
        container = QWidget()
        container.setLayout(main_card_layout)
        section.addWidget(container)
    
    def demo_interactive_controls(self):
        """Create interactive demo with live controls."""
        section = self.create_section("5. Interactive Demo")
        
        # Create the demo layout
        self.interactive_layout = HorizontalCardLayout()
        self.demo_cards = [
            DemoCard("Card 1", "Interactive card 1", color="#ffebee"),
            DemoCard("Card 2", "Interactive card 2", color="#e8eaf6"),
            DemoCard("Card 3", "Interactive card 3", color="#e0f2f1")
        ]
        
        for card in self.demo_cards:
            self.interactive_layout.addCard(card)
        
        demo_container = self.interactive_layout.createContainer()
        
        # Create controls
        controls_group = QGroupBox("Live Controls")
        controls_layout = QHBoxLayout(controls_group)
        
        # Height mode control
        height_label = QLabel("Height Mode:")
        self.height_combo = QComboBox()
        self.height_combo.addItems(["CONTENT", "MATCH"])
        self.height_combo.currentTextChanged.connect(self.update_height_mode)
        
        # Proportion controls
        prop_label = QLabel("Proportions:")
        self.prop1_spin = QSpinBox()
        self.prop1_spin.setRange(1, 10)
        self.prop1_spin.setValue(1)
        self.prop1_spin.valueChanged.connect(self.update_proportions)
        
        self.prop2_spin = QSpinBox()
        self.prop2_spin.setRange(1, 10)
        self.prop2_spin.setValue(1)
        self.prop2_spin.valueChanged.connect(self.update_proportions)
        
        self.prop3_spin = QSpinBox()
        self.prop3_spin.setRange(1, 10)
        self.prop3_spin.setValue(1)
        self.prop3_spin.valueChanged.connect(self.update_proportions)
        
        # Spacing control
        spacing_label = QLabel("Spacing:")
        self.spacing_spin = QSpinBox()
        self.spacing_spin.setRange(0, 50)
        self.spacing_spin.setValue(16)
        self.spacing_spin.valueChanged.connect(self.update_spacing)
        
        # Margin control
        margin_label = QLabel("Margins:")
        self.margin_spin = QSpinBox()
        self.margin_spin.setRange(0, 50)
        self.margin_spin.setValue(10)
        self.margin_spin.valueChanged.connect(self.update_margins)
        
        controls_layout.addWidget(height_label)
        controls_layout.addWidget(self.height_combo)
        controls_layout.addWidget(prop_label)
        controls_layout.addWidget(self.prop1_spin)
        controls_layout.addWidget(self.prop2_spin)
        controls_layout.addWidget(self.prop3_spin)
        controls_layout.addWidget(spacing_label)
        controls_layout.addWidget(self.spacing_spin)
        controls_layout.addWidget(margin_label)
        controls_layout.addWidget(self.margin_spin)
        controls_layout.addStretch()
        
        section.addWidget(demo_container)
        section.addWidget(controls_group)
    
    def demo_real_world_example(self):
        """Show a real-world layout example."""
        section = self.create_section("6. Real-World Example: Recipe App Layout")
        
        # Simulate the recipe app layout structure
        main_layout = VerticalCardLayout()
        
        # Top: Recipe details (full width)
        recipe_card = DemoCard(
            "Recipe Info",
            "Recipe Name: Spaghetti Carbonara\nTime: 30 mins | Servings: 4 | Category: Italian",
            color="#e3f2fd"
        )
        
        # Middle: Ingredients (full width)
        ingredients_card = DemoCard(
            "Ingredients",
            "• 400g Spaghetti\n• 200g Pancetta\n• 4 Eggs\n• 100g Parmesan\n• Black Pepper",
            color="#f3e5f5"
        )
        
        # Bottom row: Directions and Image side by side
        bottom_layout = HorizontalCardLayout()
        
        directions_card = DemoCard(
            "Directions & Notes",
            "1. Cook pasta according to package instructions\n"
            "2. Fry pancetta until crispy\n"
            "3. Mix eggs and cheese in bowl\n"
            "4. Combine everything while hot\n"
            "5. Season with pepper and serve",
            color="#e8f5e8"
        )
        
        image_card = DemoCard(
            "Recipe Image",
            "[ Recipe Image Upload Area ]\n\nUpload an image of your finished recipe",
            color="#fff3e0"
        )
        
        bottom_layout.addCard(directions_card, proportion=2)
        bottom_layout.addCard(image_card, proportion=1)
        bottom_layout.setHeightMode(HeightMode.MATCH)
        
        bottom_container = QWidget()
        bottom_container.setLayout(bottom_layout)
        bottom_card = Card()
        bottom_card.addWidget(bottom_container)
        
        main_layout.addCard(recipe_card)
        main_layout.addCard(ingredients_card)
        main_layout.addCard(bottom_card)
        
        container = QWidget()
        container.setLayout(main_layout)
        section.addWidget(container)
    
    def create_section(self, title: str) -> QVBoxLayout:
        """Create a demo section with title."""
        # Section title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1976d2; margin: 10px 0px;")
        self.demo_layout.addWidget(title_label)
        
        # Section container
        section_widget = QWidget()
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(20, 10, 20, 20)
        section_widget.setStyleSheet("background-color: #fafafa; border: 1px solid #e0e0e0; border-radius: 4px;")
        
        self.demo_layout.addWidget(section_widget)
        return section_layout
    
    # Interactive demo methods
    def update_height_mode(self, mode_text: str):
        """Update height mode based on combo selection."""
        mode = HeightMode.MATCH if mode_text == "MATCH" else HeightMode.CONTENT
        self.interactive_layout.setHeightMode(mode)
    
    def update_proportions(self):
        """Update proportions based on spin box values."""
        prop1 = self.prop1_spin.value()
        prop2 = self.prop2_spin.value()
        prop3 = self.prop3_spin.value()
        self.interactive_layout.setProportions(prop1, prop2, prop3)
    
    def update_spacing(self, spacing: int):
        """Update spacing based on spin box value."""
        self.interactive_layout.setCardSpacing(spacing)
    
    def update_margins(self, margin: int):
        """Update margins based on spin box value."""
        self.interactive_layout.setMargins(margin, margin, margin, margin)


def main():
    """Run the CardLayout demo application."""
    app = QApplication(sys.argv)
    
    # Set application style
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
        }
    """)
    
    demo = CardLayoutDemo()
    demo.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())