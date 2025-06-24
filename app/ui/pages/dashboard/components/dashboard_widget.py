"""Base class for dashboard widgets."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from .widget_size import WidgetSize


@dataclass
class WidgetConfig:
    widget_type: str
    row: int
    col: int
    size: WidgetSize


class DashboardWidget(QFrame):
    """A simple placeholder widget that knows its grid placement."""

    def __init__(self, config: WidgetConfig, parent=None) -> None:
        super().__init__(parent)
        self.config = config
        self.setObjectName("DashboardWidget")
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("background-color: #DDD; border-radius: 8px;")

        label = QLabel(config.widget_type)
        label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(label)

