import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QWidget
from pytestqt.qtbot import QtBot

from app.ui.main_window import MainWindow
from app.style_manager import ThemeController
from app.core.services import NavigationService
from app.ui.pages.meal_planner import MealPlanner
from app.ui.pages.dashboard import Dashboard


@pytest.fixture
def main_window(qtbot: QtBot):
    theme_controller = ThemeController()
    theme_controller.apply_full_theme = lambda: None

    def factory(sw):
        nav = NavigationService.create(sw)
        mp = MealPlanner()
        db = Dashboard()
        nav.page_instances = {"dashboard": db, "meal_planner": mp}
        sw.addWidget(db)
        sw.addWidget(mp)
        nav.build_and_register_pages = lambda: None
        return nav

    window = MainWindow(theme_controller=theme_controller, navigation_service_factory=factory)
    qtbot.addWidget(window)
    window.show()
    return window


def test_close_saves_meal_plan(main_window: MainWindow, qtbot: QtBot):
    planner = main_window.navigation.page_instances["meal_planner"]
    planner.save_meal_plan = MagicMock()
    main_window.close()
    planner.save_meal_plan.assert_called_once()
