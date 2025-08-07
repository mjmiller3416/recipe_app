"""test_button_system.py

Enhanced test file for the new button system (Phase 2).
Tests BaseButton, Button, and ToolButton classes in isolation.
"""

import sys
from pathlib import Path

# Add the app directory to the Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir.parent))

from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QCheckBox, QSpinBox, QGroupBox,
                               QScrollArea)
from PySide6.QtCore import Qt, QTimer

from app.ui.components.widgets.button import Button, ToolButton
from app.style.icon.config import Name, Type, State
from app.style.theme_controller import Theme
from app.style.theme.config import Color, Mode


class ButtonTestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Button System Test - Phase 2")
        self.setMinimumSize(1200, 900)

        # Create scroll area for the main content
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Create the main content widget
        content_widget = QWidget()
        main_layout = QVBoxLayout(content_widget)

        # Set the content widget in the scroll area
        scroll_area.setWidget(content_widget)

        # Set the scroll area as the main layout of the window
        window_layout = QVBoxLayout(self)
        window_layout.addWidget(scroll_area)

        # === BASIC BUTTON TESTS ===
        basic_group = QGroupBox("Basic Button Tests")
        basic_layout = QVBoxLayout(basic_group)

        # Test Button widgets with icons and labels
        basic_layout.addWidget(QLabel("Button widgets (icon + label):"))
        button_row = QHBoxLayout()

        self.btn_dashboard = Button("Dashboard", Type.PRIMARY, Name.DASHBOARD)
        self.btn_settings = Button("Settings", Type.PRIMARY, Name.SETTINGS)
        self.btn_exit = Button("Exit", Type.PRIMARY, Name.EXIT)
        self.btn_no_icon = Button("No Icon", Type.PRIMARY)

        button_row.addWidget(self.btn_dashboard)
        button_row.addWidget(self.btn_settings)
        button_row.addWidget(self.btn_exit)
        button_row.addWidget(self.btn_no_icon)
        button_row.addStretch()

        basic_layout.addLayout(button_row)

        # Test ToolButton widgets (icon only)
        basic_layout.addWidget(QLabel("ToolButton widgets (icon only):"))
        tool_row = QHBoxLayout()

        self.tool_edit = ToolButton(Name.EDIT, Type.PRIMARY)
        self.tool_save = ToolButton(Name.SAVE, Type.SECONDARY)
        self.tool_refresh = ToolButton(Name.REFRESH, Type.DEFAULT)
        self.tool_cross = ToolButton(Name.CROSS, Type.DEFAULT)

        tool_row.addWidget(self.tool_edit)
        tool_row.addWidget(self.tool_save)
        tool_row.addWidget(self.tool_refresh)
        tool_row.addWidget(self.tool_cross)
        tool_row.addStretch()

        basic_layout.addLayout(tool_row)
        main_layout.addWidget(basic_group)

        # === CHECKABLE BEHAVIOR TESTS ===
        checkable_group = QGroupBox("Checkable Behavior Tests")
        checkable_layout = QVBoxLayout(checkable_group)

        checkable_layout.addWidget(QLabel("Checkable Buttons (click to toggle):"))
        check_row = QHBoxLayout()

        self.check_btn = Button("Toggle Me", Type.PRIMARY, Name.HEART)
        self.check_btn.setCheckable(True)

        self.check_tool = ToolButton(Name.HEART_FILLED, Type.SECONDARY)
        self.check_tool.setCheckable(True)

        check_row.addWidget(self.check_btn)
        check_row.addWidget(self.check_tool)
        check_row.addStretch()

        checkable_layout.addLayout(check_row)
        main_layout.addWidget(checkable_group)

        # === SIZING TESTS ===
        sizing_group = QGroupBox("Button Sizing Tests")
        sizing_layout = QVBoxLayout(sizing_group)

        # Custom button sizes
        sizing_layout.addWidget(QLabel("Custom Button Sizes:"))
        size_row = QHBoxLayout()

        self.size_small = Button("Small", Type.PRIMARY, Name.SETTINGS)

        self.size_medium = Button("Medium", Type.SECONDARY, Name.SETTINGS)

        self.size_large = Button("Large", Type.DEFAULT, Name.SETTINGS)

        size_row.addWidget(self.size_small)
        size_row.addWidget(self.size_medium)
        size_row.addWidget(self.size_large)
        size_row.addStretch()

        sizing_layout.addLayout(size_row)

        # Custom icon sizes
        sizing_layout.addWidget(QLabel("Custom Icon Sizes:"))
        icon_size_row = QHBoxLayout()

        self.icon_small = ToolButton(Name.HEART, Type.PRIMARY)
        self.icon_small.setCheckable(True)
        self.icon_small.setIconSize(12, 12)

        self.icon_medium = ToolButton(Name.HEART, Type.PRIMARY)
        self.icon_medium.setCheckable(True)
        self.icon_medium.setIconSize(24, 24)

        self.icon_large = ToolButton(Name.HEART, Type.PRIMARY)
        self.icon_large.setCheckable(True)
        self.icon_large.setIconSize(48, 48)

        icon_size_row.addWidget(QLabel("12px"))
        icon_size_row.addWidget(self.icon_small)
        icon_size_row.addWidget(QLabel("24px"))
        icon_size_row.addWidget(self.icon_medium)
        icon_size_row.addWidget(QLabel("48px"))
        icon_size_row.addWidget(self.icon_large)
        icon_size_row.addStretch()

        sizing_layout.addLayout(icon_size_row)

        # Dynamic sizing test
        sizing_layout.addWidget(QLabel("Dynamic Icon Sizing (use spinbox):"))
        dynamic_row = QHBoxLayout()

        self.dynamic_tool = ToolButton(Name.SETTINGS, Type.SECONDARY)
        self.icon_size_spinbox = QSpinBox()
        self.icon_size_spinbox.setRange(8, 64)
        self.icon_size_spinbox.setValue(24)
        self.icon_size_spinbox.valueChanged.connect(self._update_dynamic_icon_size)

        dynamic_row.addWidget(QLabel("Icon Size:"))
        dynamic_row.addWidget(self.icon_size_spinbox)
        dynamic_row.addWidget(self.dynamic_tool)
        dynamic_row.addStretch()

        sizing_layout.addLayout(dynamic_row)
        main_layout.addWidget(sizing_group)

        # === BUTTON TYPE TESTS ===
        type_group = QGroupBox("Button Type Tests")
        type_layout = QVBoxLayout(type_group)

        type_layout.addWidget(QLabel("Different Button Types (hover to see state changes):"))
        type_row = QHBoxLayout()

        self.type_default = Button("Default", Type.DEFAULT, Name.INFO)
        self.type_primary = Button("Primary", Type.PRIMARY, Name.INFO)
        self.type_secondary = Button("Secondary", Type.SECONDARY, Name.INFO)
        self.type_titlebar = Button("Titlebar", Type.TITLEBAR, Name.INFO)

        type_row.addWidget(self.type_default)
        type_row.addWidget(self.type_primary)
        type_row.addWidget(self.type_secondary)
        type_row.addWidget(self.type_titlebar)
        type_row.addStretch()

        type_layout.addLayout(type_row)
        main_layout.addWidget(type_group)

        # === STATE OVERRIDE TESTS ===
        state_group = QGroupBox("State Override Tests")
        state_layout = QVBoxLayout(state_group)

        state_layout.addWidget(QLabel("Custom State Colors (hover and click to test):"))
        state_row = QHBoxLayout()

        self.state_btn = Button("Custom States", Type.DEFAULT, Name.HEART)
        self.state_btn.setCheckable(True)
        self.state_btn.setStateDefault("error")
        self.state_btn.setStateHover("error")
        self.state_btn.setStateChecked("error")

        self.state_tool = ToolButton(Name.LIGHTBULB, Type.DEFAULT)
        self.state_tool.setCheckable(True)
        self.state_tool.setStateDefault("secondary")
        self.state_tool.setStateHover("tertiary")
        self.state_tool.setStateChecked("primary")

        state_row.addWidget(self.state_btn)
        state_row.addWidget(self.state_tool)
        state_row.addStretch()

        state_layout.addLayout(state_row)

        # Clear overrides test
        clear_row = QHBoxLayout()
        btn_clear_overrides = QPushButton("Clear State Overrides")
        btn_clear_overrides.clicked.connect(self._clear_state_overrides)
        clear_row.addWidget(btn_clear_overrides)
        clear_row.addStretch()
        state_layout.addLayout(clear_row)

        main_layout.addWidget(state_group)

        # === MANUAL STATE CONTROLS ===
        control_group = QGroupBox("Manual State Controls")
        control_layout = QVBoxLayout(control_group)

        control_layout.addWidget(QLabel("Force Enable/Disable (affects all buttons):"))
        control_row = QHBoxLayout()

        btn_enable = QPushButton("Enable All")
        btn_disable = QPushButton("Disable All")

        btn_enable.clicked.connect(self._enable_all_buttons)
        btn_disable.clicked.connect(self._disable_all_buttons)

        control_row.addWidget(btn_enable)
        control_row.addWidget(btn_disable)
        control_row.addStretch()

        control_layout.addLayout(control_row)
        main_layout.addWidget(control_group)

        # === SPACING TESTS ===
        spacing_group = QGroupBox("Spacing Tests")
        spacing_layout = QVBoxLayout(spacing_group)

        spacing_layout.addWidget(QLabel("Icon-Label Spacing (use spinbox):"))
        spacing_row = QHBoxLayout()

        self.spacing_btn = Button("Spacing Test", Type.PRIMARY, Name.SETTINGS)
        self.spacing_spinbox = QSpinBox()
        self.spacing_spinbox.setRange(0, 50)
        self.spacing_spinbox.setValue(6)
        self.spacing_spinbox.valueChanged.connect(self._update_spacing)

        spacing_row.addWidget(QLabel("Spacing:"))
        spacing_row.addWidget(self.spacing_spinbox)
        spacing_row.addWidget(self.spacing_btn)
        spacing_row.addStretch()

        spacing_layout.addLayout(spacing_row)
        main_layout.addWidget(spacing_group)

        # === THEME CONTROLS ===
        theme_group = QGroupBox("Theme Controls")
        theme_layout = QVBoxLayout(theme_group)

        theme_layout.addWidget(QLabel("Theme Switching:"))
        theme_row1 = QHBoxLayout()

        btn_light = QPushButton("Light Mode")
        btn_dark = QPushButton("Dark Mode")
        btn_toggle = QPushButton("Toggle Mode")

        btn_light.clicked.connect(lambda: Theme.setThemeMode(Mode.LIGHT))
        btn_dark.clicked.connect(lambda: Theme.setThemeMode(Mode.DARK))
        btn_toggle.clicked.connect(lambda: Theme.toggleThemeMode())

        theme_row1.addWidget(btn_light)
        theme_row1.addWidget(btn_dark)
        theme_row1.addWidget(btn_toggle)
        theme_row1.addStretch()

        theme_layout.addLayout(theme_row1)

        theme_layout.addWidget(QLabel("Color Schemes:"))
        theme_row2 = QHBoxLayout()

        btn_blue = QPushButton("Blue")
        btn_teal = QPushButton("Teal")
        btn_purple = QPushButton("Purple")
        btn_red = QPushButton("Red")
        btn_green = QPushButton("Green")

        btn_blue.clicked.connect(lambda: Theme.setThemeColor(Color.BLUE))
        btn_teal.clicked.connect(lambda: Theme.setThemeColor(Color.TEAL))
        btn_purple.clicked.connect(lambda: Theme.setThemeColor(Color.PURPLE))
        btn_red.clicked.connect(lambda: Theme.setThemeColor(Color.RED))
        btn_green.clicked.connect(lambda: Theme.setThemeColor(Color.GREEN))

        theme_row2.addWidget(btn_blue)
        theme_row2.addWidget(btn_teal)
        theme_row2.addWidget(btn_purple)
        theme_row2.addWidget(btn_red)
        theme_row2.addWidget(btn_green)
        theme_row2.addStretch()

        theme_layout.addLayout(theme_row2)

        # Rapid theme switching test
        theme_layout.addWidget(QLabel("Stress Tests:"))
        stress_row = QHBoxLayout()

        self.rapid_timer = QTimer()
        self.rapid_timer.timeout.connect(self._rapid_theme_switch)
        self.rapid_colors = [Color.BLUE, Color.TEAL, Color.RED, Color.GREEN, Color.PURPLE]
        self.rapid_index = 0

        btn_rapid = QPushButton("Start Rapid Theme Switching")
        btn_stop_rapid = QPushButton("Stop")

        btn_rapid.clicked.connect(lambda: self.rapid_timer.start(500))  # Every 500ms
        btn_stop_rapid.clicked.connect(lambda: self.rapid_timer.stop())

        stress_row.addWidget(btn_rapid)
        stress_row.addWidget(btn_stop_rapid)
        stress_row.addStretch()

        theme_layout.addLayout(stress_row)
        main_layout.addWidget(theme_group)

        # === STATUS INFO ===
        status_group = QGroupBox("Status Info")
        status_layout = QVBoxLayout(status_group)

        self.status_label = QLabel("Status: Ready")
        status_layout.addWidget(self.status_label)

        main_layout.addWidget(status_group)

        main_layout.addStretch()

    def _update_dynamic_icon_size(self, size):
        """Update the dynamic icon size."""
        self.dynamic_tool.setIconSize(size, size)
        self.status_label.setText(f"Status: Updated dynamic icon to {size}x{size}")

    def _update_spacing(self, spacing):
        """Update the icon-label spacing."""
        self.spacing_btn.setIconSpacing(spacing)
        self.status_label.setText(f"Status: Updated spacing to {spacing}px")

    def _clear_state_overrides(self):
        """Clear state overrides on custom buttons."""
        self.state_btn.clearAllStateOverrides()
        self.state_tool.clearAllStateOverrides()
        self.status_label.setText("Status: Cleared all state overrides")

    def _enable_all_buttons(self):
        """Enable all buttons."""
        buttons = [
            self.btn_dashboard, self.btn_settings, self.btn_exit, self.btn_no_icon,
            self.tool_edit, self.tool_save, self.tool_refresh, self.tool_cross,
            self.check_btn, self.check_tool, self.size_small, self.size_medium, self.size_large,
            self.icon_small, self.icon_medium, self.icon_large, self.dynamic_tool,
            self.type_default, self.type_primary, self.type_secondary, self.type_titlebar,
            self.state_btn, self.state_tool, self.spacing_btn
        ]

        for btn in buttons:
            btn.setEnabled(True)

        self.status_label.setText("Status: Enabled all buttons")

    def _disable_all_buttons(self):
        """Disable all buttons."""
        buttons = [
            self.btn_dashboard, self.btn_settings, self.btn_exit, self.btn_no_icon,
            self.tool_edit, self.tool_save, self.tool_refresh, self.tool_cross,
            self.check_btn, self.check_tool, self.size_small, self.size_medium, self.size_large,
            self.icon_small, self.icon_medium, self.icon_large, self.dynamic_tool,
            self.type_default, self.type_primary, self.type_secondary, self.type_titlebar,
            self.state_btn, self.state_tool, self.spacing_btn
        ]

        for btn in buttons:
            btn.setEnabled(False)

        self.status_label.setText("Status: Disabled all buttons")

    def _rapid_theme_switch(self):
        """Rapidly switch between themes for stress testing."""
        color = self.rapid_colors[self.rapid_index]
        mode = Mode.LIGHT if self.rapid_index % 2 == 0 else Mode.DARK

        Theme.setTheme(color, mode)

        self.rapid_index = (self.rapid_index + 1) % len(self.rapid_colors)
        self.status_label.setText(f"Status: Rapid switching - {color.name} {mode.name}")

    def keyPressEvent(self, event):
        """Keyboard shortcuts for quick testing."""
        if event.key() == Qt.Key_1:
            Theme.setTheme(Color.BLUE, Mode.LIGHT)
        elif event.key() == Qt.Key_2:
            Theme.setTheme(Color.BLUE, Mode.DARK)
        elif event.key() == Qt.Key_3:
            Theme.setTheme(Color.TEAL, Mode.LIGHT)
        elif event.key() == Qt.Key_4:
            Theme.setTheme(Color.TEAL, Mode.DARK)
        elif event.key() == Qt.Key_T:
            Theme.toggleThemeMode()
        elif event.key() == Qt.Key_C:
            self._clear_state_overrides()
        elif event.key() == Qt.Key_E:
            self._enable_all_buttons()
        elif event.key() == Qt.Key_D:
            self._disable_all_buttons()
        elif event.key() == Qt.Key_Escape:
            if self.rapid_timer.isActive():
                self.rapid_timer.stop()
                self.status_label.setText("Status: Stopped rapid switching")


def main():
    app = QApplication(sys.argv)

    # Initialize theme
    try:
        #Theme.setCustomColorMap("material-theme.json", Mode.DARK)
        Theme.setTheme(Color.FOJI_GREEN, Mode.DARK)
        print("Theme system initialized successfully")
    except Exception as e:
        print(f"Warning: Could not initialize theme system: {e}")

    window = ButtonTestWindow()
    window.show()

    print("\n=== KEYBOARD SHORTCUTS ===")
    print("1: Blue Light")
    print("2: Blue Dark")
    print("3: Teal Light")
    print("4: Teal Dark")
    print("T: Toggle Light/Dark")
    print("C: Clear State Overrides")
    print("E: Enable All Buttons")
    print("D: Disable All Buttons")
    print("ESC: Stop rapid switching")
    print("============================\n")

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
