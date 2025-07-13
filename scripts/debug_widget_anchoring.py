"""scripts/debug_widget_anchoring.py

Debug script to examine widget anchoring behavior and coordinate calculations.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QGroupBox
)
from PySide6.QtCore import Qt, QPoint, QRect
from PySide6.QtGui import QPainter, QPen

from app.ui.components.layout.flyout_widget import FlyoutWidget
from dev_tools import DebugLogger


class DebugFlyoutWidget(FlyoutWidget):
    """Debug version of FlyoutWidget that logs coordinate calculations."""

    def _calculate_widget_positions(self, width: int, height: int) -> tuple[QPoint, QPoint]:
        """Calculate positions for widget-based anchoring with debug logging."""
        # Get the anchor widget's global position correctly
        anchor_global_pos = self.anchor.mapToGlobal(QPoint(0, 0))
        anchor_size = self.anchor.size()
        anchor_global = QRect(anchor_global_pos, anchor_size)

        print(f"\n=== Widget Anchoring Debug ===")
        print(f"Anchor widget size: {anchor_size}")
        print(f"Anchor widget global position: {anchor_global_pos}")
        print(f"Anchor widget global rect: {anchor_global}")
        print(f"Flyout size: {width}x{height}")
        print(f"Direction: {self.direction}")
        print(f"Margin: {self.margin}")

        if self.direction == self.RIGHT:
            end_x = anchor_global.right() + self.margin
            end_y = anchor_global.top()
            start = QPoint(end_x + width, end_y)
            end = QPoint(end_x, end_y)
            print(f"RIGHT: end_x={end_x}, end_y={end_y}")
        elif self.direction == self.LEFT:
            end_x = anchor_global.left() - width - self.margin
            end_y = anchor_global.top()
            start = QPoint(end_x - width, end_y)
            end = QPoint(end_x, end_y)
            print(f"LEFT: end_x={end_x}, end_y={end_y}")
        elif self.direction == self.BOTTOM:
            end_x = anchor_global.left()
            end_y = anchor_global.bottom() + self.margin
            start = QPoint(end_x, end_y + height)
            end = QPoint(end_x, end_y)
            print(f"BOTTOM: end_x={end_x}, end_y={end_y}")
        else:  # TOP
            end_x = anchor_global.left()
            end_y = anchor_global.top() - height - self.margin
            start = QPoint(end_x, end_y - height)
            end = QPoint(end_x, end_y)
            print(f"TOP: end_x={end_x}, end_y={end_y}")

        print(f"Animation: start={start} -> end={end}")
        print("================================\n")

        return start, end


class DebugWidget(QWidget):
    """Widget that shows its boundaries for debugging."""

    def __init__(self, text="Debug Widget"):
        super().__init__()
        self.text = text
        self.setMinimumSize(100, 50)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)

        # Draw border
        pen = QPen(Qt.red, 2)
        painter.setPen(pen)
        painter.drawRect(self.rect())

        # Draw corner markers
        painter.fillRect(0, 0, 5, 5, Qt.red)  # Top-left
        painter.fillRect(self.width()-5, 0, 5, 5, Qt.blue)  # Top-right
        painter.fillRect(0, self.height()-5, 5, 5, Qt.green)  # Bottom-left
        painter.fillRect(self.width()-5, self.height()-5, 5, 5, Qt.yellow)  # Bottom-right

        # Draw text
        painter.setPen(Qt.black)
        painter.drawText(self.rect(), Qt.AlignCenter, self.text)


class DebugWidgetAnchoring(QMainWindow):
    """Debug window for widget anchoring behavior."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Debug Widget Anchoring")
        self.setGeometry(100, 100, 800, 600)

        self.flyouts = {}
        self.setup_ui()

    def setup_ui(self):
        """Setup the debug interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Widget Anchoring Debug")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        main_layout.addWidget(title)

        # Instructions
        instructions = QLabel(
            "Red corners = top-left, Blue = top-right, Green = bottom-left, Yellow = bottom-right\n"
            "Check console output for coordinate calculations."
        )
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("background: #f0f8ff; padding: 10px; border-radius: 5px;")
        main_layout.addWidget(instructions)

        # Test buttons with debug borders
        test_group = QGroupBox("Anchor Buttons (with visual boundaries)")
        test_layout = QVBoxLayout(test_group)

        # Button row
        button_layout = QHBoxLayout()

        # Create buttons with debug visualization
        self.right_btn = DebugWidget("RIGHT Flyout")
        self.right_btn.mousePressEvent = lambda e: self.show_right_flyout()
        button_layout.addWidget(self.right_btn)

        self.bottom_btn = DebugWidget("BOTTOM Flyout")
        self.bottom_btn.mousePressEvent = lambda e: self.show_bottom_flyout()
        button_layout.addWidget(self.bottom_btn)

        test_layout.addLayout(button_layout)

        # Info button
        info_btn = QPushButton("Print Button Positions")
        info_btn.clicked.connect(self.print_button_info)
        test_layout.addWidget(info_btn)

        main_layout.addWidget(test_group)

        # Setup flyouts
        self.setup_flyouts()

    def setup_flyouts(self):
        """Setup debug flyouts."""
        # RIGHT flyout
        right_content = QLabel("RIGHT Flyout\nShould appear to the right\nof the button with top edges aligned")
        right_content.setStyleSheet("padding: 15px; background: #e3f2fd; border: 2px solid #1976d2; border-radius: 4px;")
        self.right_flyout = DebugFlyoutWidget.from_widget(self.right_btn, FlyoutWidget.RIGHT, right_content)

        # BOTTOM flyout
        bottom_content = QLabel("BOTTOM Flyout\nShould appear below\nthe button with left edges aligned")
        bottom_content.setStyleSheet("padding: 15px; background: #f3e5f5; border: 2px solid #7b1fa2; border-radius: 4px;")
        self.bottom_flyout = DebugFlyoutWidget.from_widget(self.bottom_btn, FlyoutWidget.BOTTOM, bottom_content)

    def show_right_flyout(self):
        """Show the RIGHT flyout with debug info."""
        print(f"\n>>> Showing RIGHT flyout")
        self.print_widget_info(self.right_btn, "RIGHT Button")
        self.right_flyout.toggle_flyout()

    def show_bottom_flyout(self):
        """Show the BOTTOM flyout with debug info."""
        print(f"\n>>> Showing BOTTOM flyout")
        self.print_widget_info(self.bottom_btn, "BOTTOM Button")
        self.bottom_flyout.toggle_flyout()

    def print_button_info(self):
        """Print detailed information about button positions."""
        print(f"\n=== Button Position Info ===")
        self.print_widget_info(self.right_btn, "RIGHT Button")
        self.print_widget_info(self.bottom_btn, "BOTTOM Button")

        window_geo = self.geometry()
        print(f"Window geometry: {window_geo}")
        print("================================\n")

    def print_widget_info(self, widget, name):
        """Print detailed info about a widget's position."""
        local_geo = widget.geometry()
        global_top_left = widget.mapToGlobal(QPoint(0, 0))
        global_geo = QRect(global_top_left, local_geo.size())

        print(f"{name}:")
        print(f"  Local geometry: {local_geo}")
        print(f"  Global top-left: {global_top_left}")
        print(f"  Global geometry: {global_geo}")
        print(f"  Global corners:")
        print(f"    Top-left: {global_geo.topLeft()}")
        print(f"    Top-right: {global_geo.topRight()}")
        print(f"    Bottom-left: {global_geo.bottomLeft()}")
        print(f"    Bottom-right: {global_geo.bottomRight()}")


def main():
    """Run the debug widget anchoring test."""
    app = QApplication(sys.argv)

    debug_window = DebugWidgetAnchoring()
    debug_window.show()

    print("Debug Widget Anchoring Test Started")
    print("Click the colored widgets to see flyouts and check console for coordinate info")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
