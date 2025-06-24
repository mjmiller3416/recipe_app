"""app/ui/pages/dashboard/dashboard_widget.py

Base class for widgets placed on the dashboard grid.
"""

# ── Imports ────────────────────────────────────────────
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QFrame

from .widget_sizes import WidgetSize


class DashboardWidget(QFrame):
    """Simple placeholder widget displayed on the dashboard."""

    def __init__(self, widget_id: str, title: str, size: WidgetSize, parent=None):
        super().__init__(parent)
        self.widget_id = widget_id
        self.title = title
        self.size = size

        self.setObjectName("DashboardWidget")
        self._build_ui()

    # ── Internal Methods ──────────────────────────────────────
    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel(self.title)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
