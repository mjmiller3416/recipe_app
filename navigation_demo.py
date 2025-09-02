"""navigation_demo.py

Demonstration of the new route-based navigation system.
Shows how views can be navigated to, how RecipeBrowser works as both
embedded and standalone, and the key benefits of the new architecture.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt

from app.ui.services.navigation_registry import NavigationRegistry, ViewType, RouteConstants
from app.ui.services.navigation_service_v2 import NavigationService, navigate_to
from app.ui.services.navigation_stack import NavigationStackManager
from app.ui.components.navigation.sidebar_v2 import Sidebar, connect_sidebar_navigation
from _dev_tools import DebugLogger


class NavigationDemo(QMainWindow):
    """Demo application showing the new navigation system."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Navigation System Demo")
        self.setGeometry(100, 100, 1200, 800)

        self.setup_ui()
        self.setup_navigation()
        self.register_demo_routes()

    def setup_ui(self):
        """Setup the demo UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create sidebar
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)

        # Create main content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # Add demo controls
        self.create_demo_controls(content_layout)

        # Create main stacked widget for navigation
        self.main_stack = QStackedWidget()
        content_layout.addWidget(self.main_stack)

        main_layout.addWidget(content_widget)

    def create_demo_controls(self, layout):
        """Create demo control buttons."""
        controls_widget = QWidget()
        controls_layout = QHBoxLayout(controls_widget)

        # Navigation test buttons
        btn_dashboard = QPushButton("Dashboard")
        btn_dashboard.clicked.connect(lambda: navigate_to(RouteConstants.DASHBOARD))

        btn_recipes = QPushButton("Browse Recipes")
        btn_recipes.clicked.connect(lambda: navigate_to(RouteConstants.RECIPES_BROWSE))

        btn_standalone_browser = QPushButton("Standalone Recipe Browser")
        btn_standalone_browser.clicked.connect(lambda: navigate_to("/recipes/browser"))

        btn_back = QPushButton("← Back")
        btn_back.clicked.connect(lambda: NavigationService.get_instance().go_back())

        btn_forward = QPushButton("Forward →")
        btn_forward.clicked.connect(lambda: NavigationService.get_instance().go_forward())

        # Add buttons
        controls_layout.addWidget(btn_dashboard)
        controls_layout.addWidget(btn_recipes)
        controls_layout.addWidget(btn_standalone_browser)
        controls_layout.addWidget(btn_back)
        controls_layout.addWidget(btn_forward)
        controls_layout.addStretch()

        layout.addWidget(controls_widget)

    def setup_navigation(self):
        """Setup the navigation service."""
        self.nav_service = NavigationService.create(self.main_stack)

        # Connect sidebar to navigation
        connect_sidebar_navigation(self.sidebar)

        # Connect navigation service signals
        self.nav_service.navigation_started.connect(
            lambda path, params: print(f"Navigation started: {path} with params: {params}")
        )
        self.nav_service.navigation_completed.connect(
            lambda path, params: print(f"Navigation completed: {path}")
        )
        self.nav_service.navigation_failed.connect(
            lambda path, error: print(f"Navigation failed: {path} - {error}")
        )

    def register_demo_routes(self):
        """Register demo routes to show the system working."""
        # Import and register the v2 views we created
        try:
            from app.ui.views.dashboard_v2 import Dashboard
            from app.ui.views.view_recipes_v2 import ViewRecipes
            from app.ui.components.composite.recipe_browser_v2 import StandaloneRecipeBrowser

            print("Registered demo routes successfully")
        except ImportError as e:
            print(f"Could not import demo views: {e}")

            # Register simple demo views instead
            self.register_simple_demo_routes()

    def register_simple_demo_routes(self):
        """Register simple demo routes for testing."""
        from PySide6.QtWidgets import QLabel
        from app.ui.services.navigation_views import MainView

        @NavigationRegistry.register("/dashboard", ViewType.MAIN, title="Dashboard")
        class DemoMainView(MainView):
            def __init__(self, parent=None):
                super().__init__(parent)
                layout = QVBoxLayout(self)
                layout.addWidget(QLabel("Dashboard Demo View"))

        @NavigationRegistry.register("/recipes/browse", ViewType.MAIN, title="Browse Recipes")
        class DemoRecipesView(MainView):
            def __init__(self, parent=None):
                super().__init__(parent)
                layout = QVBoxLayout(self)
                layout.addWidget(QLabel("Recipes Browse Demo View"))

        @NavigationRegistry.register("/recipes/browser", ViewType.EMBEDDED, title="Recipe Browser")
        class DemoBrowserView(MainView):
            def __init__(self, parent=None):
                super().__init__(parent)
                layout = QVBoxLayout(self)
                layout.addWidget(QLabel("Standalone Recipe Browser Demo"))

        print("Registered simple demo routes")


def show_navigation_info():
    """Show information about registered routes."""
    print("\n=== Navigation System Demo ===")
    print("Registered Routes:")

    routes = NavigationRegistry.get_routes()
    for route in routes:
        print(f"  {route.path} -> {route.view_class.__name__} ({route.view_type.value})")

    print(f"\nTotal routes: {len(routes)}")
    print("Navigation stack contexts:", NavigationStackManager.get_all_contexts())
    print("\n=== Demo Controls ===")
    print("- Use sidebar buttons for navigation")
    print("- Use demo control buttons to test specific features")
    print("- Back/Forward buttons to test navigation history")
    print("- Try the 'Standalone Recipe Browser' button to see embedded view as standalone")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create and show demo
    demo = NavigationDemo()
    demo.show()

    # Show navigation info
    show_navigation_info()

    # Start with dashboard
    navigate_to(RouteConstants.DASHBOARD)

    sys.exit(app.exec())
