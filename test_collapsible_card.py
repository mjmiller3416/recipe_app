"""Debug app to test Card widget collapse animation issues.

Testing the actual Card widget implementation to identify animation jerkiness.
"""

import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QCheckBox
)

from dev_tools.debug_logger import DebugLogger
from app.ui.components.layout.card import Card
from app.style.theme_controller import Theme
from app.style.theme.config import Mode


# ── Main Window ──────────────────────────────────────────────────────────────────────
class CardDebugWindow(QMainWindow):
    """Window to test actual Card widget collapse animation."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Card Animation Debug")
        self.setGeometry(100, 100, 600, 500)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # Create actual Card widget
        self.test_card = Card()
        self.test_card.setHeader("Actual Card Widget")

        # Add some content to the card FIRST
        self.test_card.addWidget(QLabel("Content line 1"))
        text_edit = QTextEdit("Some text content that should animate smoothly...")
        text_edit.setMaximumHeight(100)
        self.test_card.addWidget(text_edit)
        self.test_card.addWidget(QPushButton("A button in the card"))

        # Enable collapsible AFTER adding content
        self.test_card.enableCollapsible(True)

        main_layout.addWidget(self.test_card, 2)

        # Controls
        controls = QWidget()
        controls_layout = QVBoxLayout(controls)
        controls.setMaximumWidth(200)

        controls_layout.addWidget(QLabel("<b>Card Controls:</b>"))

        # Manual collapse/expand buttons
        collapse_btn = QPushButton("Collapse")
        collapse_btn.clicked.connect(lambda: self.test_card.setCollapsed(True))
        controls_layout.addWidget(collapse_btn)

        expand_btn = QPushButton("Expand")
        expand_btn.clicked.connect(lambda: self.test_card.setCollapsed(False))
        controls_layout.addWidget(expand_btn)

        # Toggle button for quick testing (like sidebar)
        toggle_btn = QPushButton("Toggle")
        toggle_btn.clicked.connect(self.test_card.toggle)
        controls_layout.addWidget(toggle_btn)

        controls_layout.addStretch()
        main_layout.addWidget(controls)
        DebugLogger.log(f"Card height: {self.test_card.height()}", "error")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Initialize theme manager as requested
    Theme.setCustomColorMap("material-theme.json", Mode.DARK)

    window = CardDebugWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
