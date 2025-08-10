"""
Card Text Fix Demo - Shows the text clipping fixes in action

Demonstrates the before/after of text clipping issues and the various
methods to prevent them in EnhancedCard widgets.
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


class CardTextFixDemo(ThemePlayground):
    """Demo showing text clipping fixes."""

    def _setup_ui(self):
        """Override to add text fix demo components."""
        # Call parent setup first
        super()._setup_ui()

        # Replace the placeholder content with text fix demos
        self._add_text_fix_demos()

    def _add_text_fix_demos(self):
        """Add card text fix demonstrations."""
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
        self._add_size_comparisons(content_layout)
        self._add_wrapping_demos(content_layout)
        self._add_button_demos(content_layout)
        content_layout.addStretch()

    def _add_size_comparisons(self, parent_layout):
        """Add size comparison demonstrations."""
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
        title = QLabel("Card Size Improvements")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; margin-bottom: 10px;")
        layout.addWidget(title)

        # Old vs New sizes
        sizes_row = QHBoxLayout()

        # Compact cards - old size would be too narrow
        compact_demo = (EnhancedCard()
                       .set_title("Compact Card with Longer Title That Would Clip")
                       .set_subtitle("Subtitle that might also get clipped in narrow cards")
                       .add_header_action("favorite", Name.HEART, "Favorite")
                       .add_header_action("share", Name.ADD, "Share")
                       .add_content_text("Now uses 320px width instead of 280px")
                       .set_size(CardSize.COMPACT))

        # Medium cards - more space
        medium_demo = (EnhancedCard()
                      .set_title("Medium Card With Even Longer Title Text")
                      .set_subtitle("Subtitles can now be longer without getting cut off")
                      .add_header_action("favorite", Name.HEART, "Favorite")
                      .add_header_action("edit", Name.EDIT, "Edit")
                      .add_header_action("settings", Name.SETTINGS, "Settings")
                      .add_content_text("Now uses 400px width instead of 340px")
                      .set_size(CardSize.MEDIUM))

        # New wide size
        wide_demo = (EnhancedCard()
                    .set_title("Wide Card For Really Long Titles That Need Extra Space")
                    .set_subtitle("Perfect for detailed subtitles and multiple header actions without crowding")
                    .add_header_action("favorite", Name.HEART, "Favorite")
                    .add_header_action("edit", Name.EDIT, "Edit")
                    .add_header_action("share", Name.ADD, "Share")
                    .add_header_action("settings", Name.SETTINGS, "Settings")
                    .add_content_text("New WIDE size: 600px width for complex cards")
                    .set_size(CardSize.WIDE))

        sizes_row.addWidget(compact_demo)
        sizes_row.addWidget(medium_demo)
        sizes_row.addWidget(wide_demo)
        sizes_row.addStretch()
        layout.addLayout(sizes_row)

        parent_layout.addWidget(section)

    def _add_wrapping_demos(self, parent_layout):
        """Add text wrapping demonstrations."""
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
        title = QLabel("Text Wrapping and Layout Improvements")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; margin-bottom: 10px;")
        layout.addWidget(title)

        wrapping_row = QHBoxLayout()

        # Auto-wrapping card
        auto_wrap_card = (EnhancedCard()
                         .set_title("This is a Very Long Title That Demonstrates Automatic Text Wrapping")
                         .set_subtitle("And this subtitle is also quite long to show how wrapping works for both title and subtitle text")
                         .add_header_action("favorite", Name.HEART, "Favorite")
                         .add_content_text("Headers now use word wrapping and expanding size policies")
                         .set_size(CardSize.MEDIUM))

        # Custom minimum width card
        min_width_card = (EnhancedCard()
                         .set_title("Custom Minimum Width")
                         .set_subtitle("Prevents squashing below a certain size")
                         .add_content_text("This card has a minimum width set to prevent text clipping")
                         .set_minimum_width(350)
                         .add_header_action("settings", Name.SETTINGS, "Settings")
                         .set_size(CardSize.COMPACT))  # Compact but with min width override

        wrapping_row.addWidget(auto_wrap_card)
        wrapping_row.addWidget(min_width_card)
        wrapping_row.addStretch()
        layout.addLayout(wrapping_row)

        parent_layout.addWidget(section)

    def _add_button_demos(self, parent_layout):
        """Add button sizing demonstrations."""
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
        title = QLabel("Button Text Clipping Fixes")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; margin-bottom: 10px;")
        layout.addWidget(title)

        button_row = QHBoxLayout()

        # Card with long button text
        button_demo = (EnhancedCard()
                      .set_title("Better Button Sizing")
                      .set_subtitle("Footer buttons now expand properly")
                      .add_content_text("Action buttons use expanding size policy to prevent text clipping")
                      .add_action_button("View Full Recipe Details", Name.SUCCESS)
                      .add_secondary_action("Share with Friends", Name.ADD)
                      .set_size(CardSize.MEDIUM))

        # Card showing header action improvements
        header_actions_demo = (EnhancedCard()
                              .set_title("Header Layout Improvements")
                              .set_subtitle("Text and actions balance properly")
                              .add_header_action("fav", Name.HEART, "Add to favorites")
                              .add_header_action("edit", Name.EDIT, "Edit recipe")
                              .add_header_action("share", Name.ADD, "Share recipe")
                              .add_content_text("Header content gets priority space, actions stay compact")
                              .set_size(CardSize.MEDIUM))

        button_row.addWidget(button_demo)
        button_row.addWidget(header_actions_demo)
        button_row.addStretch()
        layout.addLayout(button_row)

        # Interactive demo
        interactive_title = QLabel("Interactive Test")
        interactive_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #555; margin-top: 20px;")
        layout.addWidget(interactive_title)

        # Test card with very long content
        self.test_card = (EnhancedCard()
                         .set_title("Interactive Test Card with Very Long Title That Would Previously Get Clipped")
                         .set_subtitle("This subtitle is also intentionally long to test the wrapping and sizing behavior")
                         .add_header_action("favorite", Name.HEART, "Add to favorites")
                         .add_header_action("edit", Name.EDIT, "Edit this item")
                         .add_header_action("share", Name.ADD, "Share with others")
                         .add_content_text("You can test theme changes using the controls above to see how text behaves.")
                         .add_action_button("Primary Action Button", Name.SUCCESS)
                         .add_secondary_action("Secondary Action", Name.SETTINGS)
                         .set_size(CardSize.LARGE))

        layout.addWidget(self.test_card)

        # Connect actions to logger
        button_demo.action_clicked.connect(
            lambda action: self.logger.log_message(f"Button demo action: {action}", "event")
        )
        header_actions_demo.action_clicked.connect(
            lambda action: self.logger.log_message(f"Header demo action: {action}", "event")
        )
        self.test_card.action_clicked.connect(
            lambda action: self.logger.log_message(f"Test card action: {action}", "event")
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
    demo = CardTextFixDemo()
    demo.setWindowTitle("Card Text Clipping Fix Demo")
    demo.resize(1200, 800)  # Make window larger to show the cards properly
    demo.show()

    sys.exit(app.exec())
