"""core/application/application.py

Main application window with a custom title bar, sidebar, header, and dynamic stacked content.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QMainWindow,
                               QStackedWidget, QVBoxLayout, QWidget)

from services.planner_service import PlannerService
from services.shopping_service import ShoppingService
from style_manager.theme_controller import ThemeController
from ui.animations import SidebarAnimator
from ui.components.inputs.search_bar import SearchBar

from views.add_recipes import AddRecipes
from views.dashboard import Dashboard
from views.meal_planner import MealPlanner
from views.shopping_list import ShoppingList
from views.view_recipes import ViewRecipes

from ..controllers import AnimationManager
from ..helpers import DebugLogger
from .app_window import ApplicationWindow
from .sidebar import Sidebar

# ── Constants ───────────────────────────────────────────────────────────────────
COLLAPSED_SIDEBAR_WIDTH = 0
EXPANDED_SIDEBAR_WIDTH = 400

# ── Class Definition ────────────────────────────────────────────────────────────
class Application(ApplicationWindow):
    """
    Main application window with a custom title bar, sidebar, header, and dynamic stacked content.
    Applies custom styling and manages navigation.
    """
    def __init__(self):
        super().__init__(width = 1720, height=1080)

         # ── Initialize ThemeController ──
        self.theme_controller = ThemeController()
        self.theme_controller.apply_full_theme()

        # ── Instantiate Sidebar ──
        self.sidebar = Sidebar()
        self.body_layout.insertWidget(0, self.sidebar)
        self.sidebar_is_expanded = True

        # ── Connect Signals ──
        self.sidebar_toggle_requested.connect(self._toggle_sidebar)
        self.sidebar.btn_exit.clicked.connect(self._handle_close)

        # ── Stacked Pages ──
        self.sw_pages = QStackedWidget()
        self.content_layout.addWidget(self.sw_pages)

    def _toggle_sidebar(self):
        """ Toggle the sidebar's expanded/collapsed state with animation."""

        start_width = self.sidebar.width()
        end_width = COLLAPSED_SIDEBAR_WIDTH if self.sidebar_is_expanded else EXPANDED_SIDEBAR_WIDTH

        self.sidebar_animator = SidebarAnimator(self.sidebar)

        self.sidebar_animation = QPropertyAnimation(self.sidebar_animator, b"value")
        self.sidebar_animation.setDuration(500)
        self.sidebar_animation.setStartValue(start_width)
        self.sidebar_animation.setEndValue(end_width)
        self.sidebar_animation.setEasingCurve(QEasingCurve.OutExpo)

        self.sidebar_animation.start()
        self.sidebar_is_expanded = not self.sidebar_is_expanded

    def _handle_close(self):
        """Custom logic before application closes."""
        # MealPlanner.save_meal_plan(self.page_instances["meal_planner"])
        QApplication.quit()


