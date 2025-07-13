"""scripts/flyout_demo.py

Demo application showcasing the FlyoutWidget functionality with different directions,
content types, and interactive features.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QTextEdit, QSpinBox, QComboBox,
    QCheckBox, QListWidget, QGridLayout, QGroupBox, QSlider,
    QProgressBar, QLineEdit, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPalette

from app.ui.components.layout.flyout_widget import FlyoutWidget
from dev_tools import DebugLogger


class FlyoutDemo(QMainWindow):
    """Main demo window showcasing FlyoutWidget capabilities."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FlyoutWidget Demo")
        self.setGeometry(100, 100, 800, 600)

        # Store flyout references
        self.flyouts = {}

        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        """Setup the main demo interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("FlyoutWidget Demo")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        main_layout.addWidget(title)

        # Direction demos
        direction_group = self.create_direction_demo()
        main_layout.addWidget(direction_group)

        # Content type demos
        content_group = self.create_content_demo()
        main_layout.addWidget(content_group)

        # Advanced features
        advanced_group = self.create_advanced_demo()
        main_layout.addWidget(advanced_group)

        # Settings panel
        settings_group = self.create_settings_demo()
        main_layout.addWidget(settings_group)

        main_layout.addStretch()

    def create_direction_demo(self):
        """Create demo section for different flyout directions."""
        group = QGroupBox("Direction Demos")
        layout = QGridLayout(group)

        # Center anchor widget
        center_widget = QFrame()
        center_widget.setFixedSize(120, 80)
        center_widget.setStyleSheet("""
            QFrame {
                background-color: #3498db;
                border: 2px solid #2980b9;
                border-radius: 8px;
            }
        """)
        center_label = QLabel("Anchor\nWidget")
        center_label.setAlignment(Qt.AlignCenter)
        center_label.setStyleSheet("color: white; font-weight: bold;")
        center_layout = QVBoxLayout(center_widget)
        center_layout.addWidget(center_label)

        # Position center widget
        layout.addWidget(center_widget, 1, 1)

        # Direction buttons and flyouts
        directions = [
            ("TOP", FlyoutWidget.TOP, 0, 1),
            ("RIGHT", FlyoutWidget.RIGHT, 1, 2),
            ("BOTTOM", FlyoutWidget.BOTTOM, 2, 1),
            ("LEFT", FlyoutWidget.LEFT, 1, 0)
        ]

        for name, direction, row, col in directions:
            btn = QPushButton(f"Show {name}")
            btn.setFixedSize(100, 30)
            layout.addWidget(btn, row, col)

            # Create flyout content
            content = QLabel(f"Flyout from {name}\nDirection: {direction}")
            content.setAlignment(Qt.AlignCenter)
            content.setStyleSheet("""
                QLabel {
                    background-color: #ecf0f1;
                    border: 1px solid #bdc3c7;
                    padding: 10px;
                    border-radius: 4px;
                    min-width: 150px;
                    min-height: 60px;
                }
            """)

            flyout = FlyoutWidget(
                anchor=center_widget,
                direction=direction,
                content=content,
                duration=400
            )

            self.flyouts[f"direction_{name.lower()}"] = flyout
            btn.clicked.connect(lambda checked, f=flyout: f.toggle_flyout())

        return group

    def create_content_demo(self):
        """Create demo section for different content types."""
        group = QGroupBox("Content Type Demos")
        layout = QHBoxLayout(group)

        # Simple text content
        text_btn = QPushButton("Simple Text")
        text_content = QLabel("This is a simple text flyout\nwith multiple lines of content.")
        text_content.setStyleSheet("padding: 15px; background: #f8f9fa; border-radius: 4px;")
        text_flyout = FlyoutWidget(text_btn, FlyoutWidget.BOTTOM, text_content)
        self.flyouts["text"] = text_flyout
        text_btn.clicked.connect(text_flyout.toggle_flyout)
        layout.addWidget(text_btn)

        # Interactive content
        interactive_btn = QPushButton("Interactive Content")
        interactive_content = self.create_interactive_content()
        interactive_flyout = FlyoutWidget(interactive_btn, FlyoutWidget.RIGHT, interactive_content)
        self.flyouts["interactive"] = interactive_flyout
        interactive_btn.clicked.connect(interactive_flyout.toggle_flyout)
        layout.addWidget(interactive_btn)

        # List content
        list_btn = QPushButton("List Content")
        list_content = self.create_list_content()
        list_flyout = FlyoutWidget(list_btn, FlyoutWidget.LEFT, list_content)
        self.flyouts["list"] = list_flyout
        list_btn.clicked.connect(list_flyout.toggle_flyout)
        layout.addWidget(list_btn)

        # Form content
        form_btn = QPushButton("Form Content")
        form_content = self.create_form_content()
        form_flyout = FlyoutWidget(form_btn, FlyoutWidget.TOP, form_content)
        self.flyouts["form"] = form_flyout
        form_btn.clicked.connect(form_flyout.toggle_flyout)
        layout.addWidget(form_btn)

        return group

    def create_interactive_content(self):
        """Create interactive content for flyout."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)

        layout.addWidget(QLabel("Interactive Controls:"))

        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(50)
        layout.addWidget(slider)

        progress = QProgressBar()
        progress.setValue(50)
        layout.addWidget(progress)

        # Connect slider to progress bar
        slider.valueChanged.connect(progress.setValue)

        checkbox = QCheckBox("Enable feature")
        checkbox.setChecked(True)
        layout.addWidget(checkbox)

        widget.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border: 1px solid #ddd;
                border-radius: 6px;
            }
        """)

        return widget

    def create_list_content(self):
        """Create list content for flyout."""
        list_widget = QListWidget()
        list_widget.setFixedSize(200, 150)

        items = [
            "🍎 Apples",
            "🍌 Bananas",
            "🍊 Oranges",
            "🍇 Grapes",
            "🥝 Kiwi",
            "🍓 Strawberries"
        ]

        for item in items:
            list_widget.addItem(item)

        list_widget.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
        """)

        return list_widget

    def create_form_content(self):
        """Create form content for flyout."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)

        layout.addWidget(QLabel("Quick Form:"))

        name_input = QLineEdit()
        name_input.setPlaceholderText("Enter name...")
        layout.addWidget(name_input)

        combo = QComboBox()
        combo.addItems(["Option 1", "Option 2", "Option 3"])
        layout.addWidget(combo)

        spinbox = QSpinBox()
        spinbox.setRange(1, 100)
        spinbox.setValue(10)
        layout.addWidget(spinbox)

        submit_btn = QPushButton("Submit")
        submit_btn.clicked.connect(lambda: DebugLogger.log("Form submitted!", "info"))
        layout.addWidget(submit_btn)

        widget.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border: 1px solid #ddd;
                border-radius: 6px;
            }
        """)

        return widget

    def create_advanced_demo(self):
        """Create advanced features demo."""
        group = QGroupBox("Advanced Features")
        layout = QHBoxLayout(group)

        # Chained flyouts
        chain_btn = QPushButton("Chained Flyouts")
        self.setup_chained_flyouts(chain_btn)
        layout.addWidget(chain_btn)

        # Auto-close flyout
        auto_btn = QPushButton("Auto-Close Flyout")
        self.setup_auto_close_flyout(auto_btn)
        layout.addWidget(auto_btn)

        # Dynamic content
        dynamic_btn = QPushButton("Dynamic Content")
        self.setup_dynamic_content_flyout(dynamic_btn)
        layout.addWidget(dynamic_btn)

        return group

    def setup_chained_flyouts(self, anchor_btn):
        """Setup chained flyouts demo."""
        # First flyout
        first_content = QWidget()
        first_layout = QVBoxLayout(first_content)
        first_layout.addWidget(QLabel("First Flyout"))

        second_btn = QPushButton("Show Second")
        first_layout.addWidget(second_btn)

        first_flyout = FlyoutWidget(anchor_btn, FlyoutWidget.RIGHT, first_content)

        # Second flyout
        second_content = QLabel("Second Flyout\nChained from first!")
        second_content.setStyleSheet("padding: 10px; background: #e8f5e8; border-radius: 4px;")
        second_flyout = FlyoutWidget(second_btn, FlyoutWidget.RIGHT, second_content)

        # Connect buttons
        anchor_btn.clicked.connect(first_flyout.toggle_flyout)
        second_btn.clicked.connect(second_flyout.toggle_flyout)

        self.flyouts["chain_first"] = first_flyout
        self.flyouts["chain_second"] = second_flyout

    def setup_auto_close_flyout(self, anchor_btn):
        """Setup auto-closing flyout."""
        content = QLabel("This flyout will\nauto-close in 3 seconds")
        content.setStyleSheet("padding: 15px; background: #fff3cd; border-radius: 4px;")

        flyout = FlyoutWidget(anchor_btn, FlyoutWidget.BOTTOM, content)

        def show_auto_close():
            flyout.setVisibleAnimated(True)
            QTimer.singleShot(3000, lambda: flyout.setVisibleAnimated(False))

        anchor_btn.clicked.connect(show_auto_close)
        self.flyouts["auto_close"] = flyout

    def setup_dynamic_content_flyout(self, anchor_btn):
        """Setup flyout with dynamic content updates."""
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)

        self.dynamic_label = QLabel("Dynamic Content #1")
        self.dynamic_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.dynamic_label)

        update_btn = QPushButton("Update Content")
        layout.addWidget(update_btn)

        self.content_counter = 1

        def update_content():
            self.content_counter += 1
            self.dynamic_label.setText(f"Dynamic Content #{self.content_counter}")

        update_btn.clicked.connect(update_content)

        flyout = FlyoutWidget(anchor_btn, FlyoutWidget.TOP, content_widget)
        anchor_btn.clicked.connect(flyout.toggle_flyout)
        self.flyouts["dynamic"] = flyout

    def create_settings_demo(self):
        """Create settings demonstration."""
        group = QGroupBox("Flyout Settings Demo")
        layout = QVBoxLayout(group)

        controls_layout = QHBoxLayout()

        # Duration control
        controls_layout.addWidget(QLabel("Duration (ms):"))
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(100, 2000)
        self.duration_spin.setValue(300)
        controls_layout.addWidget(self.duration_spin)

        # Margin control
        controls_layout.addWidget(QLabel("Margin:"))
        self.margin_spin = QSpinBox()
        self.margin_spin.setRange(0, 50)
        self.margin_spin.setValue(5)
        controls_layout.addWidget(self.margin_spin)

        # Direction control
        controls_layout.addWidget(QLabel("Direction:"))
        self.direction_combo = QComboBox()
        self.direction_combo.addItems(["TOP", "RIGHT", "BOTTOM", "LEFT"])
        self.direction_combo.setCurrentText("RIGHT")
        controls_layout.addWidget(self.direction_combo)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Test button
        test_btn = QPushButton("Test Custom Settings")
        test_btn.setFixedHeight(40)
        layout.addWidget(test_btn)

        # Setup custom flyout
        self.setup_custom_settings_flyout(test_btn)

        return group

    def setup_custom_settings_flyout(self, anchor_btn):
        """Setup flyout with customizable settings."""
        content = QLabel("Custom Settings Flyout\nDuration and margin adjustable!")
        content.setStyleSheet("padding: 20px; background: #e1f5fe; border-radius: 6px;")

        # Create flyout with initial settings
        flyout = FlyoutWidget(
            anchor_btn,
            FlyoutWidget.RIGHT,
            content,
            duration=300,
            margin=5
        )

        def show_with_settings():
            # Update flyout settings based on controls
            direction_map = {
                "TOP": FlyoutWidget.TOP,
                "RIGHT": FlyoutWidget.RIGHT,
                "BOTTOM": FlyoutWidget.BOTTOM,
                "LEFT": FlyoutWidget.LEFT
            }

            flyout.direction = direction_map[self.direction_combo.currentText()]
            flyout.duration = self.duration_spin.value()
            flyout.margin = self.margin_spin.value()

            flyout.toggle_flyout()

        anchor_btn.clicked.connect(show_with_settings)
        self.flyouts["custom"] = flyout

    def apply_styles(self):
        """Apply overall styling to the demo."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)

    def closeEvent(self, event):
        """Clean up when closing."""
        # Hide all flyouts before closing
        for flyout in self.flyouts.values():
            if flyout._visible:
                flyout.hide()
        event.accept()


def main():
    """Run the flyout demo application."""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("FlyoutWidget Demo")
    app.setApplicationVersion("1.0")

    # Create and show the demo window
    demo = FlyoutDemo()
    demo.show()

    DebugLogger.log("FlyoutWidget Demo started", "info")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
