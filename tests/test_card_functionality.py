"""
Card Widget Functionality Test

A comprehensive test demonstrating the refactored Card widget functionality,
based on the UI test template structure. Shows layout management, elevation effects,
content margins, and generic container behavior.

Usage:
    python tests/test_card_functionality.py

Features:
- Theme-aware test environment with real-time switching
- Interactive card demonstrations
- Debug logging for widget events
- Scrollable content area with multiple test sections
"""

import sys
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, Signal, QObject
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QScrollArea, QFrame, QLabel, QPlainTextEdit, QPushButton,
    QLineEdit, QTextEdit, QSizePolicy, QGridLayout
)
from PySide6.QtGui import QFont

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.ui.components.widgets.combobox import ComboBox
from app.ui.components.widgets.toggle_switch import ToggleSwitch
from app.ui.components.widgets.button import Button
from app.ui.components.layout.card import Card
from app.style.theme.config import Color, Mode
from app.style.theme_controller import Theme
from app.style.icon.config import Name, Type
from app.style.effects.config import Shadow


class ThemeManager(QObject):
    """Minimal theme manager for the test environment."""

    theme_changed = Signal(dict)

    def __init__(self):
        super().__init__()
        self._startup_color = None
        self._startup_mode = None
        self._current_color = None
        self._current_mode = None

    def initialize_startup_state(self):
        """Capture the current theme state as startup defaults."""
        self._startup_color = Theme.get_current_theme_color()
        self._startup_mode = Theme.get_current_theme_mode()
        self._current_color = self._startup_color
        self._current_mode = self._startup_mode

    def get_current_theme(self) -> Dict[str, Any]:
        """Get current theme state."""
        return {
            'color': self._current_color,
            'mode': self._current_mode,
            'color_name': self._current_color.name if self._current_color else 'None',
            'mode_name': self._current_mode.value if self._current_mode else 'None'
        }

    def set_color(self, color_enum: Color):
        """Set theme color and update immediately."""
        old_color = self._current_color
        self._current_color = color_enum
        Theme.setThemeColor(color_enum)
        self.theme_changed.emit({
            'type': 'color_change',
            'old': old_color.name if old_color else 'None',
            'new': color_enum.name
        })

    def set_mode(self, mode: str):
        """Set theme mode (light/dark) and update immediately."""
        mode_enum = Mode.LIGHT if mode == "light" else Mode.DARK
        old_mode = self._current_mode
        self._current_mode = mode_enum
        Theme.setThemeMode(mode_enum)
        self.theme_changed.emit({
            'type': 'mode_change',
            'old': old_mode.value if old_mode else 'None',
            'new': mode_enum.value
        })

    def reset_to_startup_defaults(self):
        """Reset both color and mode to startup state."""
        old_theme = self.get_current_theme()
        self._current_color = self._startup_color
        self._current_mode = self._startup_mode

        if self._startup_color and self._startup_mode:
            Theme.setTheme(self._startup_color, self._startup_mode)

        self.theme_changed.emit({
            'type': 'reset',
            'old_color': old_theme['color_name'],
            'old_mode': old_theme['mode_name'],
            'new_color': self._current_color.name if self._current_color else 'None',
            'new_mode': self._current_mode.value if self._current_mode else 'None'
        })


class LoggingWidget(QPlainTextEdit):
    """Enhanced logging widget with console styling."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LoggingConsole")

        # Console styling
        font = QFont("Consolas", 9)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)

        self.setMaximumBlockCount(1000)  # Limit log history
        self.setReadOnly(True)
        self.setLineWrapMode(QPlainTextEdit.WidgetWidth)

        # Style as console
        self.setStyleSheet("""
            QPlainTextEdit#LoggingConsole {
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Courier New', monospace;
            }
        """)

    def log_message(self, message: str, level: str = "info"):
        """Add a timestamped log entry."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        level_color = {
            "info": "#87CEEB",     # Sky blue
            "event": "#90EE90",    # Light green
            "warning": "#FFD700",  # Gold
            "error": "#FF6B6B"     # Light red
        }.get(level, "#e0e0e0")

        formatted_message = f'<span style="color: #888">[{timestamp}]</span> <span style="color: {level_color}">[{level.upper()}]</span> {message}'
        self.appendHtml(formatted_message)

        # Auto-scroll to bottom
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


