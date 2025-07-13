"""scripts/simple_flyout_test.py

Simple test script for the FlyoutWidget showing basic functionality.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt

from app.ui.components.layout.flyout_widget import FlyoutWidget


class SimpleFlyoutTest(QMainWindow):
    """Simple test window for FlyoutWidget."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple FlyoutWidget Test")
        self.setGeometry(200, 200, 400, 300)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignCenter)

        # Test buttons
        self.test_button = QPushButton("Widget Anchor Flyout")
        self.test_button.setFixedSize(200, 50)
        layout.addWidget(self.test_button)

        # Add more test buttons for different anchor modes
        self.point_button = QPushButton("Point Anchor Flyout")
        self.point_button.setFixedSize(200, 50)
        layout.addWidget(self.point_button)

        self.edge_button = QPushButton("Edge Anchor Flyout")
        self.edge_button.setFixedSize(200, 50)
        layout.addWidget(self.edge_button)

        # Create flyout using improved anchoring
        flyout_content = QLabel("Hello from the flyout!\nNow with precise anchoring!")
        flyout_content.setAlignment(Qt.AlignCenter)
        flyout_content.setStyleSheet("""
            QLabel {
                background-color: #e8f4f8;
                border: 2px solid #3498db;
                border-radius: 8px;
                padding: 15px;
                font-size: 14px;
                min-width: 180px;
                min-height: 80px;
            }
        """)

        # Using the new factory method for cleaner code
        self.flyout = FlyoutWidget.from_widget(
            anchor_widget=self.test_button,
            direction=FlyoutWidget.RIGHT,
            content=flyout_content,
            duration=350,
            margin=10
        )

        # Connect buttons to flyouts
        self.test_button.clicked.connect(self.flyout.toggle_flyout)

        # Point anchor flyout
        point_content = QLabel("Anchored to coordinates\n(300, 200)")
        point_content.setStyleSheet("padding: 15px; background: #f3e5f5; border-radius: 4px;")
        self.point_flyout = FlyoutWidget.from_point(
            x=300, y=200,
            direction=FlyoutWidget.BOTTOM,
            content=point_content
        )
        self.point_button.clicked.connect(self.point_flyout.toggle_flyout)

        # Edge anchor flyout (sidebar style) - now with improved anchoring!
        edge_content = QLabel("Sliding from left edge\nNow properly anchored to THIS window!\nTry resizing/moving the window.")
        edge_content.setStyleSheet("padding: 20px; background: #e8f5e8; border-radius: 4px;")
        self.edge_flyout = FlyoutWidget.from_edge(
            edge="left",
            content=edge_content,
            parent=self,
            auto_reposition=True  # Automatically repositions when window moves/resizes
        )
        self.edge_button.clicked.connect(self.edge_flyout.toggle_flyout)

        # Apply styles
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)


def main():
    """Run the simple flyout test."""
    app = QApplication(sys.argv)

    window = SimpleFlyoutTest()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
