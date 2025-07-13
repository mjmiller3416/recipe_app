"""scripts/advanced_flyout_demo.py

Advanced demo showcasing the improved FlyoutWidget with flexible anchoring options.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QGroupBox, QGridLayout,
    QSpinBox, QComboBox, QFormLayout, QTextEdit, QSlider
)
from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtGui import QFont

from app.ui.components.layout.flyout_widget import FlyoutWidget
from dev_tools import DebugLogger


class AdvancedFlyoutDemo(QMainWindow):
    """Advanced demo showcasing all flyout anchoring modes."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced FlyoutWidget Demo - Flexible Anchoring")
        self.setGeometry(100, 100, 1000, 700)

        # Store flyout references
        self.flyouts = {}

        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        """Setup the advanced demo interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Advanced FlyoutWidget Demo - Flexible Anchoring")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        main_layout.addWidget(title)

        # Create demo sections
        sections_layout = QHBoxLayout()

        # Left column
        left_column = QVBoxLayout()
        left_column.addWidget(self.create_widget_anchor_demo())
        left_column.addWidget(self.create_edge_anchor_demo())

        # Right column
        right_column = QVBoxLayout()
        right_column.addWidget(self.create_point_anchor_demo())
        right_column.addWidget(self.create_custom_anchor_demo())

        sections_layout.addLayout(left_column)
        sections_layout.addLayout(right_column)
        main_layout.addLayout(sections_layout)

        # Interactive testing section
        main_layout.addWidget(self.create_interactive_test_section())

    def create_widget_anchor_demo(self):
        """Traditional widget anchoring demo."""
        group = QGroupBox("Widget Anchoring (Traditional)")
        layout = QVBoxLayout(group)

        desc = QLabel("Flyouts anchored to specific widgets:")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        buttons_layout = QHBoxLayout()

        # Different widget anchor examples
        btn1 = QPushButton("Right Flyout")
        content1 = QLabel("Anchored to button\n(Right direction)")
        content1.setStyleSheet("padding: 10px; background: #e3f2fd; border-radius: 4px;")
        flyout1 = FlyoutWidget.from_widget(btn1, FlyoutWidget.RIGHT, content1)
        btn1.clicked.connect(flyout1.toggle_flyout)
        buttons_layout.addWidget(btn1)
        self.flyouts["widget_right"] = flyout1

        btn2 = QPushButton("Bottom Flyout")
        content2 = QLabel("Anchored to button\n(Bottom direction)")
        content2.setStyleSheet("padding: 10px; background: #f3e5f5; border-radius: 4px;")
        flyout2 = FlyoutWidget.from_widget(btn2, FlyoutWidget.BOTTOM, content2)
        btn2.clicked.connect(flyout2.toggle_flyout)
        buttons_layout.addWidget(btn2)
        self.flyouts["widget_bottom"] = flyout2

        layout.addLayout(buttons_layout)
        return group

    def create_point_anchor_demo(self):
        """Point anchoring demo."""
        group = QGroupBox("Point Anchoring (Coordinates)")
        layout = QVBoxLayout(group)

        desc = QLabel("Flyouts anchored to specific screen coordinates:")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Coordinate controls
        coords_layout = QFormLayout()
        self.point_x_spin = QSpinBox()
        self.point_x_spin.setRange(0, 2000)
        self.point_x_spin.setValue(400)
        coords_layout.addRow("X:", self.point_x_spin)

        self.point_y_spin = QSpinBox()
        self.point_y_spin.setRange(0, 2000)
        self.point_y_spin.setValue(300)
        coords_layout.addRow("Y:", self.point_y_spin)

        layout.addLayout(coords_layout)

        point_btn = QPushButton("Show at Coordinates")
        point_content = QLabel("Flyout at specific\ncoordinates!")
        point_content.setStyleSheet("padding: 15px; background: #e8f5e8; border-radius: 4px;")

        def show_point_flyout():
            x = self.point_x_spin.value()
            y = self.point_y_spin.value()
            # Create new flyout with updated coordinates
            flyout = FlyoutWidget.from_point(x, y, FlyoutWidget.RIGHT, point_content)
            flyout.toggle_flyout()
            self.flyouts["point_current"] = flyout

        point_btn.clicked.connect(show_point_flyout)
        layout.addWidget(point_btn)

        return group

    def create_edge_anchor_demo(self):
        """Edge anchoring demo (sidebar style)."""
        group = QGroupBox("Edge Anchoring (Off-Screen Sliding)")
        layout = QVBoxLayout(group)

        desc = QLabel("Flyouts that slide in from window/screen edges:")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        edges_layout = QGridLayout()

        edges = [
            ("Left Edge", "left", 0, 0),
            ("Right Edge", "right", 0, 1),
            ("Top Edge", "top", 1, 0),
            ("Bottom Edge", "bottom", 1, 1)
        ]

        for name, edge, row, col in edges:
            btn = QPushButton(name)
            content = QLabel(f"Sliding from {edge} edge\nLike a sidebar!")
            content.setStyleSheet("""
                padding: 20px;
                background: #fff3e0;
                border-radius: 6px;
                min-width: 200px;
                min-height: 100px;
            """)

            flyout = FlyoutWidget.from_edge(edge, content, parent=self)
            btn.clicked.connect(flyout.toggle_flyout)
            edges_layout.addWidget(btn, row, col)
            self.flyouts[f"edge_{edge}"] = flyout

        layout.addLayout(edges_layout)
        return group

    def create_custom_anchor_demo(self):
        """Custom anchoring demo."""
        group = QGroupBox("Custom Anchoring (Precise Control)")
        layout = QVBoxLayout(group)

        desc = QLabel("Flyouts with custom start/end positions:")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Custom position controls
        custom_layout = QFormLayout()

        self.start_x_spin = QSpinBox()
        self.start_x_spin.setRange(-100, 2000)
        self.start_x_spin.setValue(600)
        custom_layout.addRow("Start X:", self.start_x_spin)

        self.start_y_spin = QSpinBox()
        self.start_y_spin.setRange(-100, 2000)
        self.start_y_spin.setValue(200)
        custom_layout.addRow("Start Y:", self.start_y_spin)

        self.end_x_spin = QSpinBox()
        self.end_x_spin.setRange(0, 2000)
        self.end_x_spin.setValue(700)
        custom_layout.addRow("End X:", self.end_x_spin)

        self.end_y_spin = QSpinBox()
        self.end_y_spin.setRange(0, 2000)
        self.end_y_spin.setValue(250)
        custom_layout.addRow("End Y:", self.end_y_spin)

        layout.addLayout(custom_layout)

        custom_btn = QPushButton("Show Custom Flyout")
        custom_content = QLabel("Custom positioned\nflyout with precise\nstart/end control!")
        custom_content.setStyleSheet("padding: 15px; background: #fce4ec; border-radius: 4px;")

        def show_custom_flyout():
            start = QPoint(self.start_x_spin.value(), self.start_y_spin.value())
            end = QPoint(self.end_x_spin.value(), self.end_y_spin.value())
            flyout = FlyoutWidget.from_custom(start, end, custom_content)
            flyout.toggle_flyout()
            self.flyouts["custom_current"] = flyout

        custom_btn.clicked.connect(show_custom_flyout)
        layout.addWidget(custom_btn)

        return group

    def create_interactive_test_section(self):
        """Interactive testing section with advanced features."""
        group = QGroupBox("Interactive Testing & Advanced Features")
        layout = QHBoxLayout(group)

        # Left side - Controls
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)

        controls_layout.addWidget(QLabel("Dynamic Flyout Builder:"))

        # Anchor mode selection
        mode_layout = QFormLayout()
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Widget", "Point", "Edge", "Custom"])
        mode_layout.addRow("Anchor Mode:", self.mode_combo)

        # Direction selection
        self.direction_combo = QComboBox()
        self.direction_combo.addItems(["RIGHT", "LEFT", "TOP", "BOTTOM"])
        mode_layout.addRow("Direction:", self.direction_combo)

        # Duration control
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(100, 3000)
        self.duration_spin.setValue(400)
        mode_layout.addRow("Duration (ms):", self.duration_spin)

        # Margin control
        self.margin_spin = QSpinBox()
        self.margin_spin.setRange(0, 100)
        self.margin_spin.setValue(10)
        mode_layout.addRow("Margin:", self.margin_spin)

        controls_layout.addLayout(mode_layout)

        # Test button
        test_btn = QPushButton("Create Test Flyout")
        test_btn.setStyleSheet("""
            QPushButton {
                background: #4caf50;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover { background: #45a049; }
        """)
        test_btn.clicked.connect(self.create_test_flyout)
        controls_layout.addWidget(test_btn)

        layout.addWidget(controls_widget)

        # Right side - Advanced features
        advanced_widget = QWidget()
        advanced_layout = QVBoxLayout(advanced_widget)

        advanced_layout.addWidget(QLabel("Advanced Features:"))

        # Chained flyouts demo
        chain_btn = QPushButton("Chained Flyouts")
        chain_btn.clicked.connect(self.demo_chained_flyouts)
        advanced_layout.addWidget(chain_btn)

        # Auto-positioning demo
        auto_btn = QPushButton("Auto-positioning Demo")
        auto_btn.clicked.connect(self.demo_auto_positioning)
        advanced_layout.addWidget(auto_btn)

        # Dynamic content demo
        dynamic_btn = QPushButton("Dynamic Content Updates")
        dynamic_btn.clicked.connect(self.demo_dynamic_content)
        advanced_layout.addWidget(dynamic_btn)

        # Multiple flyouts demo
        multi_btn = QPushButton("Multiple Flyouts")
        multi_btn.clicked.connect(self.demo_multiple_flyouts)
        advanced_layout.addWidget(multi_btn)

        layout.addWidget(advanced_widget)

        return group

    def create_test_flyout(self):
        """Create a test flyout based on current settings."""
        mode = self.mode_combo.currentText().lower()
        direction_map = {
            "RIGHT": FlyoutWidget.RIGHT,
            "LEFT": FlyoutWidget.LEFT,
            "TOP": FlyoutWidget.TOP,
            "BOTTOM": FlyoutWidget.BOTTOM
        }
        direction = direction_map[self.direction_combo.currentText()]
        duration = self.duration_spin.value()
        margin = self.margin_spin.value()

        content = QLabel(f"Test Flyout\nMode: {mode}\nDirection: {self.direction_combo.currentText()}")
        content.setStyleSheet("padding: 15px; background: #e1f5fe; border-radius: 4px;")

        if mode == "widget":
            flyout = FlyoutWidget.from_widget(
                self.sender() if hasattr(self, 'sender') else self.findChild(QPushButton),
                direction, content, duration=duration, margin=margin
            )
        elif mode == "point":
            flyout = FlyoutWidget.from_point(
                500, 350, direction, content, duration=duration, margin=margin
            )
        elif mode == "edge":
            edge_map = {"RIGHT": "right", "LEFT": "left", "TOP": "top", "BOTTOM": "bottom"}
            edge = edge_map[self.direction_combo.currentText()]
            flyout = FlyoutWidget.from_edge(
                edge, content, parent=self, duration=duration, margin=margin
            )
        else:  # custom
            start = QPoint(400, 200)
            end = QPoint(500, 250)
            flyout = FlyoutWidget.from_custom(
                start, end, content, duration=duration, margin=margin
            )

        flyout.toggle_flyout()
        self.flyouts["test_current"] = flyout

    def demo_chained_flyouts(self):
        """Demonstrate chained flyouts."""
        # First flyout
        first_widget = QWidget()
        first_layout = QVBoxLayout(first_widget)
        first_layout.addWidget(QLabel("First Flyout"))

        second_btn = QPushButton("Open Second")
        first_layout.addWidget(second_btn)

        first_flyout = FlyoutWidget.from_edge("right", first_widget, parent=self)

        # Second flyout (chained from first)
        second_content = QLabel("Second Flyout\n(Chained from first)")
        second_content.setStyleSheet("padding: 15px; background: #f3e5f5; border-radius: 4px;")
        second_flyout = FlyoutWidget.from_point(600, 300, FlyoutWidget.RIGHT, second_content)

        second_btn.clicked.connect(second_flyout.toggle_flyout)
        first_flyout.toggle_flyout()

        self.flyouts["chain_first"] = first_flyout
        self.flyouts["chain_second"] = second_flyout

    def demo_auto_positioning(self):
        """Demonstrate automatic positioning based on screen space."""
        content = QLabel("Auto-positioned flyout\nAdjusts based on available space")
        content.setStyleSheet("padding: 15px; background: #e8f5e8; border-radius: 4px;")

        # Try right first, fall back to left if not enough space
        screen_geometry = QApplication.primaryScreen().geometry()
        mouse_pos = self.mapFromGlobal(self.cursor().pos())

        if mouse_pos.x() + 200 < screen_geometry.width():
            flyout = FlyoutWidget.from_point(mouse_pos.x(), mouse_pos.y(), FlyoutWidget.RIGHT, content)
        else:
            flyout = FlyoutWidget.from_point(mouse_pos.x(), mouse_pos.y(), FlyoutWidget.LEFT, content)

        flyout.toggle_flyout()
        self.flyouts["auto_positioned"] = flyout

    def demo_dynamic_content(self):
        """Demonstrate dynamic content updates."""
        self.update_counter = 0

        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.dynamic_label = QLabel(f"Dynamic Content #{self.update_counter}")
        layout.addWidget(self.dynamic_label)

        update_btn = QPushButton("Update Content")
        layout.addWidget(update_btn)

        def update_content():
            self.update_counter += 1
            self.dynamic_label.setText(f"Dynamic Content #{self.update_counter}")

        update_btn.clicked.connect(update_content)

        flyout = FlyoutWidget.from_edge("left", widget, parent=self)
        flyout.toggle_flyout()
        self.flyouts["dynamic"] = flyout

    def demo_multiple_flyouts(self):
        """Demonstrate multiple simultaneous flyouts."""
        positions = [
            ("top", FlyoutWidget.from_edge("top", QLabel("Top Flyout"), parent=self)),
            ("bottom", FlyoutWidget.from_edge("bottom", QLabel("Bottom Flyout"), parent=self)),
            ("left", FlyoutWidget.from_edge("left", QLabel("Left Flyout"), parent=self)),
            ("right", FlyoutWidget.from_edge("right", QLabel("Right Flyout"), parent=self))
        ]

        for name, flyout in positions:
            flyout.toggle_flyout()
            self.flyouts[f"multi_{name}"] = flyout

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
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QSpinBox, QComboBox {
                padding: 4px;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
        """)

    def closeEvent(self, event):
        """Clean up when closing."""
        for flyout in self.flyouts.values():
            if flyout._visible:
                flyout.hide()
        event.accept()


def main():
    """Run the advanced flyout demo."""
    app = QApplication(sys.argv)

    app.setApplicationName("Advanced FlyoutWidget Demo")
    app.setApplicationVersion("2.0")

    demo = AdvancedFlyoutDemo()
    demo.show()

    DebugLogger.log("Advanced FlyoutWidget Demo started", "info")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
