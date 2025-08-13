"""test_toggle_switch.py

Test demo for the ToggleSwitch widget.
Shows various toggle switches with different states and demonstrates functionality.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QSpacerItem, QSizePolicy, QGroupBox, QPushButton,
    QCheckBox, QTextEdit
)
from PySide6.QtGui import QFont

from app.style.theme_controller import Theme, Mode, Color
from app.ui.components.widgets.toggle_switch import ToggleSwitch


class ToggleSwitchDemo(QMainWindow):
    """Demo window for testing the ToggleSwitch widget."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Toggle Switch Demo")
        self.setFixedSize(600, 500)

        # Apply theme
        Theme.setTheme(Color.BLUE, Mode.DARK)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title = QLabel("Toggle Switch Component Demo")
        title.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        title.setFont(font)
        main_layout.addWidget(title)

        # Create demo sections
        self.create_basic_demos(main_layout)
        self.create_interactive_demo(main_layout)
        self.create_control_demo(main_layout)

        # Add stretch
        main_layout.addStretch()

        # Log area
        self.log_area = QTextEdit()
        self.log_area.setMaximumHeight(100)
        self.log_area.setPlaceholderText("Event log will appear here...")
        main_layout.addWidget(QLabel("Event Log:"))
        main_layout.addWidget(self.log_area)

    def create_basic_demos(self, layout):
        """Create basic toggle switch demonstrations."""
        group = QGroupBox("Basic Toggle Switches")
        group_layout = QVBoxLayout(group)

        # Default states
        states_layout = QHBoxLayout()

        # Off switch
        off_container = QVBoxLayout()
        off_label = QLabel("Default (Off)")
        off_label.setAlignment(Qt.AlignCenter)
        self.switch_off = ToggleSwitch(checked=False)
        self.switch_off.toggled.connect(lambda state: self.log_event(f"Off Switch: {state}"))
        off_container.addWidget(off_label)
        off_container.addWidget(self.switch_off, alignment=Qt.AlignCenter)

        # On switch
        on_container = QVBoxLayout()
        on_label = QLabel("Default (On)")
        on_label.setAlignment(Qt.AlignCenter)
        self.switch_on = ToggleSwitch(checked=True)
        self.switch_on.toggled.connect(lambda state: self.log_event(f"On Switch: {state}"))
        on_container.addWidget(on_label)
        on_container.addWidget(self.switch_on, alignment=Qt.AlignCenter)

        states_layout.addLayout(off_container)
        states_layout.addStretch()
        states_layout.addLayout(on_container)

        group_layout.addLayout(states_layout)
        layout.addWidget(group)

    def create_interactive_demo(self, layout):
        """Create interactive toggle switch demonstration."""
        group = QGroupBox("Interactive Demo")
        group_layout = QVBoxLayout(group)

        # Multiple switches
        switches_layout = QHBoxLayout()

        self.interactive_switches = []
        switch_labels = ["WiFi", "Bluetooth", "Dark Mode", "Notifications", "Auto-Save"]

        for i, label in enumerate(switch_labels):
            container = QVBoxLayout()
            label_widget = QLabel(label)
            label_widget.setAlignment(Qt.AlignCenter)

            switch = ToggleSwitch(checked=i % 2 == 0)  # Alternate initial states
            switch.toggled.connect(lambda state, name=label: self.log_event(f"{name}: {state}"))
            self.interactive_switches.append(switch)

            container.addWidget(label_widget)
            container.addWidget(switch, alignment=Qt.AlignCenter)
            switches_layout.addLayout(container)

        group_layout.addLayout(switches_layout)
        layout.addWidget(group)

    def create_control_demo(self, layout):
        """Create programmatic control demonstration."""
        group = QGroupBox("Programmatic Control")
        group_layout = QVBoxLayout(group)

        # Control switch
        control_layout = QHBoxLayout()
        control_label = QLabel("Master Switch:")
        self.master_switch = ToggleSwitch()
        self.master_switch.toggled.connect(self.on_master_toggle)

        control_layout.addWidget(control_label)
        control_layout.addWidget(self.master_switch)
        control_layout.addStretch()

        # Control buttons
        button_layout = QHBoxLayout()

        self.toggle_all_btn = QPushButton("Toggle All")
        self.toggle_all_btn.clicked.connect(self.toggle_all_switches)

        self.turn_on_all_btn = QPushButton("Turn On All")
        self.turn_on_all_btn.clicked.connect(self.turn_on_all_switches)

        self.turn_off_all_btn = QPushButton("Turn Off All")
        self.turn_off_all_btn.clicked.connect(self.turn_off_all_switches)

        button_layout.addWidget(self.toggle_all_btn)
        button_layout.addWidget(self.turn_on_all_btn)
        button_layout.addWidget(self.turn_off_all_btn)

        group_layout.addLayout(control_layout)
        group_layout.addLayout(button_layout)
        layout.addWidget(group)

    def log_event(self, message):
        """Log an event to the log area."""
        self.log_area.append(f"• {message}")
        # Keep only last 10 lines
        text = self.log_area.toPlainText()
        lines = text.split('\n')
        if len(lines) > 10:
            self.log_area.clear()
            self.log_area.append('\n'.join(lines[-10:]))

    def on_master_toggle(self, state):
        """Handle master switch toggle."""
        self.log_event(f"Master Switch: {state}")
        action = "enabled" if state else "disabled"
        self.log_event(f"All controls {action}")

    def toggle_all_switches(self):
        """Toggle all interactive switches."""
        for switch in self.interactive_switches:
            switch.toggle()
        self.log_event("Toggled all switches")

    def turn_on_all_switches(self):
        """Turn on all switches."""
        switches_to_update = [self.switch_off, self.switch_on, self.master_switch] + self.interactive_switches
        for switch in switches_to_update:
            switch.setChecked(True)
        self.log_event("Turned on all switches")

    def turn_off_all_switches(self):
        """Turn off all switches."""
        switches_to_update = [self.switch_off, self.switch_on, self.master_switch] + self.interactive_switches
        for switch in switches_to_update:
            switch.setChecked(False)
        self.log_event("Turned off all switches")


def run_test(app):
    """Entry point for the test harness."""
    window = ToggleSwitchDemo()
    window.show()
    return window


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = run_test(app)
    sys.exit(app.exec())