class CardContentArea(QFrame):
    """Main content area with card widget demonstrations."""

    widget_event = Signal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CardContentArea")

        # Setup main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(30)

        # Add title
        title = QLabel("Card Widget Functionality Demonstration")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("margin-bottom: 20px; color: #333;")
        main_layout.addWidget(title)

        # Create test sections
        main_layout.addWidget(self._create_basic_layout_section())
        main_layout.addWidget(self._create_grid_layout_section())
        main_layout.addWidget(self._create_sizing_section())
        main_layout.addWidget(self._create_elevation_section())
        main_layout.addWidget(self._create_content_margins_section())
        main_layout.addWidget(self._create_interactive_section())

        main_layout.addStretch()

        # Enable mouse tracking for events
        self.setMouseTracking(True)

    def _create_section_frame(self, title: str):
        """Helper to create a consistent section frame."""
        section = QFrame()
        section.setFrameStyle(QFrame.Box)
        section.setStyleSheet("""
            QFrame {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.5);
                margin: 5px;
            }
        """)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(20, 15, 20, 15)

        # Section title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #444; margin-bottom: 10px;")
        layout.addWidget(title_label)

        return section, layout

    def _create_basic_layout_section(self):
        """Demonstrate basic VBox and HBox layouts."""
        section, layout = self._create_section_frame("Basic Layouts (VBox & HBox)")

        # Container for cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)

        # VBox Card
        vbox_card = Card()
        vbox_card.addLayout("vbox", spacing=15)

        vbox_title = QLabel("VBox Layout Card")
        vbox_title.setStyleSheet("font-weight: bold; font-size: 12px; color: #555;")
        vbox_card.addWidget(vbox_title)

        vbox_card.addWidget(QLabel("Item 1: Simple label"))

        btn = QPushButton("Item 2: Interactive Button")
        btn.clicked.connect(lambda: self.widget_event.emit("button_click", {"section": "vbox", "button": "interactive"}))
        vbox_card.addWidget(btn)

        text_edit = QTextEdit()
        text_edit.setPlainText("Item 3: Text editor - try typing here!")
        text_edit.setMaximumHeight(80)
        vbox_card.addWidget(text_edit)

        cards_layout.addWidget(vbox_card, 0, Qt.AlignLeft)  # No stretch, left-aligned

        # HBox Card
        hbox_card = Card()
        hbox_card.addLayout("hbox", spacing=10)

        hbox_card.addWidget(QLabel("Search:"))

        search_field = QLineEdit()
        search_field.setPlaceholderText("Enter search terms...")
        hbox_card.addWidget(search_field)

        search_btn = QPushButton("Go")
        search_btn.clicked.connect(lambda: self.widget_event.emit("search", {"query": search_field.text()}))
        hbox_card.addWidget(search_btn)

        cards_layout.addWidget(hbox_card, 0, Qt.AlignLeft)  # No stretch, left-aligned

        cards_layout.addStretch()  # Add stretch to push cards to left
        layout.addLayout(cards_layout)
        return section

    def _create_grid_layout_section(self):
        """Demonstrate grid layout functionality."""
        section, layout = self._create_section_frame("Grid Layout")

        # Grid Card
        grid_card = Card()
        grid_card.addLayout("grid", spacing=10)

        # Add widgets to grid positions
        grid_card.addWidget(QLabel("Name:"), 0, 0)
        name_field = QLineEdit("John Doe")
        grid_card.addWidget(name_field, 0, 1)

        grid_card.addWidget(QLabel("Email:"), 1, 0)
        email_field = QLineEdit("john@example.com")
        grid_card.addWidget(email_field, 1, 1)

        grid_card.addWidget(QLabel("Phone:"), 2, 0)
        phone_field = QLineEdit("+1234567890")
        grid_card.addWidget(phone_field, 2, 1)

        # Span across columns
        save_btn = QPushButton("Save Information")
        save_btn.clicked.connect(lambda: self.widget_event.emit("form_save", {
            "name": name_field.text(),
            "email": email_field.text(),
            "phone": phone_field.text()
        }))
        grid_card.addWidget(save_btn, 3, 0, 1, 2)  # row=3, col=0, rowspan=1, colspan=2

        layout.addWidget(grid_card)
        return section

    def _create_sizing_section(self):
        """Demonstrate sizing behavior and expansion options."""
        section, layout = self._create_section_frame("Card Sizing & Expansion")

        # Description
        desc = QLabel("Cards now size to their contents by default. Use expansion methods to control growth behavior.")
        desc.setStyleSheet("color: #666; font-style: italic; margin-bottom: 15px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Row 1: Default sizing behavior
        row1_frame = QFrame()
        row1_layout = QHBoxLayout(row1_frame)
        row1_layout.setSpacing(15)

        # Small content card
        small_card = Card()
        small_card.addLayout("vbox")
        small_card.addWidget(QLabel("Small Card"))
        small_card.addWidget(QPushButton("Button"))
        row1_layout.addWidget(small_card, 0, Qt.AlignLeft)

        # Medium content card
        medium_card = Card()
        medium_card.addLayout("vbox")
        medium_card.addWidget(QLabel("Medium Content Card"))
        medium_card.addWidget(QLabel("This card has more content\nto demonstrate size-to-contents behavior"))
        medium_card.addWidget(QPushButton("Action Button"))
        row1_layout.addWidget(medium_card, 0, Qt.AlignLeft)

        # Large content card
        large_card = Card()
        large_card.addLayout("vbox")
        large_card.addWidget(QLabel("Large Content Card"))
        desc_text = QTextEdit()
        desc_text.setPlainText("This card contains a text area with more substantial content to show how cards automatically size to their contents without expanding unnecessarily.")
        desc_text.setMaximumHeight(100)
        large_card.addWidget(desc_text)
        large_card.addWidget(QPushButton("Process"))
        row1_layout.addWidget(large_card, 0, Qt.AlignLeft)

        row1_layout.addStretch()  # Push cards to left
        layout.addWidget(row1_frame)

        # Row 2: Expansion demonstration
        row2_frame = QFrame()
        row2_layout = QVBoxLayout(row2_frame)
        row2_layout.setSpacing(10)

        # Expansion controls label
        exp_label = QLabel("Expansion Controls:")
        exp_label.setStyleSheet("font-weight: bold; margin-top: 15px;")
        row2_layout.addWidget(exp_label)

        # Container for expansion cards
        exp_container = QHBoxLayout()
        exp_container.setSpacing(15)

        # Width expansion card
        width_card = Card()
        width_card.addLayout("vbox")
        width_card.addWidget(QLabel("Width Expansion"))

        expand_width_btn = QPushButton("Expand Width")
        expand_width_btn.clicked.connect(lambda: self._toggle_width_expansion(width_card, expand_width_btn))
        width_card.addWidget(expand_width_btn)

        exp_container.addWidget(width_card, 0, Qt.AlignLeft)

        # Height expansion card
        height_card = Card()
        height_card.addLayout("vbox")
        height_card.addWidget(QLabel("Height Expansion"))

        expand_height_btn = QPushButton("Expand Height")
        expand_height_btn.clicked.connect(lambda: self._toggle_height_expansion(height_card, expand_height_btn))
        height_card.addWidget(expand_height_btn)

        exp_container.addWidget(height_card, 0, Qt.AlignLeft)

        # Both expansion card
        both_card = Card()
        both_card.addLayout("vbox")
        both_card.addWidget(QLabel("Both Directions"))

        expand_both_btn = QPushButton("Expand Both")
        expand_both_btn.clicked.connect(lambda: self._toggle_both_expansion(both_card, expand_both_btn))
        both_card.addWidget(expand_both_btn)

        exp_container.addWidget(both_card, 0, Qt.AlignLeft)

        exp_container.addStretch()
        row2_layout.addLayout(exp_container)

        layout.addWidget(row2_frame)
        return section

    def _toggle_width_expansion(self, card: Card, button: QPushButton):
        """Toggle width expansion for a card."""
        if "Expand" in button.text():
            card.expandWidth(True)
            button.setText("Contract Width")
            self.widget_event.emit("size_change", {"type": "width_expand", "card": "width_card"})
        else:
            card.expandWidth(False)
            button.setText("Expand Width")
            self.widget_event.emit("size_change", {"type": "width_contract", "card": "width_card"})

    def _toggle_height_expansion(self, card: Card, button: QPushButton):
        """Toggle height expansion for a card."""
        if "Expand" in button.text():
            card.expandHeight(True)
            button.setText("Contract Height")
            self.widget_event.emit("size_change", {"type": "height_expand", "card": "height_card"})
        else:
            card.expandHeight(False)
            button.setText("Expand Height")
            self.widget_event.emit("size_change", {"type": "height_contract", "card": "height_card"})

    def _toggle_both_expansion(self, card: Card, button: QPushButton):
        """Toggle both width and height expansion for a card."""
        if "Expand" in button.text():
            card.expandBoth(True)
            button.setText("Contract Both")
            self.widget_event.emit("size_change", {"type": "both_expand", "card": "both_card"})
        else:
            card.expandBoth(False)
            button.setText("Expand Both")
            self.widget_event.emit("size_change", {"type": "both_contract", "card": "both_card"})

    def _create_elevation_section(self):
        """Demonstrate different elevation effects."""
        section, layout = self._create_section_frame("Elevation Effects")

        # Container for elevation cards
        elevation_layout = QHBoxLayout()
        elevation_layout.setSpacing(15)

        elevations = [
            (Shadow.ELEVATION_0, "No Shadow"),
            (Shadow.ELEVATION_1, "Subtle"),
            (Shadow.ELEVATION_3, "Medium"),
            (Shadow.ELEVATION_6, "Strong"),
            (Shadow.ELEVATION_12, "Heavy")
        ]

        for elevation, name in elevations:
            card = Card(elevation=elevation)
            card.addLayout("vbox")

            title_label = QLabel(name)
            title_label.setStyleSheet("font-weight: bold; font-size: 11px;")
            card.addWidget(title_label)

            desc_label = QLabel(f"Elevation: {elevation.name}")
            desc_label.setStyleSheet("font-size: 10px; color: #666;")
            card.addWidget(desc_label)

            test_btn = QPushButton("Test")
            test_btn.clicked.connect(lambda checked, e=elevation: self.widget_event.emit("elevation_test", {"elevation": e.name}))
            card.addWidget(test_btn)

            elevation_layout.addWidget(card, 0, Qt.AlignLeft)  # No stretch, left-aligned

        elevation_layout.addStretch()  # Add stretch to push cards to left
        layout.addLayout(elevation_layout)

        # Disabled elevation card
        disabled_frame = QFrame()
        disabled_layout = QHBoxLayout(disabled_frame)
        disabled_layout.setContentsMargins(0, 10, 0, 0)

        disabled_card = Card()
        disabled_card.enableElevation(False)
        disabled_card.addLayout("vbox")
        disabled_card.addWidget(QLabel("Elevation Disabled"))
        disabled_card.addWidget(QLabel("No shadow effect"))

        toggle_btn = QPushButton("Toggle Elevation")
        toggle_btn.clicked.connect(lambda: self._toggle_card_elevation(disabled_card, toggle_btn))
        disabled_card.addWidget(toggle_btn)

        disabled_layout.addWidget(disabled_card)
        disabled_layout.addStretch()

        layout.addWidget(disabled_frame)
        return section

    def _create_content_margins_section(self):
        """Demonstrate content margin customization."""
        section, layout = self._create_section_frame("Content Margins Customization")

        # Container for margin cards
        margin_layout = QHBoxLayout()
        margin_layout.setSpacing(15)

        # Default margins (20,20,20,20)
        default_card = Card()
        default_card.addLayout("vbox")
        default_card.addWidget(QLabel("Default Margins"))
        default_card.addWidget(QLabel("20px all sides"))
        default_card.addWidget(QPushButton("Button"))

        margin_layout.addWidget(default_card, 0, Qt.AlignLeft)

        # Custom margins (40,10,40,10)
        custom_card = Card()
        custom_card.addLayout("vbox")
        custom_card.setContentMargins(40, 10, 40, 10)
        custom_card.addWidget(QLabel("Custom Margins"))
        custom_card.addWidget(QLabel("40px left/right\n10px top/bottom"))
        custom_card.addWidget(QPushButton("Button"))

        margin_layout.addWidget(custom_card, 0, Qt.AlignLeft)

        # Minimal margins (5,5,5,5)
        minimal_card = Card()
        minimal_card.addLayout("vbox")
        minimal_card.setContentMargins(5, 5, 5, 5)
        minimal_card.addWidget(QLabel("Minimal Margins"))
        minimal_card.addWidget(QLabel("5px all sides"))
        minimal_card.addWidget(QPushButton("Button"))

        margin_layout.addWidget(minimal_card, 0, Qt.AlignLeft)

        margin_layout.addStretch()  # Add stretch to push cards to left
        layout.addLayout(margin_layout)
        return section

    def _create_interactive_section(self):
        """Demonstrate interactive features and advanced usage."""
        section, layout = self._create_section_frame("Interactive Features & Advanced Usage")

        # Create an interactive card
        interactive_card = Card(elevation=Shadow.ELEVATION_6)
        interactive_card.addLayout("vbox", spacing=15)

        # Description
        desc = QLabel("This card demonstrates dynamic interaction with the Card widget API. "
                     "Use the controls below to modify the card in real-time.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #666; font-style: italic; margin-bottom: 10px;")
        interactive_card.addWidget(desc)

        # Content counter
        self.content_counter = 0
        self.counter_label = QLabel(f"Dynamic widgets added: {self.content_counter}")
        interactive_card.addWidget(self.counter_label)

        # Control buttons
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(10)

        add_btn = QPushButton("Add Widget")
        add_btn.clicked.connect(lambda: self._add_dynamic_widget(interactive_card))
        button_layout.addWidget(add_btn)

        clear_btn = QPushButton("Clear Content")
        clear_btn.clicked.connect(lambda: self._clear_card_content(interactive_card))
        button_layout.addWidget(clear_btn)

        layout_btn = QPushButton("Switch to HBox")
        layout_btn.clicked.connect(lambda: self._switch_card_layout(interactive_card, layout_btn))
        button_layout.addWidget(layout_btn)

        button_layout.addStretch()

        interactive_card.addWidget(button_frame)

        # Store reference for dynamic operations
        self.interactive_card = interactive_card
        self.layout_btn = layout_btn
        self.current_layout = "vbox"

        layout.addWidget(interactive_card)
        return section

    def _toggle_card_elevation(self, card: Card, button: QPushButton):
        """Toggle elevation on/off for a card."""
        # This is a simple toggle - in real usage you might want to track state
        card.setElevation(Shadow.ELEVATION_3)
        button.setText("Elevation Applied")
        button.setEnabled(False)
        self.widget_event.emit("elevation_toggle", {"status": "enabled"})

    def _add_dynamic_widget(self, card: Card):
        """Add a dynamic widget to the card."""
        self.content_counter += 1
        new_label = QLabel(f"Dynamic item #{self.content_counter}")
        new_label.setStyleSheet("background-color: rgba(100, 149, 237, 0.1); padding: 5px; border-radius: 3px;")

        # Insert before the last widget (button frame)
        layout = card.getLayout()
        if layout and layout.count() > 0:
            # Remove the last item (button frame), add new widget, then add button frame back
            last_item = layout.takeAt(layout.count() - 1)
            card.addWidget(new_label)
            if last_item and last_item.widget():
                layout.addWidget(last_item.widget())

        self.counter_label.setText(f"Dynamic widgets added: {self.content_counter}")
        self.widget_event.emit("widget_added", {"count": self.content_counter})

    def _clear_card_content(self, card: Card):
        """Clear dynamic content from the card."""
        # Recreate the card content
        card.clearWidgets()
        card.addLayout(self.current_layout, spacing=15)

        # Re-add static content
        desc = QLabel("Content cleared! This card demonstrates dynamic interaction with the Card widget API.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #666; font-style: italic; margin-bottom: 10px;")
        card.addWidget(desc)

        self.content_counter = 0
        self.counter_label = QLabel(f"Dynamic widgets added: {self.content_counter}")
        card.addWidget(self.counter_label)

        # Re-add button frame
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(10)

        add_btn = QPushButton("Add Widget")
        add_btn.clicked.connect(lambda: self._add_dynamic_widget(card))
        button_layout.addWidget(add_btn)

        clear_btn = QPushButton("Clear Content")
        clear_btn.clicked.connect(lambda: self._clear_card_content(card))
        button_layout.addWidget(clear_btn)

        layout_btn = QPushButton("Switch to HBox")
        layout_btn.clicked.connect(lambda: self._switch_card_layout(card, layout_btn))
        button_layout.addWidget(layout_btn)

        button_layout.addStretch()

        card.addWidget(button_frame)

        self.layout_btn = layout_btn
        self.widget_event.emit("content_cleared", {})

    def _switch_card_layout(self, card: Card, button: QPushButton):
        """Switch between VBox and HBox layouts."""
        new_layout = "hbox" if self.current_layout == "vbox" else "vbox"
        self.current_layout = new_layout

        # This is a simplified version - in practice you might want to preserve content
        card.addLayout(new_layout, spacing=15)

        switch_text = "Switch to VBox" if new_layout == "hbox" else "Switch to HBox"
        button.setText(switch_text)

        # Add a simple indicator
        indicator = QLabel(f"Layout switched to: {new_layout.upper()}")
        indicator.setStyleSheet("color: green; font-weight: bold;")
        card.addWidget(indicator)

        self.widget_event.emit("layout_switched", {"new_layout": new_layout})


class ThemeControlBar(QFrame):
    """Header bar with theme controls."""

    color_changed = Signal(Color)
    mode_toggled = Signal(str)  # "light" or "dark"
    reset_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ThemeControlBar")
        self.setFixedHeight(60)

        # Apply subtle styling
        self.setStyleSheet("""
            QFrame#ThemeControlBar {
                background-color: rgba(0, 0, 0, 0.03);
                border-bottom: 1px solid rgba(0, 0, 0, 0.1);
            }
        """)

        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(20)

        # Title
        title = QLabel("Card Widget Test")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        layout.addStretch()

        # Color enum combobox
        color_label = QLabel("Theme Color:")
        self.color_combo = ComboBox(
            parent=self,
            list_items=[color.name for color in Color],
            placeholder="Select color..."
        )
        self.color_combo.currentTextChanged.connect(self._on_color_selection)

        # Light/Dark toggle
        mode_label = QLabel("Dark Mode:")
        self.mode_toggle = ToggleSwitch(parent=self, checked=False)
        self.mode_toggle.toggled.connect(self._on_mode_toggle)

        # Reset button
        self.reset_button = Button("Reset", Type.SECONDARY, Name.REFRESH)
        self.reset_button.clicked.connect(self.reset_requested.emit)

        # Add widgets to layout
        layout.addWidget(color_label)
        layout.addWidget(self.color_combo)
        layout.addWidget(mode_label)
        layout.addWidget(self.mode_toggle)
        layout.addWidget(self.reset_button)

    def _on_color_selection(self, color_name: str):
        """Handle color combo selection."""
        if color_name:
            try:
                color_enum = Color[color_name]
                self.color_changed.emit(color_enum)
            except KeyError:
                pass  # Invalid selection, ignore

    def _on_mode_toggle(self, is_dark: bool):
        """Handle mode toggle."""
        mode = "dark" if is_dark else "light"
        self.mode_toggled.emit(mode)

    def set_color_selection(self, color: Color):
        """Update color combo to reflect current selection."""
        if color:
            self.color_combo.setCurrentText(color.name)

    def set_mode_selection(self, mode: Mode):
        """Update toggle to reflect current mode."""
        if mode:
            self.mode_toggle.setChecked(mode == Mode.DARK)


class CardFunctionalityTest(QMainWindow):
    """Main test window for Card widget functionality."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Card Widget Functionality Test")
        self.setMinimumSize(1200, 800)

        # Initialize theme manager
        self.theme_manager = ThemeManager()
        self.theme_manager.theme_changed.connect(self._on_theme_changed)

        # Setup UI
        self._setup_ui()
        self._connect_signals()

        # Initialize with current theme state
        QTimer.singleShot(100, self._initialize_theme_state)

        # Welcome message
        self.logger.log_message("Card Widget Functionality Test initialized", "info")

    def _setup_ui(self):
        """Setup the three-zone layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main vertical layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Theme Control Bar (Header) - Fixed
        self.control_bar = ThemeControlBar()
        main_layout.addWidget(self.control_bar)

        # 2. Main Content Area (Center) - Scrollable
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.content_area = CardContentArea()
        scroll_area.setWidget(self.content_area)
        main_layout.addWidget(scroll_area, 1)  # Takes expanding space

        # 3. Debug/Output Pane (Footer) - Fixed
        footer_frame = QFrame()
        footer_frame.setFixedHeight(200)
        footer_layout = QVBoxLayout(footer_frame)
        footer_layout.setContentsMargins(10, 5, 10, 10)

        footer_label = QLabel("Debug Output:")
        footer_label.setStyleSheet("font-weight: bold; color: #666;")
        footer_layout.addWidget(footer_label)

        self.logger = LoggingWidget()
        footer_layout.addWidget(self.logger)

        main_layout.addWidget(footer_frame)

    def _connect_signals(self):
        """Connect UI signals to handlers."""
        # Theme control signals
        self.control_bar.color_changed.connect(self._on_color_changed)
        self.control_bar.mode_toggled.connect(self._on_mode_toggled)
        self.control_bar.reset_requested.connect(self._on_reset_requested)

        # Content area widget events
        self.content_area.widget_event.connect(self._on_widget_event)

    def _initialize_theme_state(self):
        """Initialize theme state and UI controls."""
        # Capture startup defaults
        self.theme_manager.initialize_startup_state()

        # Update UI controls to match current state
        current_theme = self.theme_manager.get_current_theme()
        if current_theme['color']:
            self.control_bar.set_color_selection(current_theme['color'])
        if current_theme['mode']:
            self.control_bar.set_mode_selection(current_theme['mode'])

        self.logger.log_message(
            f"Startup defaults captured: {current_theme['color_name']} / {current_theme['mode_name']}",
            "info"
        )

    def _on_color_changed(self, color: Color):
        """Handle color selection change."""
        self.theme_manager.set_color(color)

    def _on_mode_toggled(self, mode: str):
        """Handle light/dark mode toggle."""
        self.theme_manager.set_mode(mode)

    def _on_reset_requested(self):
        """Handle reset button click."""
        self.theme_manager.reset_to_startup_defaults()

        # Update UI controls
        current_theme = self.theme_manager.get_current_theme()
        if current_theme['color']:
            self.control_bar.set_color_selection(current_theme['color'])
        if current_theme['mode']:
            self.control_bar.set_mode_selection(current_theme['mode'])

    def _on_theme_changed(self, change_info: Dict[str, Any]):
        """Handle theme change events from ThemeManager."""
        change_type = change_info['type']

        if change_type == 'color_change':
            message = f"Theme color changed: {change_info['old']} → {change_info['new']}"
        elif change_type == 'mode_change':
            message = f"Theme mode changed: {change_info['old']} → {change_info['new']}"
        elif change_type == 'reset':
            message = f"Theme reset to startup: {change_info['new_color']}/{change_info['new_mode']}"
        else:
            message = f"Theme change: {change_info}"

        self.logger.log_message(message, "event")

    def _on_widget_event(self, event_type: str, data: Dict[str, Any]):
        """Handle widget events from content area."""
        if event_type == "button_click":
            message = f"Button clicked in {data['section']} section: {data['button']}"
        elif event_type == "search":
            message = f"Search performed with query: '{data['query']}'"
        elif event_type == "form_save":
            message = f"Form saved - Name: {data['name']}, Email: {data['email']}, Phone: {data['phone']}"
        elif event_type == "elevation_test":
            message = f"Elevation test clicked: {data['elevation']}"
        elif event_type == "widget_added":
            message = f"Dynamic widget added (total: {data['count']})"
        elif event_type == "layout_switched":
            message = f"Card layout switched to: {data['new_layout']}"
        elif event_type == "size_change":
            message = f"Card size changed: {data['type']} for {data['card']}"
        else:
            message = f"Widget event: {event_type} - {data}"

        self.logger.log_message(message, "event")


def main():
    """Run the Card widget functionality test."""
    app = QApplication(sys.argv)

    # Set default theme if none exists
    try:
        current_color = Theme.get_current_theme_color()
        current_mode = Theme.get_current_theme_mode()
        if not current_color or not current_mode:
            Theme.setTheme(Color.BLUE, Mode.LIGHT)
    except:
        Theme.setTheme(Color.BLUE, Mode.LIGHT)

    # Create and show test window
    test_window = CardFunctionalityTest()
    test_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
