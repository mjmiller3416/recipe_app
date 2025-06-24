"""Transparent overlay that draws the dashboard grid."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget


class GridOverlay(QWidget):
    """Overlay widget drawing grid cells with rounded corners."""

    def __init__(self, cell_size: int, rows: int, cols: int, parent=None) -> None:
        super().__init__(parent)
        self.cell_size = cell_size
        self.rows = rows
        self.cols = cols
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.hide()

    def paintEvent(self, event):  # noqa: D401 - simple painting
        """Paint the grid."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color = QColor(0, 0, 0, 40)
        painter.setPen(color)
        for row in range(self.rows):
            for col in range(self.cols):
                x = col * self.cell_size
                y = row * self.cell_size
                rect = (x, y, self.cell_size, self.cell_size)
                painter.drawRoundedRect(*rect, 6, 6)
        painter.end()
        super().paintEvent(event)

