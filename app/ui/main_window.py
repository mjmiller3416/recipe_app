"""app/ui/main_window.py

Defines the main application window, including the custom title bar and sidebar.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QStackedWidget,
    QVBoxLayout, QWidget)
from qframelesswindow import FramelessWindow

from ..config import APPLICATION_WINDOW
from app.style.animation import WindowAnimator
from app.ui.components import SearchBar
from app.ui.components.navigation.sidebar import Sidebar
from app.ui.components.navigation.titlebar import TitleBar
from app.ui.utils.layout_utils import center_on_screen

# ── Constants ────────────────────────────────────────────────────────────────────────────────
SETTINGS = APPLICATION_WINDOW["SETTINGS"]


# ── Application Window ───────────────────────────────────────────────────────────────────────
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
    """
    # ── Signals ──────────────────────────────────────────────────────────────────────────────
    sidebar_toggle_requested = Signal()

    def __init__(self):
        """Initializes the MainWindow.

        Args:
            theme_controller (ThemeController): The controller for managing app themes.
        """
        super().__init__()

        # ── Window Properties ──
        self.setMinimumSize(800, 360)

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
        # TODO: Add subheader - brief description specific to each view.
        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(20, 30, 20, 20)
        self.content_outer_layout.addLayout(self.header_layout)

        # Header Widgets
        self.lbl_header = QLabel()
        self.lbl_header.setObjectName("AppHeader")
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
        self._connect_signals()


        # Set initial page (after signal connections)
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

        button_map = {
            "btn_dashboard": "dashboard",
            "btn_meal_planner": "meal_planner",
            "btn_view_recipes": "view_recipes",
            "btn_shopping_list": "shopping_list",
            "btn_add_recipes": "add_recipe",
            "btn_settings": "settings",
        }
        #TODO - Connect Sidebar Buttons to Navigation Service

    def _update_header(self, page_name: str):
        """Update header label text based on page name."""
        mapping = {
            "dashboard": "Dashboard",
            "meal_planner": "Meal Planner",
            "view_recipes": "View Recipes",
            "shopping_list": "Shopping List",
            "add_recipe": "Add Recipe",
            "settings": "Settings",
        }
        self.lbl_header.setText(mapping.get(page_name, page_name.replace("_", " ").title()))

    def keyPressEvent(self, event):
        """Ignore the Escape key to prevent accidental app closure."""
        if event.key() == Qt.Key_Escape:
            event.ignore()
            return
        super().keyPressEvent(event)

    def closeEvent(self, event):
        """Handle window close event to save geometry and settings."""
        super().closeEvent(event)
