#!/usr/bin/env python3
"""
Comprehensive ToolButton Hover Effects Test

This standalone test app demonstrates the ToolButton hover effects using various
icons from the application's icon configuration. It's designed for easy debugging
and troubleshooting of hover state transitions.
"""

import sys
from pathlib import Path


# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QWidget, QLabel, QScrollArea, QFrame, QGroupBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from app.ui.components.widgets.button import ToolButton
from app.appearance.icon.config import Name, Type
from app.appearance import Theme
from app.appearance.config import Color, Mode


class HoverTestWidget(QFrame):
    """A test widget that displays a ToolButton with debug information."""

    def __init__(self, icon_name: Name, button_type: Type, title: str):
        super().__init__()
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(1)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Create the ToolButton
        self.button = ToolButton(icon_name, button_type)
        self.button.setMinimumSize(50, 50)

        # Center the button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Debug info labels
        self.state_label = QLabel("State: DEFAULT")
        self.state_label.setAlignment(Qt.AlignCenter)
        self.state_label.setFont(QFont("Courier", 8))
        layout.addWidget(self.state_label)

        self.color_label = QLabel("Color: -")
        self.color_label.setAlignment(Qt.AlignCenter)
        self.color_label.setFont(QFont("Courier", 8))
        layout.addWidget(self.color_label)

        # Connect hover tracking
        self.button.enterEvent = self._on_enter
        self.button.leaveEvent = self._on_leave

        # Timer to update debug info
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_debug_info)
        self.update_timer.start(100)  # Update every 100ms

        self._update_debug_info()

    def _on_enter(self, event):
        """Handle mouse enter event."""
        self.state_label.setText("State: HOVER")
        # Call the original enterEvent if it exists
        if hasattr(ToolButton, 'enterEvent'):
            ToolButton.enterEvent(self.button, event)

    def _on_leave(self, event):
        """Handle mouse leave event."""
        self.state_label.setText("State: DEFAULT")
        # Call the original leaveEvent if it exists
        if hasattr(ToolButton, 'leaveEvent'):
            ToolButton.leaveEvent(self.button, event)

    def _update_debug_info(self):
        """Update the debug information display."""
        try:
            # Get current state from the StateIcon
            if hasattr(self.button, '_state_icon') and hasattr(self.button._state_icon, '_current_state'):
                current_state = self.button._state_icon._current_state
                self.state_label.setText(f"State: {current_state.name}")

                # Get the current color
                if hasattr(self.button._state_icon, '_current_color'):
                    current_color = self.button._state_icon._current_color
                    self.color_label.setText(f"Color: {current_color}")
                else:
                    self.color_label.setText("Color: N/A")
            else:
                # Fallback: detect state based on mouse position
                if self.button.underMouse():
                    self.state_label.setText("State: HOVER (detected)")
                else:
                    self.state_label.setText("State: DEFAULT (detected)")
        except Exception as e:
            self.color_label.setText(f"Error: {str(e)[:20]}...")


class ToolButtonHoverTest(QMainWindow):
    """Main test window for ToolButton hover effects."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ToolButton Hover Effects Test")
        self.setGeometry(100, 100, 1000, 800)

        # Create central widget with scroll area
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("ToolButton Hover Effects Test")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Instructions
        instructions = QLabel(
            "Hover over the buttons below to test hover effects. "
            "Each button shows its current state and color information."
        )
        instructions.setWordWrap(True)
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("color: gray; margin: 10px;")
        main_layout.addWidget(instructions)

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        main_layout.addWidget(scroll_area)

        # Create content widget
        content_widget = QWidget()
        scroll_area.setWidget(content_widget)
        content_layout = QVBoxLayout(content_widget)

        # Create test groups
        self._create_button_type_tests(content_layout)

        # Add stretch at the end
        content_layout.addStretch()

    def _create_button_type_tests(self, parent_layout):
        """Create test groups for different button types."""

        # Test different button types with various icons
        test_configs = [
            (Type.DEFAULT, "Default Buttons", [
                Name.ADD, Name.EDIT, Name.SAVE, Name.REFRESH, Name.SEARCH
            ]),
            (Type.PRIMARY, "Primary Buttons", [
                Name.HEART, Name.HEART_FILLED, Name.LIGHTBULB, Name.USER
            ]),
            (Type.SECONDARY, "Secondary Buttons", [
                Name.SETTINGS, Name.MENU, Name.EXIT, Name.MINIMIZE, Name.MAXIMIZE
            ]),
            (Type.TITLEBAR, "Titlebar Buttons", [
                Name.MINIMIZE, Name.MAXIMIZE, Name.RESTORE, Name.CROSS
            ])
        ]

        for button_type, group_title, icons in test_configs:
            group_box = QGroupBox(group_title)
            group_box.setFont(QFont("Arial", 12, QFont.Bold))
            parent_layout.addWidget(group_box)

            group_layout = QHBoxLayout(group_box)
            group_layout.setSpacing(15)

            for icon_name in icons:
                test_widget = HoverTestWidget(
                    icon_name,
                    button_type,
                    f"{icon_name.name}\n({button_type.value})"
                )
                group_layout.addWidget(test_widget)

            # Add stretch to center the buttons if there are fewer than expected
            group_layout.addStretch()

        # Add a special section for large icons
        large_group = QGroupBox("Large Icons Test")
        large_group.setFont(QFont("Arial", 12, QFont.Bold))
        parent_layout.addWidget(large_group)

        large_layout = QHBoxLayout(large_group)
        large_layout.setSpacing(15)

        large_icons = [Name.ADD_RECIPES, Name.DASHBOARD, Name.MEAL_PLANNER, Name.VIEW_RECIPES]
        for icon_name in large_icons:
            test_widget = HoverTestWidget(
                icon_name,
                Type.PRIMARY,
                f"{icon_name.name}\n(Large)"
            )
            large_layout.addWidget(test_widget)

        large_layout.addStretch()


def main():
    """Run the ToolButton hover test application."""
    app = QApplication(sys.argv)

    Theme.setTheme(Color.GREEN, Mode.DARK)

    # Set application properties
    app.setApplicationName("ToolButton Hover Test")
    app.setApplicationVersion("1.0")

    try:
        # Create and show the main window
        window = ToolButtonHoverTest()
        window.show()

        # Run the application
        sys.exit(app.exec())

    except Exception as e:
        print(f"Error running test application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
