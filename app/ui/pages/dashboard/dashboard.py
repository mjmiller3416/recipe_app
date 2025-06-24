"""app/ui/pages/dashboard/dashboard.py

Placeholder class for the Dashboard screen.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from app.config import DEBUG_LAYOUT_BORDERS
from .dashboard_grid import DashboardGrid


# ── Class Definition ────────────────────────────────────────────────────────────
class Dashboard(QWidget):
    """Placeholder class for the Dashboard screen."""

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # ── Setup ──
        self.setObjectName("Dashboard")
        self.setMinimumSize(984, 818)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignCenter)

        # add the dashboard grid
        self.grid = DashboardGrid(dev_mode=DEBUG_LAYOUT_BORDERS)
        self.layout.addWidget(self.grid)
