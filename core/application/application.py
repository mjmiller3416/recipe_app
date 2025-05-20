"""core/application/application.py

Main application window with a custom title bar, sidebar, header, and dynamic stacked content.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
                               QMainWindow, QStackedWidget, QVBoxLayout,
                               QWidget)

from core.controllers.animation_controller import AnimationManager
from core.controllers.theme_controller import ThemeController
from core.helpers import DebugLogger
from services.planner_service import PlannerService
from services.shopping_service import ShoppingService
from ui.animations import SidebarAnimator
from ui.components.inputs.search_widget import SearchWidget
from ui.components.title_bar import TitleBar
from ui.tools.layout_debugger import LayoutDebugger
from views.add_recipes import AddRecipes
from views.dashboard import Dashboard
from views.meal_planner import MealPlanner
from views.shopping_list import ShoppingList
from views.view_recipes import ViewRecipes

from .sidebar_widget import SidebarWidget


# ── Class Definition ────────────────────────────────────────────────────────────
class Application(QMainWindow):
    """
    Main application window with a custom title bar, sidebar, header, and dynamic stacked content.
    Applies custom styling and manages navigation.
    """
    def __init__(self):
        super().__init__()
        # ── Initialize Controller ──
        self.theme_controller = ThemeController()
        self.theme_controller.apply_full_theme()
        
        # ── Window Setup ──
        self.setObjectName("Application")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(1280, 720) # Set minimum size for the window
        self.sidebar_is_expanded = True

        # ── Outter Wrapper ──
        self.wrapper = QFrame()
        self.wrapper.setObjectName("ApplicationWrapper")
        self.setCentralWidget(self.wrapper)

        # ── Layouts ──
        self.outer_layout = QVBoxLayout(self.wrapper)
        self.outer_layout.setContentsMargins(0, 0, 0, 0)
        self.outer_layout.setSpacing(0)

        # ── Create Title Bar ──
        self.title_bar = TitleBar(self)
        self.outer_layout.addWidget(self.title_bar)

        # ── Main Layout ──
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.outer_layout.addLayout(self.main_layout)

        # ── Instantiate Sidebar ──
        self.sidebar = SidebarWidget()
        self.main_layout.addWidget(self.sidebar)

        # ── Connect Signals ──
        self.title_bar.sidebar_toggled.connect(self.toggle_sidebar)
        self.title_bar.close_clicked.connect(self.handle_close)
        self.title_bar.minimize_clicked.connect(self.showMinimized)
        self.title_bar.maximize_clicked.connect(self.toggle_maximize_restore)
        self.sidebar.close_app.connect(self.handle_close)

        # ── Main Content Container ──
        self.content_wrapper = QVBoxLayout()
        self.content_wrapper.setContentsMargins(0, 0, 0, 0)
        self.content_wrapper.setSpacing(0)
        self.main_layout.addLayout(self.content_wrapper)

        # ── Header ──
        self.header = QWidget()
        self.header.setObjectName("header")
        self.header_layout = QHBoxLayout(self.header)
        self.header_layout.setContentsMargins(20, 12, 20, 12)
        self.header_layout.setSpacing(20)

        # ── Welcome Message Group ──
        self.greeting_container = QWidget(self.header) # create a container for the greeting labels
        self.greeting_container.setObjectName("greeting_container")

        greeting_layout = QVBoxLayout(self.greeting_container) 
        greeting_layout.setContentsMargins(0, 0, 0, 0)
        greeting_layout.setSpacing(0)

        self.lbl_greeting = QLabel("Welcome Back,", self.greeting_container) 
        self.lbl_greeting.setObjectName("lbl_greeting")

        self.lbl_username = QLabel("MARYANN", self.greeting_container) 
        self.lbl_username.setObjectName("lbl_username")

        greeting_layout.addWidget(self.lbl_greeting) # add to the layout
        greeting_layout.addWidget(self.lbl_username)

        self.header_layout.addWidget(self.greeting_container) # add to the header layout

        # Instantiate Search Widget
        self.search_widget = SearchWidget()
        self.search_widget.setMaximumHeight(36)
        self.search_widget.setFixedWidth(300)
        self.header_layout.addWidget(self.search_widget, alignment=Qt.AlignRight)

        self.content_wrapper.addWidget(self.header)

        # ── Stacked Pages ──
        self.sw_pages = QStackedWidget()
        self.content_wrapper.addWidget(self.sw_pages)

        self.page_instances = self.build_pages() # build page instances

        for name, page in self.page_instances.items():
            self.sw_pages.addWidget(page)

        self.connect_navigation()
        self.switch_page("dashboard")

        #self.overlay = LayoutDebugger(self.wrapper)

    def build_pages(self):
        """Instantiate and return all page instances for the stacked widget."""
        return {
            "dashboard": Dashboard(),
            "meal_planner": MealPlanner(),
            "view_recipes": ViewRecipes(),
            "shopping_list": ShoppingList(),
            "add_recipe": AddRecipes(),
        }

    def connect_navigation(self):
        """Connect sidebar navigation buttons to stacked widget."""
        button_map = {
            "btn_dashboard": "dashboard",
            "btn_meal_planner": "meal_planner",
            "btn_view_recipes": "view_recipes",
            "btn_shopping_list": "shopping_list",
            "btn_add_recipes": "add_recipe",
        }

        for btn_name, page_name in button_map.items():
            button = self.sidebar.buttons.get(btn_name)
            if button:
                button.clicked.connect(lambda _, p=page_name: self.switch_page(p))

    def switch_page(self, page_name):
        """
        Switch stacked widget to the given page.

        Args:
            page_name (str): The name of the page to switch to.
        """
        DebugLogger.log("Switching to page: {page_name}", "info")

        # ── Check if Page Exists ──
        if page_name in self.page_instances:
            next_widget = self.page_instances[page_name]
            current_widget = self.sw_pages.currentWidget()

            if isinstance(current_widget, MealPlanner):
                current_widget.save_meal_plan()

            # ── Set Button States ──
            for btn_name, page_key in {
                "btn_dashboard": "dashboard",
                "btn_meal_planner": "meal_planner",
                "btn_view_recipes": "view_recipes",
                "btn_shopping_list": "shopping_list",
                "btn_add_recipes": "add_recipe",
            }.items():
                button = self.sidebar.buttons.get(btn_name)
                if button:
                    button.setChecked(page_key == page_name)

            # ── Animate Transisitions ──
            next_widget = self.page_instances[page_name]
            current_widget = self.sw_pages.currentWidget()

            # ── Refresh ShoppingList ──
            if page_name == "shopping_list":

                if isinstance(next_widget, ShoppingList):
                    meal_ids = PlannerService.load_saved_meal_ids()  # Get current active meals
                    recipe_ids = ShoppingService.get_recipe_ids_from_meals(meal_ids)
                    next_widget.load_shopping_list(recipe_ids)
        
            if current_widget != next_widget:
                AnimationManager.transition_stack(current_widget, next_widget, self.sw_pages)

    def toggle_maximize_restore(self):
        if self.isMaximized():
            self.showNormal()
            self.title_bar.update_maximize_icon(False)
        else:
            self.showMaximized()
            self.title_bar.update_maximize_icon(True)

    def toggle_sidebar(self):
        """ Toggle the sidebar's expanded/collapsed state with animation."""
        collapsed_width = 0
        expanded_width = 215

        start_width = self.sidebar.width()
        end_width = collapsed_width if self.sidebar_is_expanded else expanded_width

        self.sidebar_animator = SidebarAnimator(self.sidebar)

        self.sidebar_animation = QPropertyAnimation(self.sidebar_animator, b"value")
        self.sidebar_animation.setDuration(500)
        self.sidebar_animation.setStartValue(start_width)
        self.sidebar_animation.setEndValue(end_width)
        self.sidebar_animation.setEasingCurve(QEasingCurve.OutExpo)

        self.sidebar_animation.start()
        self.sidebar_is_expanded = not self.sidebar_is_expanded

    def handle_close(self):
        """Custom logic before application closes."""
        MealPlanner.save_meal_plan(self.page_instances["meal_planner"])
        QApplication.quit()


