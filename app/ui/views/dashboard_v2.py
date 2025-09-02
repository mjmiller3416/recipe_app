"""app/ui/views/dashboard_v2.py

Dashboard view migrated to the new route-based navigation system.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout

from app.style.icon.config import Name, Type
from app.ui.components.layout.card import Card
from app.ui.components.widgets.button import Button
from app.ui.services.navigation_views import MainView
from app.ui.services.navigation_registry import NavigationRegistry, ViewType, RouteConstants
from _dev_tools import DebugLogger


@NavigationRegistry.register(
    path=RouteConstants.DASHBOARD,
    view_type=ViewType.MAIN,
    title="Dashboard",
    description="Main dashboard overview"
)
class Dashboard(MainView):
    """Dashboard view with route-based navigation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Dashboard")
        DebugLogger.log("Initializing Dashboard page (v2)", "info")
        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        """Build the dashboard UI."""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Example Card
        card = Card(card_type="Primary")
        card.setAttribute(Qt.WA_StyledBackground, True)
        card.expandWidth(False)
        card.setHeader("Dashboard Overview")
        card.setSubHeader("This is a placeholder for dashboard content.")

        summary_label = QLabel("This is a placeholder for dashboard content.")
        summary_label.setProperty("font", "Body")
        summary_label.setWordWrap(True)
        card.addWidget(summary_label)
        self.layout.addWidget(card)

        # Navigation test buttons
        self.btn_recipes = Button(
            label="View Recipes",
            type=Type.PRIMARY
        )
        self.btn_recipes.setIcon(Name.VIEW_RECIPES)
        self.btn_recipes.setIconSize(20, 20)
        self.btn_recipes.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.layout.addWidget(self.btn_recipes)

        self.btn_meal_planner = Button(
            label="Meal Planner",
            type=Type.SECONDARY
        )
        self.btn_meal_planner.setIcon(Name.MEAL_PLANNER)
        self.btn_meal_planner.setIconSize(20, 20)
        self.btn_meal_planner.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.layout.addWidget(self.btn_meal_planner)

        # Add stretch to push content to top
        self.layout.addStretch()

    def _connect_signals(self):
        """Connect button signals to navigation."""
        self.btn_recipes.clicked.connect(
            lambda: self.navigate_to(RouteConstants.RECIPES_BROWSE)
        )
        self.btn_meal_planner.clicked.connect(
            lambda: self.navigate_to(RouteConstants.MEAL_PLANNER)
        )

    def on_route_changed(self, path: str, params: dict):
        """Handle route changes - refresh data if needed."""
        DebugLogger.log(f"Dashboard route changed: {path}", "info")
        # Add any dashboard-specific initialization here

    def before_navigate_to(self, path: str, params: dict) -> bool:
        """Called before navigating to dashboard."""
        DebugLogger.log("Preparing to show dashboard", "info")
        return True

    def after_navigate_to(self, path: str, params: dict):
        """Called after navigating to dashboard."""
        DebugLogger.log("Dashboard is now active", "info")
        # Refresh dashboard data if needed

    def before_navigate_from(self, next_path: str, next_params: dict) -> bool:
        """Called before navigating away from dashboard."""
        DebugLogger.log(f"Leaving dashboard for: {next_path}", "info")
        # Save any dashboard state if needed
        return True
