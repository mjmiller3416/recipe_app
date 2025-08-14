"""simple_flyout_test.py

Simple test app to demonstrate the FlyoutWidget with custom theme applied.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QTextEdit
)
from PySide6.QtGui import QFont

from app.style.theme_controller import Theme, Mode
from app.ui.components.layout.flyout_widget import FlyoutWidget


class SimpleFlyoutTest(QMainWindow):
    """Simple test window for the FlyoutWidget with theme."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple FlyoutWidget Test")
        self.setObjectName("SimpleFlyoutTest")
        self.setGeometry(100, 100, 600, 400)

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
        title = QLabel("FlyoutWidget Demonstration")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        # Create buttons for different flyout types
        self._create_flyout_demos(layout)

        # Add stretch to push everything to the top
        layout.addStretch()

    def _create_flyout_demos(self, layout):
        """Create demo buttons for different flyout anchoring modes."""

        # 1. Widget Anchor Flyout (RIGHT)
        button1 = QPushButton("Widget Anchor Flyout (Right)")
        button1.setObjectName("WidgetAnchorButton")
        layout.addWidget(button1)

        content1 = self._create_flyout_content("Widget-anchored flyout\nSlides from the right side\nof the button")
        flyout1 = FlyoutWidget.from_widget(button1, FlyoutWidget.RIGHT, content1)
        button1.clicked.connect(flyout1.toggle_flyout)

        # 2. Widget Anchor Flyout (BOTTOM)
        button2 = QPushButton("Widget Anchor Flyout (Bottom)")
        button2.setObjectName("WidgetAnchorBottomButton")
        layout.addWidget(button2)

        content2 = self._create_flyout_content("Widget-anchored flyout\nSlides from the bottom\nof the button")
        flyout2 = FlyoutWidget.from_widget(button2, FlyoutWidget.BOTTOM, content2)
        button2.clicked.connect(flyout2.toggle_flyout)

        # 3. Point Anchor Flyout
        button3 = QPushButton("Point Anchor Flyout")
        button3.setObjectName("PointAnchorButton")
        layout.addWidget(button3)

        content3 = self._create_flyout_content("Point-anchored flyout\nAnchored to specific\ncoordinates (300, 200)")
        flyout3 = FlyoutWidget.from_point(300, 200, FlyoutWidget.BOTTOM, content3)
        button3.clicked.connect(flyout3.toggle_flyout)

        # 4. Edge Anchor Flyout (Left)
        button4 = QPushButton("Edge Anchor Flyout (Left)")
        button4.setObjectName("EdgeAnchorButton")
        layout.addWidget(button4)

        content4 = self._create_flyout_content("Edge-anchored flyout\nSlides from the left\nedge of the window")
        flyout4 = FlyoutWidget.from_edge("left", content4, parent=self)
        button4.clicked.connect(flyout4.toggle_flyout)

        # 5. Edge Anchor Flyout (Right)
        button5 = QPushButton("Edge Anchor Flyout (Right)")
        button5.setObjectName("EdgeAnchorRightButton")
        layout.addWidget(button5)

        content5 = self._create_flyout_content("Edge-anchored flyout\nSlides from the right\nedge of the window")
        flyout5 = FlyoutWidget.from_edge("right", content5, parent=self)
        button5.clicked.connect(flyout5.toggle_flyout)

        # 6. Custom Anchor Flyout
        button6 = QPushButton("Custom Anchor Flyout")
        button6.setObjectName("CustomAnchorButton")
        layout.addWidget(button6)

        content6 = self._create_flyout_content("Custom-anchored flyout\nWith custom start/end\npositions")
        from PySide6.QtCore import QPoint
        start_point = QPoint(100, 100)
        end_point = QPoint(250, 150)
        flyout6 = FlyoutWidget.from_custom(start_point, end_point, content6)
        button6.clicked.connect(flyout6.toggle_flyout)

    def _create_flyout_content(self, text: str) -> QWidget:
        """Create content widget for flyout."""
        frame = QFrame()
        frame.setObjectName("FlyoutContent")
        frame.setFrameStyle(QFrame.StyledPanel)
        frame.setFixedSize(200, 120)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)

        label = QLabel(text)
        label.setObjectName("FlyoutLabel")
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)
        layout.addWidget(label)

        # Add a close button
        close_btn = QPushButton("Close")
        close_btn.setObjectName("FlyoutCloseButton")
        close_btn.setMaximumWidth(80)
        layout.addWidget(close_btn)

        # Connect close button to hide the flyout
        def close_flyout():
            # Find the parent flyout widget
            parent = frame.parent()
            while parent and not isinstance(parent, FlyoutWidget):
                parent = parent.parent()
            if parent and isinstance(parent, FlyoutWidget):
                parent.setVisibleAnimated(False)

        close_btn.clicked.connect(close_flyout)

        return frame


def main():
    """Main function to run the test app."""
    app = QApplication(sys.argv)
    app.setApplicationName("Simple FlyoutWidget Test")

    # Create and show the test window
    window = SimpleFlyoutTest()
    window.show()

    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
