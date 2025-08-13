"""
PySide6 Theme Playground Test Harness

A reusable test environment for theme development and UI component testing.
Provides a persistent theme control bar, scrollable content area, and debug output pane.

Usage:
    python tests/theme_playground.py

Features:
- Three-zone layout: fixed header, scrollable content, fixed footer
- Real-time theme switching with Color enum and Light/Dark toggle
- Reset functionality to restore startup defaults
- Comprehensive event logging for debugging
- Ready-to-use template for future UI tests
"""

import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, Signal, QObject
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QScrollArea, QFrame, QLabel, QPlainTextEdit, QSizePolicy
)
from PySide6.QtGui import QFont

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.ui.components.widgets.combobox import ComboBox
from app.ui.components.widgets.toggle_switch import ToggleSwitch
from app.ui.components.widgets.button import Button
from app.style.theme.config import Color, Mode
from app.style.theme_controller import Theme
from app.style.icon.config import Name, Type


class ThemeManager(QObject):
    """Minimal theme manager for the playground."""

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


class MainContentArea(QFrame):
    """Main content area with mouse event tracking."""

    mouse_event = Signal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MainContentArea")

        # Setup layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Placeholder content
        placeholder = QLabel("Drop tests here")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #888888;
                background-color: rgba(0, 0, 0, 0.05);
                border: 2px dashed #cccccc;
                border-radius: 8px;
                padding: 40px;
                margin: 20px;
            }
        """)
        layout.addWidget(placeholder)
        layout.addStretch()

        # Enable mouse tracking
        self.setMouseTracking(True)

    def enterEvent(self, event):
        """Track mouse enter events."""
        self.mouse_event.emit("enter", {"widget": "MainContentArea"})
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Track mouse leave events."""
        self.mouse_event.emit("leave", {"widget": "MainContentArea"})
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Track mouse click events."""
        self.mouse_event.emit("click", {
            "widget": "MainContentArea",
            "button": event.button().name,
            "pos": f"({event.pos().x()}, {event.pos().y()})"
        })
        super().mousePressEvent(event)


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
        layout.addStretch()  # Push everything to the left

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


class ThemePlayground(QMainWindow):
    """Main theme playground window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Theme Playground")
        self.setMinimumSize(1000, 700)

        # Initialize theme manager
        self.theme_manager = ThemeManager()
        self.theme_manager.theme_changed.connect(self._on_theme_changed)

        # Setup UI
        self._setup_ui()
        self._connect_signals()

        # Initialize with current theme state
        QTimer.singleShot(100, self._initialize_theme_state)

        # Welcome message
        self.logger.log_message("Theme Playground initialized", "info")

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

        self.content_area = MainContentArea()
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

        # Content area mouse events
        self.content_area.mouse_event.connect(self._on_mouse_event)

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
            message = f"Color changed: {change_info['old']} → {change_info['new']}"
        elif change_type == 'mode_change':
            message = f"Mode changed: {change_info['old']} → {change_info['new']}"
        elif change_type == 'reset':
            message = f"Reset to startup: {change_info['new_color']}/{change_info['new_mode']}"
        else:
            message = f"Theme change: {change_info}"

        self.logger.log_message(message, "event")

    def _on_mouse_event(self, event_type: str, data: Dict[str, Any]):
        """Handle mouse events from content area."""
        if event_type == "click":
            message = f"Mouse {event_type} on {data['widget']} - {data['button']} at {data['pos']}"
        else:
            message = f"Mouse {event_type} on {data['widget']}"

        self.logger.log_message(message, "event")


# Helper functions for external use
def log_info(message: str):
    """Helper function to log info messages (if playground is running)."""
    # This would need to be connected to the active playground instance
    print(f"INFO: {message}")

def log_event(event: str, payload=""):
    """Helper function to log events (if playground is running)."""
    # This would need to be connected to the active playground instance
    print(f"EVENT: {event} - {payload}")


def main():
    """Run the theme playground as a standalone application."""
    app = QApplication(sys.argv)

    # Set default theme if none exists
    try:
        current_color = Theme.get_current_theme_color()
        current_mode = Theme.get_current_theme_mode()
        if not current_color or not current_mode:
            Theme.setTheme(Color.BLUE, Mode.LIGHT)
    except:
        Theme.setTheme(Color.BLUE, Mode.LIGHT)

    # Create and show playground
    playground = ThemePlayground()
    playground.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
