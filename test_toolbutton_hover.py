#!/usr/bin/env python3
"""
Standalone ToolButton Hover Test App

Simple test application to troubleshoot ToolButton hover effects.
This app creates various ToolButton configurations to help debug hover state issues.
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLabel, QPushButton, QCheckBox, QSpinBox
)
from PySide6.QtCore import Qt

# Import your ToolButton and related classes
try:
    from app.ui.components.widgets.button import ToolButton
    from app.appearance.icon.config import Name, Type
    from app.appearance.theme import Theme
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the recipe_app directory")
    sys.exit(1)


class ToolButtonHoverTestWindow(QMainWindow):
    """Main test window for ToolButton hover effects."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ToolButton Hover Test")
        self.setGeometry(100, 100, 800, 600)

        # Initialize theme
        try:
            Theme.initialize()
        except Exception as e:
            print(f"Theme initialization warning: {e}")

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Add title
        title = QLabel("ToolButton Hover Effect Test")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Add instructions
        instructions = QLabel(
            "Move your mouse over the buttons to test hover effects.\n"
            "Watch the console for debug output and hover state changes."
        )
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("margin: 10px; color: gray;")
        main_layout.addWidget(instructions)

        # Create test sections
        self.create_basic_hover_test(main_layout)
        self.create_different_types_test(main_layout)
        self.create_checkable_test(main_layout)
        self.create_size_test(main_layout)
        self.create_state_override_test(main_layout)
        self.create_debug_controls(main_layout)

    def create_basic_hover_test(self, parent_layout):
        """Create basic hover test section."""
        group = QGroupBox("Basic Hover Test")
        layout = QHBoxLayout(group)

        # Simple ToolButton with different icons
        self.basic_button1 = DebugToolButton(Name.HEART, Type.DEFAULT)
        self.basic_button2 = DebugToolButton(Name.STAR, Type.DEFAULT)
        self.basic_button3 = DebugToolButton(Name.LIGHTBULB, Type.DEFAULT)

        layout.addWidget(QLabel("Default Icons:"))
        layout.addWidget(self.basic_button1)
        layout.addWidget(self.basic_button2)
        layout.addWidget(self.basic_button3)
        layout.addStretch()

        parent_layout.addWidget(group)

    def create_different_types_test(self, parent_layout):
        """Create test for different button types."""
        group = QGroupBox("Different Button Types")
        layout = QHBoxLayout(group)

        # Different button types
        self.type_default = DebugToolButton(Name.INFO, Type.DEFAULT)
        self.type_primary = DebugToolButton(Name.INFO, Type.PRIMARY)
        self.type_secondary = DebugToolButton(Name.INFO, Type.SECONDARY)
        self.type_titlebar = DebugToolButton(Name.INFO, Type.TITLEBAR)

        layout.addWidget(QLabel("Types:"))
        layout.addWidget(QLabel("Default"))
        layout.addWidget(self.type_default)
        layout.addWidget(QLabel("Primary"))
        layout.addWidget(self.type_primary)
        layout.addWidget(QLabel("Secondary"))
        layout.addWidget(self.type_secondary)
        layout.addWidget(QLabel("Titlebar"))
        layout.addWidget(self.type_titlebar)
        layout.addStretch()

        parent_layout.addWidget(group)

    def create_checkable_test(self, parent_layout):
        """Create checkable button test section."""
        group = QGroupBox("Checkable Buttons")
        layout = QHBoxLayout(group)

        # Checkable buttons
        self.checkable1 = DebugToolButton(Name.BOOKMARK, Type.DEFAULT)
        self.checkable1.setCheckable(True)

        self.checkable2 = DebugToolButton(Name.FAVORITE, Type.PRIMARY)
        self.checkable2.setCheckable(True)

        self.checkable3 = DebugToolButton(Name.TOGGLE_ON, Type.SECONDARY)
        self.checkable3.setCheckable(True)

        layout.addWidget(QLabel("Checkable (click to toggle):"))
        layout.addWidget(self.checkable1)
        layout.addWidget(self.checkable2)
        layout.addWidget(self.checkable3)
        layout.addStretch()

        parent_layout.addWidget(group)

    def create_size_test(self, parent_layout):
        """Create size test section."""
        group = QGroupBox("Size Tests")
        layout = QVBoxLayout(group)

        # Size controls
        size_controls = QHBoxLayout()
        size_controls.addWidget(QLabel("Icon Size:"))

        self.icon_size_spinbox = QSpinBox()
        self.icon_size_spinbox.setRange(12, 64)
        self.icon_size_spinbox.setValue(24)
        self.icon_size_spinbox.valueChanged.connect(self.update_dynamic_icon_size)
        size_controls.addWidget(self.icon_size_spinbox)

        # Dynamic size button
        self.dynamic_size_button = DebugToolButton(Name.SETTINGS, Type.DEFAULT)
        size_controls.addWidget(self.dynamic_size_button)
        size_controls.addStretch()

        layout.addLayout(size_controls)

        # Fixed size buttons
        fixed_size_row = QHBoxLayout()
        fixed_size_row.addWidget(QLabel("Fixed Sizes:"))

        self.small_button = DebugToolButton(Name.CLOSE, Type.DEFAULT)
        self.small_button.setIconSize(16, 16)

        self.medium_button = DebugToolButton(Name.CLOSE, Type.DEFAULT)
        self.medium_button.setIconSize(32, 32)

        self.large_button = DebugToolButton(Name.CLOSE, Type.DEFAULT)
        self.large_button.setIconSize(48, 48)

        fixed_size_row.addWidget(QLabel("16px"))
        fixed_size_row.addWidget(self.small_button)
        fixed_size_row.addWidget(QLabel("32px"))
        fixed_size_row.addWidget(self.medium_button)
        fixed_size_row.addWidget(QLabel("48px"))
        fixed_size_row.addWidget(self.large_button)
        fixed_size_row.addStretch()

        layout.addLayout(fixed_size_row)
        parent_layout.addWidget(group)

    def create_state_override_test(self, parent_layout):
        """Create state override test section."""
        group = QGroupBox("State Color Overrides")
        layout = QHBoxLayout(group)

        # Buttons with custom state colors
        self.override1 = DebugToolButton(Name.PALETTE, Type.DEFAULT)
        self.override1.setCheckable(True)
        self.override1.setStateDefault("text")
        self.override1.setStateHover("primary")
        self.override1.setStateChecked("tertiary")

        self.override2 = DebugToolButton(Name.BRUSH, Type.DEFAULT)
        self.override2.setCheckable(True)
        self.override2.setStateDefault("secondary")
        self.override2.setStateHover("error")
        self.override2.setStateChecked("success")

        layout.addWidget(QLabel("Custom State Colors:"))
        layout.addWidget(self.override1)
        layout.addWidget(self.override2)
        layout.addStretch()

        parent_layout.addWidget(group)

    def create_debug_controls(self, parent_layout):
        """Create debug controls section."""
        group = QGroupBox("Debug Controls")
        layout = QHBoxLayout(group)

        # Debug output toggle
        self.debug_checkbox = QCheckBox("Verbose Debug Output")
        self.debug_checkbox.setChecked(True)
        self.debug_checkbox.toggled.connect(self.toggle_debug_output)
        layout.addWidget(self.debug_checkbox)

        # Clear console button
        clear_btn = QPushButton("Clear Console")
        clear_btn.clicked.connect(lambda: print("\n" + "="*50 + "\n"))
        layout.addWidget(clear_btn)

        # Theme test button
        refresh_btn = QPushButton("Force Theme Refresh")
        refresh_btn.clicked.connect(self.force_theme_refresh)
        layout.addWidget(refresh_btn)

        layout.addStretch()
        parent_layout.addWidget(group)

    def update_dynamic_icon_size(self, size):
        """Update the dynamic size button's icon size."""
        self.dynamic_size_button.setIconSize(size, size)
        print(f"Updated dynamic button icon size to {size}x{size}")

    def toggle_debug_output(self, enabled):
        """Toggle debug output for all debug buttons."""
        DebugToolButton.DEBUG_ENABLED = enabled
        print(f"Debug output {'enabled' if enabled else 'disabled'}")

    def force_theme_refresh(self):
        """Force a theme refresh to test theme changes."""
        try:
            Theme.refresh()
            print("Theme refreshed successfully")
        except Exception as e:
            print(f"Theme refresh error: {e}")


