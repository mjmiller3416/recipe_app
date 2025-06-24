"""Initialization for dashboard components."""

from .dashboard import Dashboard
from .components.dashboard_grid import DashboardGrid
from .components.dashboard_widget import DashboardWidget, WidgetConfig
from .components.widget_size import WidgetSize

__all__ = [
    "Dashboard",
    "DashboardGrid",
    "DashboardWidget",
    "WidgetConfig",
    "WidgetSize",
]

