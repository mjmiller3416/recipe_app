"""simple_combobox_test.py

Simple test app to display the ComboBox widget with custom theme applied.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QFrame, QSizePolicy
)
from PySide6.QtGui import QFont

from app.style.theme_controller import Theme, Mode
from app.ui.components.widgets.combobox import ComboBox


class SimpleComboBoxTest(QMainWindow):
    """Simple test window for the ComboBox widget with theme."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple ComboBox Test")
        self.setObjectName("SimpleComboBoxTest")
        self.setFixedSize(400, 300)

        # Apply theme
        Theme.setCustomColorMap("material-theme.json", Mode.DARK)

        # Main container widget
        container = QWidget()
        self.setCentralWidget(container)

        # Create layout
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title label
        title = QLabel("ComboBox Widget Test")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        # Test ComboBox with fruits
        fruits = ["Apple", "Banana", "Cherry", "Date", "Elderberry", "Fig", "Grape", "Honeydew", "Kiwi", "Lemon"]
        combo1 = ComboBox(list_items=fruits, placeholder="Choose a fruit...")
        combo1.setObjectName("FruitCombo")
        layout.addWidget(combo1)

        # Test ComboBox with colors
        colors = ["Red", "Green", "Blue", "Yellow", "Purple", "Orange", "Pink", "Black", "White"]
        combo2 = ComboBox(list_items=colors, placeholder="Choose a color...")
        combo2.setObjectName("ColorCombo")
        layout.addWidget(combo2)

        # Test empty ComboBox
        combo3 = ComboBox(placeholder="Empty combo box...")
        combo3.setObjectName("EmptyCombo")
        layout.addWidget(combo3)

        # Add some items to the empty combo box
        for item in ["Option 1", "Option 2", "Option 3"]:
            combo3.addItem(item)

        # Add stretch to push everything to the top
        layout.addStretch()

        # Connect signals for testing
        combo1.currentTextChanged.connect(lambda text: print(f"Fruit selected: {text}"))
        combo2.currentTextChanged.connect(lambda text: print(f"Color selected: {text}"))
        combo3.currentTextChanged.connect(lambda text: print(f"Option selected: {text}"))


def main():
    """Main function to run the test app."""
    app = QApplication(sys.argv)
    app.setApplicationName("Simple ComboBox Test")

    # Create and show the test window
    window = SimpleComboBoxTest()
    window.show()

    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
