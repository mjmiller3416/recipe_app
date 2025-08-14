"""test_combobox.py

Test demo for the ComboBox widget.
Shows various combo boxes with different configurations and demonstrates functionality.
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
    QTextEdit, QScrollArea
)
from PySide6.QtGui import QFont

from app.style.theme_controller import Theme, Mode, Color
from app.ui.components.widgets.combobox import ComboBox


class ComboBoxDemo(QMainWindow):
    """Demo window for testing the ComboBox widget."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ComboBox Widget Demo")
        self.setObjectName("ComboBoxDemo")
        self.setFixedSize(800, 800)

        # Main container widget
        container = QWidget()
        self.setCentralWidget(container)

        # Create and set layout for container
        layout = QVBoxLayout(container)

        fruits = ["Apple", "Banana", "Cherry", "Date", "Elderberry", "Fig", "Grape"]
        combo = ComboBox(list_items=fruits, placeholder="Choose a fruit...")

        # add ComboBox to layout
        layout.addWidget(combo)


def run_test(app):
    """Entry point for the test harness."""
    window = ComboBoxDemo()
    return window


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = run_test(app)
    window.show()
    sys.exit(app.exec())
