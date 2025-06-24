import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pytestqt.qtbot import QtBot

from app.ui.pages.dashboard import Dashboard, DashboardGrid


def test_dashboard_contains_grid(qtbot: QtBot):
    dashboard = Dashboard()
    qtbot.addWidget(dashboard)
    grid = dashboard.findChild(DashboardGrid)
    assert grid is not None
