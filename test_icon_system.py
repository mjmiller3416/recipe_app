"""test_icon_system.py

Enhanced test file for the new icon system (Phase 1).
Tests BaseIcon, ThemedIcon, Icon, and StateIcon classes in isolation.
"""

import sys
from pathlib import Path

# Add the app directory to the Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir.parent))

from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QCheckBox, QSpinBox, QGroupBox)
from PySide6.QtCore import Qt, QTimer

from app.appearance.icon.icon import Icon, StateIcon
from app.appearance.icon.config import Name, Type, State
from app.appearance.theme import Theme
from app.appearance.config import Color, Mode


class IconTestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Icon System Test - Phase 1")
        self.setMinimumSize(1000, 800)

        # Create scroll area for the main content
        from PySide6.QtWidgets import QScrollArea
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

        # === BASIC ICON TESTS ===
        basic_group = QGroupBox("Basic Icon Tests")
        basic_layout = QVBoxLayout(basic_group)

        # Test standalone Icon widgets
        basic_layout.addWidget(QLabel("Standalone Icons (different sizes):"))
        icon_row = QHBoxLayout()

        self.icon_dashboard = Icon(Name.DASHBOARD)  # Large
        self.icon_edit = Icon(Name.EDIT)  # Small
        self.icon_heart = Icon(Name.HEART)  # Small
        self.icon_logo = Icon(Name.LOGO)  # Medium
        self.icon_info = Icon(Name.INFO)  # XL

        icon_row.addWidget(QLabel("DASHBOARD\n(Large)"))
        icon_row.addWidget(self.icon_dashboard)
        icon_row.addWidget(QLabel("EDIT\n(Small)"))
        icon_row.addWidget(self.icon_edit)
        icon_row.addWidget(QLabel("HEART\n(Small)"))
        icon_row.addWidget(self.icon_heart)
        icon_row.addWidget(QLabel("LOGO\n(Medium)"))
        icon_row.addWidget(self.icon_logo)
        icon_row.addWidget(QLabel("INFO\n(XL)"))
        icon_row.addWidget(self.icon_info)
        icon_row.addStretch()

        basic_layout.addLayout(icon_row)
        main_layout.addWidget(basic_group)

        # === CUSTOM SIZING TESTS ===
        sizing_group = QGroupBox("Custom Sizing Tests")
        sizing_layout = QVBoxLayout(sizing_group)

        sizing_layout.addWidget(QLabel("Custom Sized Icons:"))
        custom_row = QHBoxLayout()

        self.icon_large = Icon(Name.SETTINGS)
        self.icon_large.setSize(64, 64)

        self.icon_medium = Icon(Name.SETTINGS)
        self.icon_medium.setSize(32, 32)

        self.icon_small = Icon(Name.SETTINGS)
        self.icon_small.setSize(16, 16)

        self.icon_tiny = Icon(Name.SETTINGS)
        self.icon_tiny.setSize(8, 8)

        custom_row.addWidget(QLabel("64x64"))
        custom_row.addWidget(self.icon_large)
        custom_row.addWidget(QLabel("32x32"))
        custom_row.addWidget(self.icon_medium)
        custom_row.addWidget(QLabel("16x16"))
        custom_row.addWidget(self.icon_small)
        custom_row.addWidget(QLabel("8x8"))
        custom_row.addWidget(self.icon_tiny)
        custom_row.addStretch()

        sizing_layout.addLayout(custom_row)

        # Dynamic sizing test
        sizing_layout.addWidget(QLabel("Dynamic Sizing (use spinbox):"))
        dynamic_row = QHBoxLayout()

        self.dynamic_icon = Icon(Name.HEART)
        self.size_spinbox = QSpinBox()
        self.size_spinbox.setRange(8, 128)
        self.size_spinbox.setValue(24)
        self.size_spinbox.valueChanged.connect(self._update_dynamic_size)

        dynamic_row.addWidget(QLabel("Size:"))
        dynamic_row.addWidget(self.size_spinbox)
        dynamic_row.addWidget(self.dynamic_icon)
        dynamic_row.addStretch()

        sizing_layout.addLayout(dynamic_row)
        main_layout.addWidget(sizing_group)

        # === COLOR TESTS ===
        color_group = QGroupBox("Color Tests")
        color_layout = QVBoxLayout(color_group)

        # Static colors (shouldn't change with theme)
        color_layout.addWidget(QLabel("Static Colors (should NOT change with theme):"))
        static_color_row = QHBoxLayout()

        self.icon_red = Icon(Name.HEART)
        self.icon_red.setColor("#FF0000")

        self.icon_blue = Icon(Name.HEART)
        self.icon_blue.setColor("#0000FF")

        self.icon_green = Icon(Name.HEART)
        self.icon_green.setColor("#00FF00")

        static_color_row.addWidget(QLabel("Red"))
        static_color_row.addWidget(self.icon_red)
        static_color_row.addWidget(QLabel("Blue"))
        static_color_row.addWidget(self.icon_blue)
        static_color_row.addWidget(QLabel("Green"))
        static_color_row.addWidget(self.icon_green)
        static_color_row.addStretch()

        color_layout.addLayout(static_color_row)

        # Themed colors (should change with theme)
        color_layout.addWidget(QLabel("Themed Colors (SHOULD change with theme):"))
        themed_color_row = QHBoxLayout()

        self.icon_primary = Icon(Name.SETTINGS)
        self.icon_primary.setColor("primary")

        self.icon_secondary = Icon(Name.DASHBOARD)
        self.icon_secondary.setColor("secondary")

        self.icon_tertiary = Icon(Name.EDIT)
        self.icon_tertiary.setColor("tertiary")

        self.icon_on_surface = Icon(Name.MENU)
        self.icon_on_surface.setColor("on_surface")

        themed_color_row.addWidget(QLabel("Primary"))
        themed_color_row.addWidget(self.icon_primary)
        themed_color_row.addWidget(QLabel("Secondary"))
        themed_color_row.addWidget(self.icon_secondary)
        themed_color_row.addWidget(QLabel("Tertiary"))
        themed_color_row.addWidget(self.icon_tertiary)
        themed_color_row.addWidget(QLabel("On Surface"))
        themed_color_row.addWidget(self.icon_on_surface)
        themed_color_row.addStretch()

        color_layout.addLayout(themed_color_row)
        main_layout.addWidget(color_group)

        # === STATE ICON TESTS ===
        state_group = QGroupBox("StateIcon Tests")
        state_layout = QVBoxLayout(state_group)

        # Different button types
        state_layout.addWidget(QLabel("Different Button Types (hover over them):"))
        type_row = QHBoxLayout()

        self.state_icon_default = StateIcon(Name.HEART, Type.DEFAULT)
        self.state_icon_primary = StateIcon(Name.EDIT, Type.PRIMARY)
        self.state_icon_secondary = StateIcon(Name.SETTINGS, Type.SECONDARY)
        self.state_icon_titlebar = StateIcon(Name.MINIMIZE, Type.TITLEBAR)

        type_row.addWidget(QLabel("DEFAULT"))
        type_row.addWidget(self.state_icon_default)
        type_row.addWidget(QLabel("PRIMARY"))
        type_row.addWidget(self.state_icon_primary)
        type_row.addWidget(QLabel("SECONDARY"))
        type_row.addWidget(self.state_icon_secondary)
        type_row.addWidget(QLabel("TITLEBAR"))
        type_row.addWidget(self.state_icon_titlebar)
        type_row.addStretch()

        state_layout.addLayout(type_row)

        # State override tests
        state_layout.addWidget(QLabel("Custom State Colors (overridden from type defaults):"))
        override_row = QHBoxLayout()

        self.state_icon_custom = StateIcon(Name.HEART_FILLED, Type.DEFAULT)
        self.state_icon_custom.setStateDefault("error")
        self.state_icon_custom.setStateHover("primary")
        self.state_icon_custom.setStateChecked("tertiary")

        override_row.addWidget(QLabel("Custom Colors\n(error/primary/tertiary)"))
        override_row.addWidget(self.state_icon_custom)
        override_row.addStretch()

        state_layout.addLayout(override_row)

        # AutoDetectState test
        state_layout.addWidget(QLabel("AutoDetectState Test:"))
        auto_row = QHBoxLayout()

        self.auto_state_icon = StateIcon(Name.BATTERY, Type.PRIMARY)

        self.hover_checkbox = QCheckBox("Hover")
        self.checked_checkbox = QCheckBox("Checked")
        self.enabled_checkbox = QCheckBox("Enabled")
        self.enabled_checkbox.setChecked(True)

        self.hover_checkbox.toggled.connect(self._update_auto_state)
        self.checked_checkbox.toggled.connect(self._update_auto_state)
        self.enabled_checkbox.toggled.connect(self._update_auto_state)

        auto_row.addWidget(self.auto_state_icon)
        auto_row.addWidget(self.hover_checkbox)
        auto_row.addWidget(self.checked_checkbox)
        auto_row.addWidget(self.enabled_checkbox)
        auto_row.addStretch()

        state_layout.addLayout(auto_row)
        main_layout.addWidget(state_group)

        # === MANUAL STATE CONTROLS ===
        control_group = QGroupBox("Manual State Controls")
        control_layout = QVBoxLayout(control_group)

        control_layout.addWidget(QLabel("Force State (affects all StateIcons above):"))
        control_row = QHBoxLayout()

        btn_default = QPushButton("Default")
        btn_hover = QPushButton("Hover")
        btn_checked = QPushButton("Checked")
        btn_disabled = QPushButton("Disabled")

        btn_default.clicked.connect(lambda: self._set_all_states(State.DEFAULT))
        btn_hover.clicked.connect(lambda: self._set_all_states(State.HOVER))
        btn_checked.clicked.connect(lambda: self._set_all_states(State.CHECKED))
        btn_disabled.clicked.connect(lambda: self._set_all_states(State.DISABLED))

        control_row.addWidget(btn_default)
        control_row.addWidget(btn_hover)
        control_row.addWidget(btn_checked)
        control_row.addWidget(btn_disabled)
        control_row.addStretch()

        control_layout.addLayout(control_row)

        # Clear overrides test
        clear_row = QHBoxLayout()
        btn_clear = QPushButton("Clear All State Overrides")
        btn_clear.clicked.connect(self._clear_overrides)
        clear_row.addWidget(btn_clear)
        clear_row.addStretch()
        control_layout.addLayout(clear_row)

        main_layout.addWidget(control_group)

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

    def _update_dynamic_size(self, size):
        """Update the dynamic icon size."""
        self.dynamic_icon.setSize(size, size)
        self.status_label.setText(f"Status: Updated dynamic icon to {size}x{size}")

    def _update_auto_state(self):
        """Update the auto state icon based on checkboxes."""
        self.auto_state_icon.autoDetectState(
            checked=self.checked_checkbox.isChecked(),
            hovered=self.hover_checkbox.isChecked(),
            enabled=self.enabled_checkbox.isChecked()
        )

        state_text = []
        if self.hover_checkbox.isChecked():
            state_text.append("hover")
        if self.checked_checkbox.isChecked():
            state_text.append("checked")
        if not self.enabled_checkbox.isChecked():
            state_text.append("disabled")
        if not state_text:
            state_text.append("default")

        self.status_label.setText(f"Status: Auto state - {', '.join(state_text)}")

    def _set_all_states(self, state: State):
        """Set all state icons to the specified state."""
        state_icons = [
            self.state_icon_default,
            self.state_icon_primary,
            self.state_icon_secondary,
            self.state_icon_titlebar,
            self.state_icon_custom,
            self.auto_state_icon
        ]

        for icon in state_icons:
            icon.updateState(state)

        self.status_label.setText(f"Status: Set all StateIcons to {state.name}")

    def _clear_overrides(self):
        """Clear state overrides on custom state icon."""
        self.state_icon_custom.clearAllStateOverrides()
        self.status_label.setText("Status: Cleared all state overrides")

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
        elif event.key() == Qt.Key_Escape:
            if self.rapid_timer.isActive():
                self.rapid_timer.stop()
                self.status_label.setText("Status: Stopped rapid switching")


def main():
    app = QApplication(sys.argv)

    # Initialize theme
    try:
        Theme.setTheme(Color.TEAL, Mode.LIGHT)
        print("✓ Theme system initialized successfully")
    except Exception as e:
        print(f"✗ Warning: Could not initialize theme system: {e}")

    window = IconTestWindow()
    window.show()

    print("\n=== KEYBOARD SHORTCUTS ===")
    print("1: Blue Light")
    print("2: Blue Dark")
    print("3: Teal Light")
    print("4: Teal Dark")
    print("T: Toggle Light/Dark")
    print("ESC: Stop rapid switching")
    print("============================\n")

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
