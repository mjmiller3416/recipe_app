"""scripts/test_edge_anchoring.py

Test script specifically for edge anchoring improvements to verify consistent behavior
when resizing and repositioning the application window.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QGroupBox, QTextEdit
)
from PySide6.QtCore import Qt

from app.ui.components.layout.flyout_widget import FlyoutWidget
from dev_tools import DebugLogger


class EdgeAnchoringTest(QMainWindow):
    """Test window specifically for edge anchoring behavior."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Edge Anchoring Test - Resize & Move Window to Test")
        self.setGeometry(200, 200, 600, 400)

        # Store flyout references
        self.flyouts = {}

        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        """Setup the test interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Edge Anchoring Test")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 20px;")
        main_layout.addWidget(title)

        # Instructions
        instructions = QLabel(
            "Test Instructions:\n"
            "1. Click the edge buttons to show flyouts\n"
            "2. Try resizing the window while flyouts are visible\n"
            "3. Try moving the window while flyouts are visible\n"
            "4. Verify flyouts stay anchored to THIS window's edges"
        )
        instructions.setStyleSheet("background: #f0f8ff; padding: 10px; border-radius: 5px;")
        instructions.setWordWrap(True)
        main_layout.addWidget(instructions)

        # Edge buttons
        edge_group = QGroupBox("Edge Anchoring Tests")
        edge_layout = QVBoxLayout(edge_group)

        # Top/Bottom row
        top_bottom_layout = QHBoxLayout()

        self.top_btn = QPushButton("Show TOP Edge Flyout")
        self.bottom_btn = QPushButton("Show BOTTOM Edge Flyout")
        top_bottom_layout.addWidget(self.top_btn)
        top_bottom_layout.addWidget(self.bottom_btn)
        edge_layout.addLayout(top_bottom_layout)

        # Left/Right row
        left_right_layout = QHBoxLayout()

        self.left_btn = QPushButton("Show LEFT Edge Flyout")
        self.right_btn = QPushButton("Show RIGHT Edge Flyout")
        left_right_layout.addWidget(self.left_btn)
        left_right_layout.addWidget(self.right_btn)
        edge_layout.addLayout(left_right_layout)

        # All edges button
        self.all_btn = QPushButton("Show ALL Edge Flyouts")
        self.all_btn.setStyleSheet("background: #4caf50; font-weight: bold;")
        edge_layout.addWidget(self.all_btn)

        # Hide all button
        self.hide_all_btn = QPushButton("Hide All Flyouts")
        self.hide_all_btn.setStyleSheet("background: #f44336; color: white; font-weight: bold;")
        edge_layout.addWidget(self.hide_all_btn)

        main_layout.addWidget(edge_group)

        # Status area
        status_group = QGroupBox("Status & Debug Info")
        status_layout = QVBoxLayout(status_group)

        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(100)
        self.status_text.setReadOnly(True)
        status_layout.addWidget(self.status_text)

        main_layout.addWidget(status_group)

        # Setup flyouts and connections
        self.setup_flyouts()
        self.setup_connections()

    def setup_flyouts(self):
        """Create edge flyouts with debug content."""

        # TOP edge flyout
        top_content = QLabel("TOP Edge Flyout\nShould slide from window top edge\nand stay anchored during resize/move")
        top_content.setAlignment(Qt.AlignCenter)
        top_content.setStyleSheet("""
            background: #ffeb3b;
            padding: 15px;
            border-radius: 6px;
            border: 2px solid #fbc02d;
            min-width: 200px;
        """)
        self.flyouts['top'] = FlyoutWidget.from_edge("top", top_content, parent=self)

        # BOTTOM edge flyout
        bottom_content = QLabel("BOTTOM Edge Flyout\nShould slide from window bottom edge\nand stay anchored during resize/move")
        bottom_content.setAlignment(Qt.AlignCenter)
        bottom_content.setStyleSheet("""
            background: #ff5722;
            color: white;
            padding: 15px;
            border-radius: 6px;
            border: 2px solid #d84315;
            min-width: 200px;
        """)
        self.flyouts['bottom'] = FlyoutWidget.from_edge("bottom", bottom_content, parent=self)

        # LEFT edge flyout
        left_content = QLabel("LEFT Edge Flyout\nSlides from window left edge\nStays anchored during resize/move")
        left_content.setAlignment(Qt.AlignCenter)
        left_content.setStyleSheet("""
            background: #4caf50;
            color: white;
            padding: 15px;
            border-radius: 6px;
            border: 2px solid #388e3c;
            min-width: 150px;
            min-height: 100px;
        """)
        self.flyouts['left'] = FlyoutWidget.from_edge("left", left_content, parent=self)

        # RIGHT edge flyout
        right_content = QLabel("RIGHT Edge Flyout\nSlides from window right edge\nStays anchored during resize/move")
        right_content.setAlignment(Qt.AlignCenter)
        right_content.setStyleSheet("""
            background: #2196f3;
            color: white;
            padding: 15px;
            border-radius: 6px;
            border: 2px solid #1976d2;
            min-width: 150px;
            min-height: 100px;
        """)
        self.flyouts['right'] = FlyoutWidget.from_edge("right", right_content, parent=self)

    def setup_connections(self):
        """Connect buttons to flyout actions."""
        self.top_btn.clicked.connect(lambda: self.toggle_flyout('top'))
        self.bottom_btn.clicked.connect(lambda: self.toggle_flyout('bottom'))
        self.left_btn.clicked.connect(lambda: self.toggle_flyout('left'))
        self.right_btn.clicked.connect(lambda: self.toggle_flyout('right'))

        self.all_btn.clicked.connect(self.show_all_flyouts)
        self.hide_all_btn.clicked.connect(self.hide_all_flyouts)

    def toggle_flyout(self, edge):
        """Toggle a specific edge flyout and log debug info."""
        flyout = self.flyouts.get(edge)
        if flyout:
            flyout.toggle_flyout()

            # Log window geometry for debugging
            window_geo = self.geometry()
            self.log_status(f"Toggled {edge.upper()} flyout")
            self.log_status(f"Window geometry: {window_geo.x()}, {window_geo.y()}, {window_geo.width()}x{window_geo.height()}")

    def show_all_flyouts(self):
        """Show all edge flyouts simultaneously."""
        self.log_status("Showing all edge flyouts...")
        for edge, flyout in self.flyouts.items():
            if not flyout._visible:
                flyout.setVisibleAnimated(True)

    def hide_all_flyouts(self):
        """Hide all flyouts."""
        self.log_status("Hiding all flyouts...")
        for edge, flyout in self.flyouts.items():
            if flyout._visible:
                flyout.setVisibleAnimated(False)

    def log_status(self, message):
        """Log a status message to the debug area."""
        self.status_text.append(message)
        DebugLogger.log(f"EdgeAnchoringTest: {message}", "debug")

    def resizeEvent(self, event):
        """Handle window resize events."""
        super().resizeEvent(event)
        self.log_status(f"Window resized to: {event.size().width()}x{event.size().height()}")

        # Recalculate positions for all visible edge flyouts
        for edge, flyout in self.flyouts.items():
            if flyout._visible:
                flyout.recalculate_position()

    def moveEvent(self, event):
        """Handle window move events."""
        super().moveEvent(event)
        self.log_status(f"Window moved to: {event.pos().x()}, {event.pos().y()}")

        # Recalculate positions for all visible edge flyouts
        for edge, flyout in self.flyouts.items():
            if flyout._visible:
                flyout.recalculate_position()

    def apply_styles(self):
        """Apply styling to the test window."""
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
                padding: 10px 16px;
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
        """)

    def closeEvent(self, event):
        """Clean up when closing."""
        for flyout in self.flyouts.values():
            if flyout._visible:
                flyout.hide()
        event.accept()


def main():
    """Run the edge anchoring test."""
    app = QApplication(sys.argv)

    app.setApplicationName("Edge Anchoring Test")

    test = EdgeAnchoringTest()
    test.show()

    DebugLogger.log("Edge Anchoring Test started - Test resizing and moving the window!", "info")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
