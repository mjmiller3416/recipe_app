"""Container widget that positions dashboard widgets on a fixed grid."""

from __future__ import annotations

from typing import List

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget

from .dashboard_widget import DashboardWidget, WidgetConfig
from .grid_overlay import GridOverlay


class DashboardGrid(QWidget):
    """Holds DashboardWidget instances arranged on a static grid."""

    GRID_ROWS = 6
    GRID_COLS = 9
    CELL_SIZE = 100

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.widgets: List[DashboardWidget] = []
        self.overlay = GridOverlay(self.CELL_SIZE, self.GRID_ROWS, self.GRID_COLS, self)
        self.overlay.resize(self.size())

    def add_dashboard_widget(self, widget: DashboardWidget) -> None:
        """Add a widget to the grid and position it."""
        self.widgets.append(widget)
        widget.setParent(self)
        widget.raise_()
        self._position_widget(widget)

    # ── Internal Helpers ───────────────────────────────────────────────────────
    def _position_widget(self, widget: DashboardWidget) -> None:
        cfg = widget.config
        width = cfg.size.cols * self.CELL_SIZE
        height = cfg.size.rows * self.CELL_SIZE
        x = cfg.col * self.CELL_SIZE
        y = cfg.row * self.CELL_SIZE
        widget.setGeometry(x, y, width, height)

    def resizeEvent(self, event):  # noqa: D401 - Qt override
        """Resize overlay along with the grid."""
        self.overlay.resize(self.size())
        for widget in self.widgets:
            self._position_widget(widget)
        super().resizeEvent(event)