class DebugToolButton(ToolButton):
    """ToolButton subclass with debug output for hover events."""

    DEBUG_ENABLED = True

    def __init__(self, icon: Name, type: Type = Type.DEFAULT, parent=None):
        super().__init__(icon, type, parent)
        self.icon_name = icon
        self.button_type = type
        self._hover_count = 0
        self._leave_count = 0

        # Add debug info as tooltip
        self.setToolTip(f"Icon: {icon.name}, Type: {type.name}")

        if self.DEBUG_ENABLED:
            print(f"Created DebugToolButton: {icon.name} ({type.name})")

    def enterEvent(self, event):
        """Override enterEvent to add debug output."""
        self._hover_count += 1
        if self.DEBUG_ENABLED:
            print(f"🖱️  HOVER ENTER #{self._hover_count}: {self.icon_name.name} "
                  f"(checked={self.isChecked()}, enabled={self.isEnabled()})")

        super().enterEvent(event)

        if self.DEBUG_ENABLED:
            print(f"   → State after enterEvent: {self.state_icon._current_state if self.state_icon else 'None'}")

    def leaveEvent(self, event):
        """Override leaveEvent to add debug output."""
        self._leave_count += 1
        if self.DEBUG_ENABLED:
            print(f"🖱️  HOVER LEAVE #{self._leave_count}: {self.icon_name.name} "
                  f"(checked={self.isChecked()}, enabled={self.isEnabled()})")

        super().leaveEvent(event)

        if self.DEBUG_ENABLED:
            print(f"   → State after leaveEvent: {self.state_icon._current_state if self.state_icon else 'None'}")

    def mousePressEvent(self, event):
        """Override mousePressEvent to add debug output."""
        if self.DEBUG_ENABLED:
            print(f"🖱️  CLICK: {self.icon_name.name}")
        super().mousePressEvent(event)

    def changeEvent(self, event):
        """Override changeEvent to add debug output."""
        if self.DEBUG_ENABLED and event.type() == event.Type.EnabledChange:
            print(f"🔄 ENABLED CHANGE: {self.icon_name.name} → enabled={self.isEnabled()}")
        super().changeEvent(event)


def main():
    """Main function to run the test application."""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("ToolButton Hover Test")
    app.setApplicationVersion("1.0")

    print("="*60)
    print("ToolButton Hover Effects Test Application")
    print("="*60)
    print("Instructions:")
    print("1. Move your mouse over the buttons to test hover effects")
    print("2. Click checkable buttons to test checked states")
    print("3. Adjust sizes to test different configurations")
    print("4. Watch console output for state change debug info")
    print("="*60)

    # Create and show main window
    window = ToolButtonHoverTestWindow()
    window.show()

    # Run the application
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
