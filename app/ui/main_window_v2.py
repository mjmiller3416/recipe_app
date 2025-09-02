"""app/ui/main_window_v2.py

MainWindow updated for the new route-based navigation system.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QStackedWidget,
    QVBoxLayout, QWidget)
from qframelesswindow import FramelessWindow

from ..config import APPLICATION_WINDOW
from app.style.animation import WindowAnimator
from app.ui.components import SearchBar
from app.ui.components.navigation.sidebar_v2 import Sidebar, connect_sidebar_navigation
from app.ui.components.navigation.titlebar import TitleBar
from app.ui.services.navigation_service_v2 import NavigationService
from app.ui.utils.layout_utils import center_on_screen
from _dev_tools import DebugLogger


# ── Constants ───────────────────────────────────────────────────────────────────────────────────────────────
SETTINGS = APPLICATION_WINDOW["SETTINGS"]


class MainWindow(FramelessWindow):
    """The main application window with new route-based navigation system.

    This class serves as the central hub of the user interface, using qframelesswindow
    to provide a native look and feel for the window border and title bar.
    It incorporates a custom `TitleBar`, a collapsible `Sidebar`, and a `QStackedWidget`
    to display different application views (pages).

    Key Changes from v1:
    - Uses NavigationService v2 with route-based navigation
    - Automatic view registration instead of hardcoded page mapping
    - Enhanced sidebar with route integration
    - Navigation history support

    Attributes:
        animator (WindowAnimator): Handles window animations like minimize/maximize.
        title_bar (TitleBar): The custom title bar widget.
        sidebar (Sidebar): The navigation sidebar widget.
        sw_pages (QStackedWidget): Widget that holds and switches between different pages.
        navigation (NavigationService): Service responsible for route-based navigation.
    """
    # ── Signals ──────────────────────────────────────────────────────────────────────────────
    sidebar_toggle_requested = Signal()

    def __init__(self):
        """Initializes the MainWindow with new navigation system."""
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

        # ── Initialize New Navigation System ──
        self.animator = WindowAnimator(self)
        self._setup_navigation()
        self._register_views()
        self._connect_signals()

        # Set initial page
        self._navigate_to_initial_page()

        # Resize and center the window at the end
        self.resize(int(SETTINGS["WINDOW_WIDTH"]), int(SETTINGS["WINDOW_HEIGHT"]))
        center_on_screen(self)

    def _setup_navigation(self):
        """Setup the new navigation service."""
        # Create navigation service
        self.navigation = NavigationService.create(self.sw_pages)

        # Connect sidebar to navigation service
        connect_sidebar_navigation(self.sidebar)

        # Connect navigation signals for header updates
        self.navigation.route_changed.connect(self._on_route_changed)
        self.navigation.navigation_completed.connect(self._on_navigation_completed)

        DebugLogger.log("Navigation service v2 initialized", "info")

    def _register_views(self):
        """Register all application views with the navigation system."""
        # Import views to trigger their route registration
        # This replaces the old build_and_register_pages() method
        try:
            # Import v2 views (with route registration)
            from app.ui.views.dashboard_v2 import Dashboard
            from app.ui.views.view_recipes_v2 import ViewRecipes, StandaloneRecipeBrowser

            # Import existing views and register them
            self._register_legacy_views()

            DebugLogger.log("All views registered with navigation system", "info")

        except ImportError as e:
            DebugLogger.log(f"Could not import some views: {e}", "warning")
            # Fallback to register existing views manually
            self._register_legacy_views()

    def _register_legacy_views(self):
        """Register existing views that haven't been migrated yet."""
        from app.ui.services.navigation_registry import NavigationRegistry, ViewType, RouteConstants

        # Register views that haven't been converted to v2 yet
        try:
            from app.ui.views.meal_planner import MealPlanner
            NavigationRegistry.register_route(
                path=RouteConstants.MEAL_PLANNER,
                view_class=MealPlanner,
                view_type=ViewType.MAIN,
                title="Meal Planner"
            )
        except ImportError:
            DebugLogger.log("MealPlanner not available for registration", "warning")

        try:
            from app.ui.views.shopping_list import ShoppingList
            NavigationRegistry.register_route(
                path=RouteConstants.SHOPPING_LIST,
                view_class=ShoppingList,
                view_type=ViewType.MAIN,
                title="Shopping List"
            )
        except ImportError:
            DebugLogger.log("ShoppingList not available for registration", "warning")

        try:
            from app.ui.views.add_recipes import AddRecipes
            NavigationRegistry.register_route(
                path="/recipes/add",
                view_class=AddRecipes,
                view_type=ViewType.MAIN,
                title="Add Recipe"
            )
        except ImportError:
            DebugLogger.log("AddRecipes not available for registration", "warning")

        try:
            from app.ui.views.settings import Settings
            NavigationRegistry.register_route(
                path=RouteConstants.SETTINGS,
                view_class=Settings,
                view_type=ViewType.MAIN,
                title="Settings"
            )
        except ImportError:
            DebugLogger.log("Settings not available for registration", "warning")

    def _connect_signals(self):
        """Connect all UI signals to their respective slots."""
        # Title Bar
        self.title_bar.close_clicked.connect(self.close)
        self.title_bar.minimize_clicked.connect(self.animator.animate_minimize)
        self.title_bar.maximize_clicked.connect(self.animator.animate_toggle_maximize)
        self.title_bar.sidebar_toggled.connect(self.sidebar_toggle_requested.emit)

        # Sidebar
        self.sidebar_toggle_requested.connect(self.sidebar.toggle)

    def _navigate_to_initial_page(self):
        """Navigate to the initial page using the new system."""
        from app.ui.services.navigation_registry import RouteConstants

        # Navigate to dashboard initially
        success = self.navigation.navigate_to(RouteConstants.DASHBOARD)
        if not success:
            DebugLogger.log("Failed to navigate to initial page", "error")

    def _on_route_changed(self, path: str, params: dict):
        """Handle route changes to update UI state."""
        # Update header based on route
        self._update_header_for_route(path)

        # Update sidebar active state (handled by sidebar itself)
        DebugLogger.log(f"Route changed to: {path}", "info")

    def _on_navigation_completed(self, path: str, params: dict):
        """Handle completed navigation."""
        # Handle any post-navigation setup
        current_view = self.navigation.get_current_view()

        if current_view:
            # Auto-focus recipe name field when AddRecipes page is shown
            if path == "/recipes/add" and hasattr(current_view, 'le_recipe_name'):
                from PySide6.QtCore import QTimer
                QTimer.singleShot(0, current_view.le_recipe_name.setFocus)

        DebugLogger.log(f"Navigation completed to: {path}", "info")

    def _update_header_for_route(self, path: str):
        """Update header label based on route path."""
        from app.ui.services.navigation_registry import NavigationRegistry

        # Get route info for title
        route_match = NavigationRegistry.match_route(path)
        if route_match and route_match.config.title:
            self.lbl_header.setText(route_match.config.title)
        else:
            # Fallback mapping for routes without titles
            title_mapping = {
                "/dashboard": "Dashboard",
                "/meal-planner": "Meal Planner",
                "/recipes/browse": "View Recipes",
                "/recipes/browser": "Recipe Browser",
                "/shopping-list": "Shopping List",
                "/recipes/add": "Add Recipe",
                "/settings": "Settings",
            }
            title = title_mapping.get(path, path.replace("/", "").replace("-", " ").title())
            self.lbl_header.setText(title)

    @property
    def _is_maximized(self) -> bool:
        return self.isMaximized()

    def keyPressEvent(self, event):
        """Ignore the Escape key to prevent accidental app closure."""
        if event.key() == Qt.Key_Escape:
            event.ignore()
            return
        super().keyPressEvent(event)

    def closeEvent(self, event):
        """Persist application state before closing."""
        # Get current meal planner view and save if needed
        current_view = self.navigation.get_current_view()
        if hasattr(current_view, 'saveMealPlan'):
            current_view.saveMealPlan()

        # Also check if we have a meal planner in navigation history
        # and save it regardless of current view
        from app.ui.services.navigation_registry import RouteConstants

        # Try to get meal planner instance from registry cache
        try:
            meal_planner_route = NavigationRegistry.match_route(RouteConstants.MEAL_PLANNER)
            if meal_planner_route:
                # Check if there's a cached instance
                from app.ui.services.navigation_registry import NavigationRegistry
                # This is a simplified approach - in practice, you might need to track instances differently
                pass
        except:
            pass

        super().closeEvent(event)
