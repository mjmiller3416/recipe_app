"""app/ui/main_window.py

Defines the main application window, including the custom title bar and sidebar.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from typing import TYPE_CHECKING, Callable

from PySide6.QtCore import QPoint, QPropertyAnimation, QRect, Qt, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.config import APPLICATION_WINDOW
from app.core.utils import StartupTimer
from app.style_manager import ThemeController
from app.ui.animations import WindowAnimator
from app.ui.components import CustomGrip
from app.ui.components.navigation.sidebar import Sidebar
from app.ui.components.navigation.titlebar import TitleBar
from app.ui.components import SearchBar
from app.ui.helpers.ui_helpers import center_on_screen

if TYPE_CHECKING:
    from app.core.services import NavigationService
    from app.style_manager import ThemeController

# ── Constants ───────────────────────────────────────────────────────────────────────────
SETTINGS = APPLICATION_WINDOW["SETTINGS"]

# ── Application Window ──────────────────────────────────────────────────────────────────
class MainWindow(QDialog):
    """The main application window, orchestrating title bar, sidebar, and content pages.

    This class serves as the central hub of the user interface. It's a frameless QDialog
    that incorporates a custom `TitleBar` for window controls, a collapsible `Sidebar` for
    navigation, and a `QStackedWidget` to display different application views (pages).
    It handles window resizing, positioning, and connects user actions from the UI
    (like button clicks in the sidebar) to the `NavigationService`.

    Attributes:
        start_geometry (QRect): The window's geometry at the start of a resize operation.
        animator (WindowAnimator): Handles window animations like minimize/maximize.
        title_bar (TitleBar): The custom title bar widget.
        sidebar (Sidebar): The navigation sidebar widget.
        sw_pages (QStackedWidget): Widget that holds and switches between different pages.
        navigation (NavigationService): Service responsible for page management and nav.
        _is_maximized (bool): Tracks if the window is currently maximized.
        grips (dict[str, CustomGrip]): A dictionary of CustomGrip widgets for resizing.
    
    Signals:
        sidebar_toggle_requested: Emit when sidebar toggle button is clicked in title bar.
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
            navigation_service_factory (callable): A factory function creates an instance
            of NavigationService, pre-configured with the page container (QStackedWidget).
        """
        super().__init__()
        # ── Window Properties ──
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(800, 360)
        self.setObjectName("App")
        self.start_geometry = self.geometry()
        self.central_layout = QVBoxLayout(self)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setSpacing(0)
        self.resize(int(SETTINGS["WINDOW_WIDTH"]), int(SETTINGS["WINDOW_HEIGHT"]))
        center_on_screen(self)

        # ── Theme & Services ──
        self.theme_controller = theme_controller
        self.theme_controller.apply_full_theme()

        # ── Title Bar ──
        self.animator = WindowAnimator(self)
        self.title_bar = TitleBar(self)
        self._is_maximized = False
        self.central_layout.addWidget(self.title_bar)
        self.title_bar.close_clicked.connect(self.close)
        self.title_bar.minimize_clicked.connect(self.animator.animate_minimize)
        self.title_bar.maximize_clicked.connect(self.animator.animate_toggle_maximize)
        self.title_bar.sidebar_toggled.connect(self.sidebar_toggle_requested.emit)

        # ── Body Layout ──
        self.window_body = QWidget(self) 
        self.window_body.setObjectName("ApplicationWindow")
        self.body_layout = QHBoxLayout(self.window_body)
        self.body_layout.setContentsMargins(1, 0, 1, 1)
        self.body_layout.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar_toggle_requested.connect(self.sidebar.toggle)
        self.body_layout.addWidget(self.sidebar) # add sidebar to body layout

        self.content_area = QWidget()
        self.content_area.setObjectName("ContentArea")
        # layout containing header and page content
        self.content_outer_layout = QVBoxLayout(self.content_area)
        self.content_outer_layout.setContentsMargins(0, 0, 0, 0)
        self.content_outer_layout.setSpacing(0)

        # header layout
        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(20, 20, 20, 20)
        self.header_layout.setSpacing(0)
        self.content_outer_layout.addLayout(self.header_layout)

        # ── Header Widgets ──
        self.lbl_header = QLabel()
        self.lbl_header.setProperty("tag", "Header")
        self.lbl_header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.header_layout.addWidget(self.lbl_header, alignment=Qt.AlignLeft)

        self.search_bar = SearchBar()
        self.header_layout.addWidget(self.search_bar, alignment=Qt.AlignRight)

        # layout for stacked pages
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(8)
        self.content_outer_layout.addLayout(self.content_layout)

        self.body_layout.addWidget(self.content_area)
        self.central_layout.addWidget(self.window_body)

        # ── Stacked Pages ──
        self.sw_pages = QStackedWidget()
        self.content_layout.addWidget(self.sw_pages)

        # ── Initialize & Connect Navigation Service ──
        self.navigation: 'NavigationService' = navigation_service_factory(self.sw_pages)
        self.navigation.build_and_register_pages()
        self._connect_navigation_signals()
        self.sw_pages.currentChanged.connect(self._on_page_changed)

        # ── Create Grips ──
        self.grips = {}        
        grip_positions = [
            "top", "bottom", "left", "right",
            "top_left", "top_right", "bottom_left", "bottom_right"
        ]
        for pos in grip_positions:
            self.grips[pos] = CustomGrip(self, pos)
            self.grips[pos].raise_()
        
        self.navigation.switch_to("dashboard") # set initial page
        self.sidebar.buttons["btn_dashboard"].setChecked(True)
        self._update_header("dashboard")
        
    def _connect_navigation_signals(self):
        """Connects the navigation buttons in the sidebar to the NavigationService's switch_to method."""
        # This logic is simplified from app.py
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
        self._update_header(page_name)

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
        for name, w in self.navigation.page_instances.items():
            if w is widget:
                self._update_header(name)
                break

    def resizeEvent(self, event):
        """Handles window resize events.

        Repositions all custom size grips when the window is resized.

        Args:
            event (QResizeEvent): The resize event.
        """
        super().resizeEvent(event)
        grip_size = self.grips["top"].grip_size
        w, h = self.width(), self.height()

        if self.animator.animation_group and self.animator.animation_group.state() == QPropertyAnimation.Running:
            return

        self.grips["top"].setGeometry(grip_size, 0, w - 2 * grip_size, grip_size)
        self.grips["bottom"].setGeometry(grip_size, h - grip_size, w - 2 * grip_size, grip_size)
        self.grips["left"].setGeometry(0, grip_size, grip_size, h - 2 * grip_size)
        self.grips["right"].setGeometry(w - grip_size, grip_size, grip_size, h - 2 * grip_size)
        self.grips["top_left"].setGeometry(0, 0, grip_size, grip_size)
        self.grips["top_right"].setGeometry(w - grip_size, 0, grip_size, grip_size)
        self.grips["bottom_left"].setGeometry(0, h - grip_size, grip_size, grip_size)
        self.grips["bottom_right"].setGeometry(w - grip_size, h - grip_size, grip_size, grip_size)

    def resize_from_grip(self, position: str, delta: QPoint):
        """Resizes the window based on movement of a CustomGrip.

        Calculates the new window geometry based on which grip was moved and
        the mouse delta. Enforces minimum size constraints.

        Args:
            position (str): The position of the grip being dragged (e.g., "top_left").
            delta (QPoint): The change in mouse position since the drag started.
        """
        if self._is_maximized:
            return

        # start with the geometry from when the drag began
        new_rect = QRect(self.start_geometry)

        # adjust the rectangle's sides based on the grip's position
        if "left" in position:
            new_rect.setLeft(self.start_geometry.left() + delta.x())
        if "right" in position:
            new_rect.setRight(self.start_geometry.right() + delta.x())
        if "top" in position:
            new_rect.setTop(self.start_geometry.top() + delta.y())
        if "bottom" in position:
            new_rect.setBottom(self.start_geometry.bottom() + delta.y())

        # enforce minimum size constraints to prevent snapping
        min_size = self.minimumSize()
        if new_rect.width() < min_size.width():
            # which side was dragged? adjust the appropriate side.
            if "left" in position:
                new_rect.setLeft(new_rect.right() - min_size.width())
            else: # right side was dragged
                new_rect.setRight(new_rect.left() + min_size.width())
        
        if new_rect.height() < min_size.height():
            # which side was dragged? adjust the appropriate side.
            if "top" in position:
                new_rect.setTop(new_rect.bottom() - min_size.height())
            else: # bottom side was dragged
                new_rect.setBottom(new_rect.top() + min_size.height())

        self.setGeometry(new_rect)


