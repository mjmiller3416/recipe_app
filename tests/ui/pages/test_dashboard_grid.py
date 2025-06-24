import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QFrame
from pytestqt.qtbot import QtBot

from app.ui.pages.dashboard import DashboardGrid, DashboardWidget, WidgetSize


def test_widget_size_helpers():
    assert WidgetSize.ONE_BY_TWO.cols() == 1
    assert WidgetSize.ONE_BY_TWO.rows() == 2


def test_place_widget_geometry(qtbot: QtBot):
    grid = DashboardGrid(dev_mode=False)
    qtbot.addWidget(grid)
    builder = DashboardWidget("id", "Test", WidgetSize.ONE_BY_TWO)
    frame = grid._place_widget(builder, 1, 1)
    expected_x = 1 * (DashboardGrid.CELL_SIZE + DashboardGrid.SPACING)
    expected_y = 1 * (DashboardGrid.CELL_SIZE + DashboardGrid.SPACING)
    expected_w = WidgetSize.ONE_BY_TWO.cols() * DashboardGrid.CELL_SIZE + (WidgetSize.ONE_BY_TWO.cols() - 1) * DashboardGrid.SPACING
    expected_h = WidgetSize.ONE_BY_TWO.rows() * DashboardGrid.CELL_SIZE + (WidgetSize.ONE_BY_TWO.rows() - 1) * DashboardGrid.SPACING
    assert frame.geometry().x() == expected_x
    assert frame.geometry().y() == expected_y
    assert frame.geometry().width() == expected_w
    assert frame.geometry().height() == expected_h


def test_dummy_widget_count(qtbot: QtBot):
    grid = DashboardGrid(dev_mode=False)
    qtbot.addWidget(grid)
    widgets = grid.findChildren(QFrame, "DashboardWidget")
    assert len(widgets) == 3
