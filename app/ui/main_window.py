"""app/ui/main_window.py

Defines the main application window, including the custom title bar and sidebar.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from typing import TYPE_CHECKING, Callable

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QStackedWidget,
                               QVBoxLayout, QWidget)
# --- Import the frameless window class ---
from qframelesswindow import FramelessWindow

from app.config import APPLICATION_WINDOW
from app.style_manager.theme_controller import ThemeController
from app.ui.animations import WindowAnimator
from app.ui.components import SearchBar
from app.ui.components.navigation.sidebar import Sidebar
from app.ui.components.navigation.titlebar import TitleBar
from app.style_manager.icons.icon_loader import IconLoader
from app.ui.helpers.ui_helpers import center_on_screen

if TYPE_CHECKING:
    from app.ui.services.navigation_service import NavigationService

# ── Constants ───────────────────────────────────────────────────────────────────────────
SETTINGS = APPLICATION_WINDOW["SETTINGS"]


# ── Application Window ──────────────────────────────────────────────────────────────────
class MainWindow(FramelessWindow):
    """The main application window, orchestrating title bar, sidebar, and content pages.

    This class serves as the central hub of the user interface, using qframelesswindow
    to provide a native look and feel for the window border and title bar.
    It incorporates a custom `TitleBar`, a collapsible `Sidebar`, and a `QStackedWidget`
    to display different application views (pages).

    Attributes:
        animator (WindowAnimator): Handles window animations like minimize/maximize.
        title_bar (TitleBar): The custom title bar widget.
        sidebar (Sidebar): The navigation sidebar widget.
        sw_pages (QStackedWidget): Widget that holds and switches between different pages.
        navigation (NavigationService): Service responsible for page management and nav.
    """
    # ── Signals ─────────────────────────────────────────────────────────────────────────
    sidebar_toggle_requested = Signal()

    def __init__(
            self,
            theme_controller: 'ThemeController',
            navigation_service_factory: Callable[[QStackedWidget], 'NavigationService']
    ):
        """Initializes the MainWindow.

        Args:
            theme_controller (ThemeController): The controller for managing app themes.
            navigation_service_factory (callable): A factory function that creates an
            instance of NavigationService.
        """
        super().__init__()

        # ── Window Properties ──
        self.setObjectName("App")
        self.setMinimumSize(800, 360)

        # ── Theme & Services ──
        self.theme_controller = theme_controller
        IconLoader().connect_theme_controller(self.theme_controller)
        self.theme_controller.apply_full_theme()

        # ── Title Bar & Main Layout ──
        self.title_bar = TitleBar(self)
        self.setTitleBar(self.title_bar)
        self._isResizeEnabled = True

        # ── Main Layout ──
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, self.title_bar.height(), 0, 0)
        self.main_layout.setSpacing(0)

        # ── Body Layout ──
        self.window_body = QWidget(self)
        self.window_body.setObjectName("ApplicationWindow")
        self.body_layout = QHBoxLayout(self.window_body)
        self.body_layout.setContentsMargins(1, 0, 1, 1)
        self.body_layout.setSpacing(0)

        self.main_layout.addWidget(self.window_body) # add body widget to the main layout

        # ── Sidebar and Content Area ──
        self.sidebar = Sidebar()
        self.body_layout.addWidget(self.sidebar)

        self.content_area = QWidget()
        self.content_area.setObjectName("ContentArea")
        self.body_layout.addWidget(self.content_area)

        self.content_outer_layout = QVBoxLayout(self.content_area)
        self.content_outer_layout.setContentsMargins(0, 0, 0, 0)
        self.content_outer_layout.setSpacing(0)

        # Header Layout
        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(20, 20, 20, 20)
        self.content_outer_layout.addLayout(self.header_layout)

        # Header Widgets
        self.lbl_header = QLabel()
        self.lbl_header.setProperty("tag", "Header")
        self.lbl_header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.header_layout.addWidget(self.lbl_header, alignment=Qt.AlignLeft)

        self.search_bar = SearchBar()
        self.header_layout.addWidget(self.search_bar, alignment=Qt.AlignRight)

        # Stacked Pages
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(8)
        self.content_outer_layout.addLayout(self.content_layout)
        self.sw_pages = QStackedWidget()
        self.content_layout.addWidget(self.sw_pages)

        # ── Initialize Services & Connect Signals ──
        self.animator = WindowAnimator(self)
        self.navigation: 'NavigationService' = navigation_service_factory(self.sw_pages)
        self.navigation.build_and_register_pages()

        self._connect_signals()
        self.sw_pages.currentChanged.connect(self._on_page_changed)

        # Set initial page
        self.navigation.switch_to("dashboard")
        self.sidebar.buttons["btn_dashboard"].setChecked(True)

        # Resize and center the window at the end
        self.resize(int(SETTINGS["WINDOW_WIDTH"]), int(SETTINGS["WINDOW_HEIGHT"]))
        center_on_screen(self)

    @property
    def _is_maximized(self) -> bool:
        return self.isMaximized()

    def _connect_signals(self):
        """Connect all UI signals to their respective slots."""
        # Title Bar
        self.title_bar.close_clicked.connect(self.close)
        self.title_bar.minimize_clicked.connect(self.animator.animate_minimize)
        self.title_bar.maximize_clicked.connect(self.animator.animate_toggle_maximize)
        self.title_bar.sidebar_toggled.connect(self.sidebar_toggle_requested.emit)

        # Sidebar
        self.sidebar_toggle_requested.connect(self.sidebar.toggle)

        # Navigation
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
                button.clicked.connect(lambda _, p=page_name: self._switch_page(p))

    def _switch_page(self, page_name: str):
        """Helper to switch pages and update the header text."""
        self.navigation.switch_to(page_name)

    def _update_header(self, page_name: str):
        """Update header label text based on page name."""
        mapping = {
            "dashboard": "Dashboard",
            "meal_planner": "Meal Planner",
            "view_recipes": "View Recipes",
            "shopping_list": "Shopping List",
            "add_recipe": "Add Recipe",
        }
        self.lbl_header.setText(mapping.get(page_name, page_name.replace("_", " ").title()))

    def _on_page_changed(self, index: int):
        """Update header when stacked widget page changes."""
        widget = self.sw_pages.widget(index)
        if not widget:
            return

        for name, w_instance in self.navigation.page_instances.items():
            if w_instance is widget:
                self._update_header(name)
                # auto-focus the recipe name field when AddRecipes page is shown
                if name == "add_recipe" and hasattr(w_instance, 'le_recipe_name'):
                    from PySide6.QtCore import QTimer
                    QTimer.singleShot(0, w_instance.le_recipe_name.setFocus)
                break

    def keyPressEvent(self, event):
        """Ignore the Escape key to prevent accidental app closure."""
        if event.key() == Qt.Key_Escape:
            event.ignore()
            return
        super().keyPressEvent(event)

    def closeEvent(self, event):
        """Persist planner state before closing the application."""
        meal_planner = self.navigation.page_instances.get("meal_planner")
        if meal_planner and hasattr(meal_planner, 'save_meal_plan'):
            meal_planner.save_meal_plan()
        super().closeEvent(event)
