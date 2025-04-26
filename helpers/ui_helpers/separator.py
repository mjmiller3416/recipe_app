# helpers/separator.py

#🔸Third-pary
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QScrollArea,
                               QSizePolicy, QVBoxLayout, QWidget)

# ────────────────────────────────────────────────────────────────────────────────


class Separator(QWidget):
    """
    A 1-pixel‐wide vertical separator drawn at integer‐pixel coordinates
    for perfectly crisp rendering every time.
    """

    def __init__(self, height=60, color="#4a4a4a", parent=None):
        super().__init__(parent)
        self._color = QColor(color)
        self.setFixedSize(1, height)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # no need for WA_TransparentForMouseEvents here

    def paintEvent(self, event):
        p = QPainter(self)
        # draw a full-pixel rectangle at x=0
        p.fillRect(0, 0, 1, self.height(), self._color)
        p.end()


def create_test_widget():
    """
    Build a simple column of example rows, each with:
      [ Label ] [ Separator ] [ Label ]
    so you can see the Separator in context.
    """
    container = QWidget()
    vbox = QVBoxLayout(container)
    vbox.setSpacing(20)
    vbox.setContentsMargins(10, 10, 10, 10)

    for i in range(3):
        row = QHBoxLayout()
        row.setSpacing(10)

        left = QLabel(f"Left {i+1}")
        left.setStyleSheet("background: #333; color: #fff; padding: 8px;")
        row.addWidget(left, 1)

        sep = Separator(height=40, color="#4a4a4a")
        row.addWidget(sep)

        right = QLabel(f"Right {i+1}")
        right.setStyleSheet("background: #333; color: #fff; padding: 8px;")
        row.addWidget(right, 1)

        vbox.addLayout(row)

    return container


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    # Put it all in a scrollable window
    window = QScrollArea()
    window.setWindowTitle("Separator Test")
    window.setWidgetResizable(True)
    window.setMinimumSize(400, 300)

    test = create_test_widget()
    window.setWidget(test)
    window.show()

    sys.exit(app.exec())
