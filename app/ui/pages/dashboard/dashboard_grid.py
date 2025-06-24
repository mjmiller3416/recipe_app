"""app/ui/pages/dashboard/dashboard_grid.py

Widget responsible for manual placement of dashboard widgets using a fixed grid.
"""

# ── Imports ────────────────────────────────────────────
from PySide6.QtCore import QRect
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from .dashboard_widget import DashboardWidget
from .widget_sizes import WidgetSize


class DashboardGrid(QWidget):
    """A simple 9x6 grid layout for displaying DashboardWidgets."""

    ROWS = 6
    COLS = 9
    CELL_SIZE = 100
    SPACING = 10
    GRID_RADIUS = 8

    def __init__(self, parent=None, dev_mode: bool = False) -> None:
        super().__init__(parent)
        self.setObjectName("DashboardGrid")
        self.dev_mode = dev_mode

        self.setFixedSize(self.grid_width(), self.grid_height())
        self._place_dummy_widgets()

    # ── Public API ──────────────────────────────────
    def grid_width(self) -> int:
        """Return the total width of the grid in pixels."""
        return self.COLS * self.CELL_SIZE + (self.COLS - 1) * self.SPACING

    def grid_height(self) -> int:
        """Return the total height of the grid in pixels."""
        return self.ROWS * self.CELL_SIZE + (self.ROWS - 1) * self.SPACING

    def paintEvent(self, event) -> None:  # type: ignore[override]
        super().paintEvent(event)
        if not self.dev_mode:
            return

        painter = QPainter(self)
        pen = QPen(QColor(0, 0, 0, 40))
        painter.setPen(pen)
        for row in range(self.ROWS):
            for col in range(self.COLS):
                x = col * (self.CELL_SIZE + self.SPACING)
                y = row * (self.CELL_SIZE + self.SPACING)
                rect = QRect(x, y, self.CELL_SIZE, self.CELL_SIZE)
                painter.drawRoundedRect(rect, self.GRID_RADIUS, self.GRID_RADIUS)

    # ── Internal Methods ──────────────────────────────────────
    def _place_widget(self, widget: DashboardWidget, row: int, col: int) -> None:
        width = widget.size.cols() * self.CELL_SIZE + (widget.size.cols() - 1) * self.SPACING
        height = widget.size.rows() * self.CELL_SIZE + (widget.size.rows() - 1) * self.SPACING
        x = col * (self.CELL_SIZE + self.SPACING)
        y = row * (self.CELL_SIZE + self.SPACING)
        widget.setParent(self)
        widget.setGeometry(x, y, width, height)
        widget.show()

    def _place_dummy_widgets(self) -> None:
        self._place_widget(
            DashboardWidget("w1", "Recipe Card", WidgetSize.ONE_BY_TWO), 1, 1
        )
        self._place_widget(
            DashboardWidget("w2", "Header Banner", WidgetSize.THREE_BY_ONE), 0, 3
        )
        self._place_widget(
            DashboardWidget("w3", "Carousel", WidgetSize.FOUR_BY_THREE), 2, 4
        )
