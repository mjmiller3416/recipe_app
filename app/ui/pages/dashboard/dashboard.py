"""Dashboard page with simple grid layout."""

from __future__ import annotations

# ── Imports ────────────────────────────────────────────────────────────────────
from PySide6.QtWidgets import QVBoxLayout, QWidget

from .components.dashboard_grid import DashboardGrid
from .components.dashboard_widget import DashboardWidget, WidgetConfig
from .components.widget_size import WidgetSize


# ── Class Definition ───────────────────────────────────────────────────────────
class Dashboard(QWidget):
    """Dashboard screen composed of a grid of widgets."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setObjectName("Dashboard")
        self.setMinimumSize(984, 818)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.grid = DashboardGrid(self)
        self.layout.addWidget(self.grid)

        # ── Dummy Widgets for Initial Phase ──
        w1 = DashboardWidget(WidgetConfig("Widget A", 0, 0, WidgetSize.SIZE_2x2))
        w2 = DashboardWidget(WidgetConfig("Widget B", 0, 2, WidgetSize.SIZE_1x2))
        w3 = DashboardWidget(WidgetConfig("Widget C", 2, 0, WidgetSize.SIZE_3x1))

        for widget in (w1, w2, w3):
            self.grid.add_dashboard_widget(widget)

