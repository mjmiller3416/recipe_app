"""app/ui/pages/dashboard/dashboard_widget.py

Dashboard widget builder used to construct placeholder frames.
"""

# ── Imports ────────────────────────────────────────────
from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QFrame

from .widget_sizes import WidgetSize


@dataclass(frozen=True, slots=True)
class DashboardWidget:
    """Simple placeholder widget displayed on the dashboard."""

    widget_id: str
    title: str
    size: WidgetSize

    def build(self) -> QFrame:
        """Construct and return a styled QFrame for the widget."""
        frame = QFrame()
        frame.setObjectName("DashboardWidget")
        frame.setProperty("widget_size", f"{self.size.cols()}x{self.size.rows()}")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel(self.title)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        return frame
