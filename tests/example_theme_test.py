"""
Example Theme Test - Demonstrates extending the theme playground

This example shows how to use the theme playground as a base for specific UI tests.
Copy this file and modify it to test your own components.
"""

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.TEMPLATE_FOR_UI_TESTS import ThemePlayground, main
from app.ui.components.widgets.button import Button, ToolButton
from app.ui.components.inputs.toggle_switch import ToggleSwitch
from app.ui.components.widgets.combobox import ComboBox
from app.ui.components.layout.card import Card
from app.ui.components.layout.enhanced_card import EnhancedCard, CardSize, create_simple_card, create_media_card
from app.style.icon.config import Name, Type


class CustomThemeTest(ThemePlayground):
    """Extended playground with custom test components."""

    def _setup_ui(self):
        """Override to add custom test components."""
        # Call parent setup first
        super()._setup_ui()

        # Replace the placeholder content with test components
        self._add_test_components()

    def _add_test_components(self):
        """Add custom components to test."""
        # Clear existing content
        content_layout = self.content_area.layout()

        # Remove the placeholder
        for i in reversed(range(content_layout.count())):
            item = content_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
            elif item.spacerItem():
                content_layout.removeItem(item)

        # Add test sections
        self._add_button_tests(content_layout)
        self._add_input_tests(content_layout)
        self._add_card_tests(content_layout)
        content_layout.addStretch()

    def _add_button_tests(self, parent_layout):
        """Add button component tests."""
        section = QFrame()
        section.setObjectName("TestSection")
        section.setStyleSheet("""
            QFrame#TestSection {
                background-color: rgba(0, 0, 0, 0.02);
                border-radius: 8px;
                margin: 10px;
                padding: 15px;
            }
        """)

        layout = QVBoxLayout(section)

        # Section title
        title = QLabel("Button Tests")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; margin-bottom: 10px;")
        layout.addWidget(title)

        # Button row
        button_row = QHBoxLayout()

        # Test different button types
        primary_btn = Button("Primary", Type.PRIMARY, Name.DASHBOARD)
        secondary_btn = Button("Secondary", Type.SECONDARY, Name.SETTINGS)
        tool_btn = ToolButton(Type.DEFAULT, Name.ADD)
        tool_btn.setIconSize(24, 24)


        button_row.addWidget(primary_btn)
        button_row.addWidget(secondary_btn)
        button_row.addWidget(tool_btn)
        button_row.addStretch()

        layout.addLayout(button_row)

        # Connect to logger
        primary_btn.clicked.connect(lambda: self.logger.log_message("Primary button clicked", "event"))
        secondary_btn.clicked.connect(lambda: self.logger.log_message("Secondary button clicked", "event"))
        tool_btn.clicked.connect(lambda: self.logger.log_message("Tool button clicked", "event"))

        parent_layout.addWidget(section)

    def _add_input_tests(self, parent_layout):
        """Add input component tests."""
        section = QFrame()
        section.setObjectName("TestSection")
        section.setStyleSheet("""
            QFrame#TestSection {
                background-color: rgba(0, 0, 0, 0.02);
                border-radius: 8px;
                margin: 10px;
                padding: 15px;
            }
        """)

        layout = QVBoxLayout(section)

        # Section title
        title = QLabel("Input Tests")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; margin-bottom: 10px;")
        layout.addWidget(title)

        # Input row
        input_row = QHBoxLayout()

        # Test combobox
        combo_label = QLabel("ComboBox:")
        test_combo = ComboBox(
            list_items=["Option 1", "Option 2", "Option 3"],
            placeholder="Select option..."
        )
        test_combo.currentTextChanged.connect(
            lambda text: self.logger.log_message(f"ComboBox selection: {text}", "event")
        )

        # Test toggle
        toggle_label = QLabel("Toggle:")
        test_toggle = ToggleSwitch(checked=False)
        test_toggle.toggled.connect(
            lambda checked: self.logger.log_message(f"Toggle switched: {'ON' if checked else 'OFF'}", "event")
        )

        input_row.addWidget(combo_label)
        input_row.addWidget(test_combo)
        input_row.addWidget(toggle_label)
        input_row.addWidget(test_toggle)
        input_row.addStretch()

        layout.addLayout(input_row)
        parent_layout.addWidget(section)

    def _add_card_tests(self, parent_layout):
        """Add card component tests."""
        section = QFrame()
        section.setObjectName("TestSection")
        section.setStyleSheet("""
            QFrame#TestSection {
                background-color: rgba(0, 0, 0, 0.02);
                border-radius: 8px;
                margin: 10px;
                padding: 15px;
            }
        """)

        layout = QVBoxLayout(section)

        # Section title
        title = QLabel("Card Tests")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; margin-bottom: 10px;")
        layout.addWidget(title)

        # Card showcase row
        cards_row = QHBoxLayout()

        # 1. Simple card using original Card widget
        original_card = Card("Original Card", "Using constructor params")
        original_card.add_widget(QLabel("This is the original Card widget design"))
        cards_row.addWidget(original_card)

        # 2. Simple enhanced card using fluent API
        simple_enhanced = (EnhancedCard()
                          .set_title("Enhanced Card")
                          .set_subtitle("Built with fluent API")
                          .add_content_text("This card was created using method chaining for a more flexible API.")
                          .set_size(CardSize.COMPACT))
        cards_row.addWidget(simple_enhanced)

        # 3. Feature-rich card
        feature_card = (EnhancedCard()
                       .set_title("Feature Rich")
                       .set_subtitle("Multiple components")
                       .add_header_action("favorite", Name.HEART, "Add to favorites")
                       .add_header_action("share", Name.ADD, "Share card")
                       .add_content_text("This card demonstrates multiple features:")
                       .add_content_text("• Header with actions\n• Multiple content sections\n• Footer buttons")
                       .add_action_button("Primary Action", Name.SUCCESS)
                       .add_secondary_action("Secondary", Name.SETTINGS)
                       .set_size(CardSize.MEDIUM))
        cards_row.addWidget(feature_card)

        cards_row.addStretch()
        layout.addLayout(cards_row)

        # Connect card actions to logger
        simple_enhanced.action_clicked.connect(
            lambda action: self.logger.log_message(f"Simple card action: {action}", "event")
        )
        feature_card.action_clicked.connect(
            lambda action: self.logger.log_message(f"Feature card action: {action}", "event")
        )

        parent_layout.addWidget(section)


if __name__ == "__main__":
    # Use the main function but with our custom class
    from PySide6.QtWidgets import QApplication
    from app.style.theme.config import Color, Mode
    from app.style.theme_controller import Theme

    app = QApplication(sys.argv)

    # Set default theme
    try:
        current_color = Theme.get_current_theme_color()
        current_mode = Theme.get_current_theme_mode()
        if not current_color or not current_mode:
            Theme.setTheme(Color.BLUE, Mode.LIGHT)
    except:
        Theme.setTheme(Color.BLUE, Mode.LIGHT)

    # Create and show custom test
    playground = CustomThemeTest()
    playground.setWindowTitle("Custom Theme Test Example")
    playground.show()

    sys.exit(app.exec())
