"""app/ui/test_main_window_close.py

Test the MainWindow close event to ensure it saves the meal plan state.
This file contains a test for the MainWindow class, specifically checking that
the meal planner's state is saved when the window is closed.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QWidget
from pytestqt.qtbot import QtBot

from app.style import ThemeController
from app.ui.main_window import MainWindow
from app.ui.services.navigation_service import NavigationService
from app.ui.views.dashboard import Dashboard
from app.ui.views.meal_planner import MealPlanner


@pytest.fixture
def main_window(qtbot: QtBot):
    theme_controller = ThemeController()
    theme_controller.apply_full_theme = lambda: None

    # Create MainWindow with new NavigationService (no factory needed)
    window = MainWindow()
    
    # Manually add test widgets to simulate the old behavior for testing
    mp = MealPlanner()
    db = Dashboard()
    window.sw_pages.addWidget(db)
    window.sw_pages.addWidget(mp)
    
    qtbot.addWidget(window)
    window.show()
    return window


def test_close_saves_meal_plan(main_window: MainWindow, qtbot: QtBot):
    # Find meal planner widget from stacked widget (similar to updated closeEvent logic)
    planner = None
    for i in range(main_window.sw_pages.count()):
        widget = main_window.sw_pages.widget(i)
        if widget and (widget.__class__.__name__ == 'MealPlanner' or 
                      widget.objectName().lower() == 'mealplanner'):
            planner = widget
            break
    
    assert planner is not None, "MealPlanner widget not found"
    planner.saveMealPlan = MagicMock()
    main_window.close()
    planner.saveMealPlan.assert_called_once()
