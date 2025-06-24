import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

from app.ui.pages.dashboard import DashboardGrid, DashboardWidget, WidgetSize


def test_widget_size_helpers():
    assert WidgetSize.ONE_BY_TWO.cols() == 1
    assert WidgetSize.ONE_BY_TWO.rows() == 2


def test_place_widget_geometry(qtbot: QtBot):
    grid = DashboardGrid(dev_mode=False)
    qtbot.addWidget(grid)
    widget = DashboardWidget("id", "Test", WidgetSize.ONE_BY_TWO)
    grid._place_widget(widget, 1, 1)
    expected_x = 1 * (DashboardGrid.CELL_SIZE + DashboardGrid.SPACING)
    expected_y = 1 * (DashboardGrid.CELL_SIZE + DashboardGrid.SPACING)
    expected_w = WidgetSize.ONE_BY_TWO.cols() * DashboardGrid.CELL_SIZE + (WidgetSize.ONE_BY_TWO.cols() - 1) * DashboardGrid.SPACING
    expected_h = WidgetSize.ONE_BY_TWO.rows() * DashboardGrid.CELL_SIZE + (WidgetSize.ONE_BY_TWO.rows() - 1) * DashboardGrid.SPACING
    assert widget.geometry().x() == expected_x
    assert widget.geometry().y() == expected_y
    assert widget.geometry().width() == expected_w
    assert widget.geometry().height() == expected_h


def test_dummy_widget_count(qtbot: QtBot):
    grid = DashboardGrid(dev_mode=False)
    qtbot.addWidget(grid)
    widgets = grid.findChildren(DashboardWidget)
    assert len(widgets) == 3
