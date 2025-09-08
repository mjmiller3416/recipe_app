"""app/ui/main_window.py

Defines the main application window, including the custom title bar and sidebar.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QStackedWidget, QVBoxLayout, QWidget
from qframelesswindow import FramelessWindow

from app.config import AppConfig
from app.style.animation import WindowAnimator
from app.ui.navigator import Navigator
from app.ui.components import SearchBar
from app.ui.components.navigation.sidebar import Sidebar
from app.ui.components.navigation.titlebar import TitleBar
from app.ui.utils.layout_utils import center_on_screen
from app.ui.views import (
    AddRecipesView,
    DashboardView,
    MealPlannerView,
    RecipeBrowserView,
    SettingsView,
    ShoppingListView,
    ViewRecipe,
)

# ── Application Window ──────────────────────────────────────────────────────────────────────────────────────
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

    sidebar_toggle_requested = Signal()

    def __init__(self):
        """Initializes the MainWindow.

        Args:
            theme_controller (ThemeController): The controller for managing app themes.
        """
        super().__init__()

        # ── Window Properties ──
        self.setMinimumSize(800, 360)

        self._build_ui()
        self.animator = WindowAnimator(self)
        self._connect_signals()
        self._connect_navigation()

        self.resize(int(AppConfig.WINDOW_WIDTH), int(AppConfig.WINDOW_HEIGHT)) # initial size
        center_on_screen(self)

    @property
    def _is_maximized(self) -> bool:
        return self.isMaximized()

    def _build_ui(self):
        """Builds the UI."""

        # Title Bar
        self.title_bar = TitleBar(self)
        self.setTitleBar(self.title_bar)
        self._isResizeEnabled = True

        # Main Layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, self.title_bar.height(), 0, 0)
        self.main_layout.setSpacing(0)

        # Body Layout
        self.window_body = QWidget(self)
        self.body_layout = QHBoxLayout(self.window_body)
        self.body_layout.setContentsMargins(1, 0, 1, 1)
        self.body_layout.setSpacing(0)

        self.main_layout.addWidget(self.window_body) # add body widget to the main layout

        # Sidebar
        self.sidebar = Sidebar()
        self.body_layout.addWidget(self.sidebar)

        # Content Area
        self._create_content_area()
        self._create_header_widgets()
        self._create_stacked_pages()

    def _create_header_widgets(self):
        """Creates header widgets."""
        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(20, 30, 20, 20)
        self.content_outer_layout.addLayout(self.header_layout)

        self.lbl_header = QLabel()
        self.lbl_header.setObjectName("AppHeader")
        self.lbl_header.setProperty("tag", "Header")
        self.lbl_header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.header_layout.addWidget(self.lbl_header, alignment=Qt.AlignLeft)

        self.search_bar = SearchBar()
        self.header_layout.addWidget(self.search_bar, alignment=Qt.AlignRight)

    def _create_stacked_pages(self):
        """Creates stacked pages."""
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(8)
        self.content_outer_layout.addLayout(self.content_layout)
        self.view_stack = QStackedWidget()
        self.content_layout.addWidget(self.view_stack)

    def _create_content_area(self):
        """Creates the content area."""
        self.content_area = QWidget()
        self.content_area.setObjectName("ContentArea")
        self.body_layout.addWidget(self.content_area)

        self.content_outer_layout = QVBoxLayout(self.content_area)
        self.content_outer_layout.setContentsMargins(0, 0, 0, 0)
        self.content_outer_layout.setSpacing(0)

    def _setup_header_text(self, text: str):
        """Set header text."""
        self.lbl_header.setText(text)

    def _connect_signals(self):
        """Connect all UI signals to their respective slots."""
        # Title Bar
        self.title_bar.close_clicked.connect(self.close)
        self.title_bar.minimize_clicked.connect(self.animator.animate_minimize)
        self.title_bar.maximize_clicked.connect(self.animator.animate_toggle_maximize)
        self.title_bar.sidebar_toggled.connect(self.sidebar_toggle_requested.emit)
        self.sidebar_toggle_requested.connect(self.sidebar.toggle)  # Toggle Sidebar

        self.sidebar.buttons["btn_exit"].clicked.connect(self.close)

    def _connect_navigation(self):
        self.nav = Navigator(self.view_stack)
        self.nav.set_header_label(self.lbl_header)

        # Register all views
        self.nav.register("dashboard", DashboardView)
        self.nav.register("meal_planner", MealPlannerView)
        self.nav.register("recipes", RecipeBrowserView)
        self.nav.register("shopping", ShoppingListView)
        self.nav.register("add_recipes", AddRecipesView)
        self.nav.register("settings", SettingsView)
        self.nav.register("view_recipe", ViewRecipe)

        # Connect sidebar buttons
        self.sidebar.btn_dashboard.clicked.connect(
            lambda: self.nav.show("dashboard")
        )
        self.sidebar.btn_meal_planner.clicked.connect(
            lambda: self.nav.show("meal_planner")
        )
        self.sidebar.btn_browse_recipes.clicked.connect(
            lambda: self.nav.show("recipes")
        )
        self.sidebar.btn_shopping_list.clicked.connect(
            lambda: self.nav.show("shopping")
        )
        self.sidebar.btn_add_recipes.clicked.connect(
            lambda: self.nav.show("add_recipes")
        )
        self.sidebar.btn_settings.clicked.connect(
            lambda: self.nav.show("settings")
        )

        # Show dashboard by default
        self.nav.show("dashboard")
        self.sidebar.btn_dashboard.setChecked(True)

# ── Event Handlers ──────────────────────────────────────────────────────────────────────────────────────────
    def keyPressEvent(self, event):
        """Ignore the Escape key to prevent accidental app closure."""
        if event.key() == Qt.Key_Escape:
            event.ignore()
            return
        super().keyPressEvent(event)

    def closeEvent(self, event):
        """Handle window close event to save geometry and settings."""
        super().closeEvent(event)
