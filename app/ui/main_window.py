"""app/ui/main_window.py

Defines the main application window, including the custom title bar and sidebar.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QStackedWidget, QVBoxLayout, QWidget
from qframelesswindow import FramelessWindow

from app.config import AppConfig
from app.core.utils.error_utils import log_and_handle_exception
from app.style.animation import WindowAnimator
from app.ui.components import SearchBar
from app.ui.components.navigation.sidebar import Sidebar
from app.ui.components.navigation.titlebar import TitleBar
from app.ui.managers.navigation.registry import NavigationRegistry
from app.ui.managers.navigation.routes import (
    get_sidebar_route_mapping,
    register_main_routes,
)
from app.ui.managers.navigation.service import NavigationService
from app.ui.utils.layout_utils import center_on_screen

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

        # ── Initialize Services & Connect Signals ──
        self.animator = WindowAnimator(self)
        self._setup_navigation()
        self._connect_signals()

        self.sidebar.buttons["btn_dashboard"].setChecked(True) # default selected
        self._navigate_to_route("/dashboard")

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

        # TODO: Add subheader - brief description specific to each view.

    def _create_stacked_pages(self):
        """Creates stacked pages."""
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(8)
        self.content_outer_layout.addLayout(self.content_layout)
        self.sw_pages = QStackedWidget()
        self.content_layout.addWidget(self.sw_pages)

    def _create_content_area(self):
        """Creates the content area."""
        self.content_area = QWidget()
        self.content_area.setObjectName("ContentArea")
        self.body_layout.addWidget(self.content_area)

        self.content_outer_layout = QVBoxLayout(self.content_area)
        self.content_outer_layout.setContentsMargins(0, 0, 0, 0)
        self.content_outer_layout.setSpacing(0)

    def _setup_navigation(self):
        """Initialize the navigation service and register routes."""
        # Register all main routes
        register_main_routes()

        # Create navigation service instance
        self.navigation_service = NavigationService.create(self.sw_pages)

        # Connect navigation service signals for header updates
        self.navigation_service.navigation_completed.connect(self._on_navigation_completed)
        
        # Preload critical views for better performance
        self._preload_critical_views()

    def _preload_critical_views(self):
        """Preload frequently accessed views to eliminate loading delays."""
        from _dev_tools import DebugLogger
        from app.ui.managers.navigation.registry import RouteConstants
        
        # List of routes to preload
        critical_routes = [
            RouteConstants.RECIPES_BROWSE,           # Normal recipe browsing
            RouteConstants.RECIPES_BROWSE_SELECTION, # Recipe selection for meal planning
            RouteConstants.MEAL_PLANNER,             # Meal planning view
            RouteConstants.SHOPPING_LIST,            # Shopping list view
        ]
        
        DebugLogger.log("Preloading critical views for better performance...", "info")
        
        for route in critical_routes:
            try:
                # Trigger view creation by navigating to it (but don't show it)
                route_match = NavigationRegistry.match_route(route)
                if route_match:
                    # This will create and cache the view instance
                    view_instance = NavigationRegistry.get_instance(route_match)
                    DebugLogger.log(f"Preloaded view: {route} ({type(view_instance).__name__})", "info")
                else:
                    DebugLogger.log(f"Failed to match route for preloading: {route}", "warning")
            except Exception as e:
                DebugLogger.log(f"Failed to preload view {route}: {e}", "error")
        
        DebugLogger.log("View preloading completed", "info")

    def _navigate_to_route(self, route_path: str):
        """Navigate to a specific route using the navigation service."""
        if hasattr(self, 'navigation_service'):
            success = self.navigation_service.navigate_to(route_path)
            if not success:
                log_and_handle_exception(
                    "navigation",
                    Exception(f"Failed to navigate to route: {route_path}")
                )

    def _on_navigation_completed(self, path: str, params: dict):
        """Handle navigation completion to update UI state."""
        # Get header text from route registry to maintain single source of truth
        route_match = NavigationRegistry.match_route(path)
        header_text = "MealGenie"  # default

        if route_match and route_match.config.title:
            header_text = route_match.config.title

        self.lbl_header.setText(header_text)

    def _connect_signals(self):
        """Connect all UI signals to their respective slots."""
        # Title Bar
        self.title_bar.close_clicked.connect(self.close)
        self.title_bar.minimize_clicked.connect(self.animator.animate_minimize)
        self.title_bar.maximize_clicked.connect(self.animator.animate_toggle_maximize)
        self.title_bar.sidebar_toggled.connect(self.sidebar_toggle_requested.emit)

        # Sidebar
        self.sidebar_toggle_requested.connect(self.sidebar.toggle)

        # Connect sidebar buttons to navigation service
        route_mapping = get_sidebar_route_mapping()
        for button_name, route_path in route_mapping.items():
            button = self.sidebar.buttons.get(button_name)
            if button:
                button.clicked.connect(lambda checked, path=route_path: self._navigate_to_route(path))

        # Connect exit button
        self.sidebar.buttons["btn_exit"].clicked.connect(self.close)


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
