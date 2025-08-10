"""
Card Icon Size Demo - Demonstrates different ways to control icon sizes in EnhancedCard

Shows all the available methods for setting and changing icon sizes in header actions
and footer action buttons.
"""

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.TEMPLATE_FOR_UI_TESTS import ThemePlayground
from app.ui.components.layout.enhanced_card import EnhancedCard, CardSize
from app.style.icon.config import Name, Type


class CardIconSizeDemo(ThemePlayground):
    """Demo showing different icon size control methods."""

    def _setup_ui(self):
        """Override to add icon size demo components."""
        # Call parent setup first
        super()._setup_ui()

        # Replace the placeholder content with icon size demos
        self._add_icon_size_demos()

    def _add_icon_size_demos(self):
        """Add card icon size demonstration cards."""
        # Clear existing content
        content_layout = self.content_area.layout()

        # Remove the placeholder
        for i in reversed(range(content_layout.count())):
            item = content_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
            elif item.spacerItem():
                content_layout.removeItem(item)

        # Add demo sections
        self._add_method_demos(content_layout)
        content_layout.addStretch()

    def _add_method_demos(self, parent_layout):
        """Add demonstrations of different icon sizing methods."""
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
        title = QLabel("Card Icon Size Control Methods")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; margin-bottom: 15px;")
        layout.addWidget(title)

        # Method 1: Set icon size when creating header actions
        method1_title = QLabel("Method 1: Set size when adding header actions")
        method1_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #555; margin-top: 10px;")
        layout.addWidget(method1_title)

        cards_row1 = QHBoxLayout()

        # Small icons (16px)
        small_card = (EnhancedCard()
                     .set_title("Small Icons (16px)")
                     .set_subtitle("Header actions with 16px icons")
                     .add_header_action("favorite", Name.HEART, "Favorite", icon_size=16)
                     .add_header_action("share", Name.ADD, "Share", icon_size=16)
                     .add_content_text("Icons set to 16px when created")
                     .set_size(CardSize.COMPACT))

        # Large icons (32px)
        large_card = (EnhancedCard()
                     .set_title("Large Icons (32px)")
                     .set_subtitle("Header actions with 32px icons")
                     .add_header_action("favorite", Name.HEART, "Favorite", icon_size=32)
                     .add_header_action("share", Name.ADD, "Share", icon_size=32)
                     .add_content_text("Icons set to 32px when created")
                     .set_size(CardSize.COMPACT))

        cards_row1.addWidget(small_card)
        cards_row1.addWidget(large_card)
        cards_row1.addStretch()
        layout.addLayout(cards_row1)

        # Method 2: Access button after creation
        method2_title = QLabel("Method 2: Access button after creation and modify")
        method2_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #555; margin-top: 20px;")
        layout.addWidget(method2_title)

        cards_row2 = QHBoxLayout()

        # Modified after creation
        modified_card = (EnhancedCard()
                        .set_title("Modified After Creation")
                        .set_subtitle("Default size changed to 28px")
                        .add_header_action("favorite", Name.HEART, "Favorite")
                        .add_header_action("share", Name.ADD, "Share")
                        .add_content_text("Icons resized after creation using get_header_action()")
                        .set_size(CardSize.COMPACT))

        # Modify the favorite button to be larger
        favorite_btn = modified_card.get_header_action("favorite")
        if favorite_btn:
            favorite_btn.setStateIconSize(28, 28)

        # Modify the share button to be smaller
        share_btn = modified_card.get_header_action("share")
        if share_btn:
            share_btn.setStateIconSize(20, 20)

        cards_row2.addWidget(modified_card)
        cards_row2.addStretch()
        layout.addLayout(cards_row2)

        # Method 3: Set defaults and update existing
        method3_title = QLabel("Method 3: Set defaults and update all existing buttons")
        method3_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #555; margin-top: 20px;")
        layout.addWidget(method3_title)

        cards_row3 = QHBoxLayout()

        # Default size card
        default_card = (EnhancedCard()
                       .set_title("Default Then Updated")
                       .set_subtitle("All icons updated to 26px")
                       .add_header_action("favorite", Name.HEART, "Favorite")
                       .add_header_action("edit", Name.EDIT, "Edit")
                       .add_header_action("settings", Name.SETTINGS, "Settings")
                       .add_content_text("Started with default 24px, then updated all to 26px")
                       .update_header_icon_sizes(26)  # Update all existing header icons
                       .set_size(CardSize.MEDIUM))

        # Mixed sizes card
        mixed_card = (EnhancedCard()
                     .set_title("Mixed Icon Sizes")
                     .set_subtitle("Different sizes per action")
                     .add_header_action("favorite", Name.HEART, "Favorite", icon_size=18)
                     .add_header_action("edit", Name.EDIT, "Edit", icon_size=24)
                     .add_header_action("settings", Name.SETTINGS, "Settings", icon_size=30)
                     .add_content_text("Favorite: 18px, Edit: 24px, Settings: 30px")
                     .set_size(CardSize.MEDIUM))

        cards_row3.addWidget(default_card)
        cards_row3.addWidget(mixed_card)
        cards_row3.addStretch()
        layout.addLayout(cards_row3)

        # Method 4: Footer action icons
        method4_title = QLabel("Method 4: Footer action button icons")
        method4_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #555; margin-top: 20px;")
        layout.addWidget(method4_title)

        cards_row4 = QHBoxLayout()

        # Footer with custom icon sizes
        footer_card = (EnhancedCard()
                      .set_title("Footer Action Icons")
                      .set_subtitle("Custom icon sizes in footer buttons")
                      .add_content_text("Footer buttons with different icon sizes")
                      .add_action_button("Small Action", Name.SUCCESS, icon_size=14)
                      .add_secondary_action("Large Action", Name.SETTINGS, icon_size=22)
                      .set_size(CardSize.MEDIUM))

        cards_row4.addWidget(footer_card)
        cards_row4.addStretch()
        layout.addLayout(cards_row4)

        # Interactive demo buttons
        demo_title = QLabel("Interactive Demo")
        demo_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #555; margin-top: 20px;")
        layout.addWidget(demo_title)

        # Create an interactive card
        self.interactive_card = (EnhancedCard()
                               .set_title("Interactive Size Demo")
                               .set_subtitle("Click buttons below to change icon sizes")
                               .add_header_action("demo1", Name.HEART, "Demo Icon 1")
                               .add_header_action("demo2", Name.EDIT, "Demo Icon 2")
                               .add_content_text("Use the theme controls above to change sizes dynamically")
                               .set_size(CardSize.MEDIUM))

        layout.addWidget(self.interactive_card)

        # Connect card actions to demonstrate logging
        small_card.action_clicked.connect(
            lambda action: self.logger.log_message(f"Small card action: {action}", "event")
        )
        large_card.action_clicked.connect(
            lambda action: self.logger.log_message(f"Large card action: {action}", "event")
        )
        modified_card.action_clicked.connect(
            lambda action: self.logger.log_message(f"Modified card action: {action}", "event")
        )
        default_card.action_clicked.connect(
            lambda action: self.logger.log_message(f"Default card action: {action}", "event")
        )
        mixed_card.action_clicked.connect(
            lambda action: self.logger.log_message(f"Mixed card action: {action}", "event")
        )
        footer_card.action_clicked.connect(
            lambda action: self.logger.log_message(f"Footer card action: {action}", "event")
        )
        self.interactive_card.action_clicked.connect(
            lambda action: self.logger.log_message(f"Interactive card action: {action}", "event")
        )

        parent_layout.addWidget(section)


if __name__ == "__main__":
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

    # Create and show demo
    demo = CardIconSizeDemo()
    demo.setWindowTitle("Card Icon Size Control Demo")
    demo.show()

    sys.exit(app.exec())
