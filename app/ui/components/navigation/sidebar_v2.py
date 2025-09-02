"""app/ui/components/navigation/sidebar_v2.py

Enhanced sidebar with route-based navigation integration.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from typing import Dict, Optional

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup, QLabel, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

from app.config import SIDEBAR
from app.style import Theme
from app.style.animation import Animator
from app.style.icon.config import Name, Type
from app.style.theme.config import Qss
from app.ui.components.images import AvatarLoader
from app.ui.components.widgets.button import Button
from app.ui.services.navigation_registry import RouteConstants
from app.ui.utils.layout_utils import create_fixed_wrapper
from _dev_tools import DebugLogger

# ── Constants ───────────────────────────────────────────────────────────────────────────────────────────────
START = SIDEBAR["SETTINGS"]["EXPANDED_WIDTH"]
END = SIDEBAR["SETTINGS"]["COLLAPSED_WIDTH"]
DURATION = SIDEBAR["SETTINGS"]["DURATION"]


# ── Sidebar Component ───────────────────────────────────────────────────────────────────────────────────────
class NavigationButton(Button):
    """Enhanced navigation button that tracks route information."""

    def __init__(self, label: str, route: str, icon: Name, **kwargs):
        super().__init__(label=label, type=Type.PRIMARY, icon=icon, **kwargs)

        self.route = route
        self.setObjectName("NavButton")
        self.setCheckable(True)
        self.setContentsMargins(20, 0, 0, 0)
        self.setFixedHeight(85)
        self.setIconSpacing(30)
        self.addLayoutStretch()

    def get_route(self) -> str:
        """Get the route associated with this button."""
        return self.route


# ── Sidebar ─────────────────────────────────────────────────────────────────────────────────────────────────
class Sidebar(QWidget):
    """Enhanced sidebar with route-based navigation."""

    # Signals
    navigation_requested = Signal(str)  # route path
    back_requested = Signal()
    forward_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMinimumWidth(0)
        self.setMaximumWidth(START)
        self._is_expanded = True
        self._current_route: Optional[str] = None

        # Register for component-specific styling
        Theme.register_widget(self, Qss.SIDEBAR)

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        self._create_avatar()
        self._create_navigation_buttons()
        self._create_action_buttons()
        self._setup_navigation_connections()

    def _create_navigation_buttons(self):
        """Create main navigation buttons with route mapping."""
        self.nav_button_group = QButtonGroup(self)
        self.nav_button_group.setExclusive(True)

        # Define navigation buttons with their routes
        nav_buttons = [
            ("Dashboard", RouteConstants.DASHBOARD, Name.DASHBOARD),
            ("Meal Planner", RouteConstants.MEAL_PLANNER, Name.MEAL_PLANNER),
            ("View Recipes", RouteConstants.RECIPES_BROWSE, Name.VIEW_RECIPES),
            ("Shopping List", RouteConstants.SHOPPING_LIST, Name.SHOPPING_LIST),
            ("Add Recipes", "/recipes/add", Name.ADD_RECIPES),  # Using direct route
        ]

        self._nav_buttons: Dict[str, NavigationButton] = {}

        for label, route, icon in nav_buttons:
            button = NavigationButton(label, route, icon)
            button.clicked.connect(lambda checked, r=route: self._handle_nav_click(r))

            self.mainLayout.addWidget(button)
            self.nav_button_group.addButton(button)

            # Store button reference with route key for easy lookup
            self._nav_buttons[route] = button

        # Add spacer
        self.mainLayout.addItem(
            QSpacerItem(212, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

    def _create_action_buttons(self):
        """Create non-navigation action buttons."""
        self.btn_settings = self._create_action_button("Settings", Name.SETTINGS)
        self.btn_exit = self._create_action_button("Exit", Name.EXIT)

        # Connect action buttons
        self.btn_settings.clicked.connect(lambda: self._handle_nav_click(RouteConstants.SETTINGS))
        self.btn_exit.clicked.connect(self._handle_exit_click)

    def _create_action_button(self, label: str, icon: Name) -> Button:
        """Create a non-checkable action button."""
        button = Button(label=label, type=Type.PRIMARY, icon=icon)
        button.setObjectName("NavButton")
        button.setCheckable(False)
        button.setContentsMargins(20, 0, 0, 0)
        button.setFixedHeight(85)
        button.setIconSpacing(30)
        button.addLayoutStretch()

        self.mainLayout.addWidget(button)
        return button

    def _setup_navigation_connections(self):
        """Setup connections to the navigation service."""
        # Connect to navigation service signals when available
        from app.ui.services.navigation_service_v2 import NavigationService
        nav_service = NavigationService.get_instance()

        if nav_service:
            # Listen for route changes to update active button
            nav_service.route_changed.connect(self.set_active_route)

            # Connect back/forward requests
            self.back_requested.connect(nav_service.go_back)
            self.forward_requested.connect(nav_service.go_forward)

            DebugLogger.log("Sidebar connected to navigation service", "info")

    def _handle_nav_click(self, route: str):
        """Handle navigation button clicks."""
        DebugLogger.log(f"Sidebar navigation requested: {route}", "info")
        self.navigation_requested.emit(route)

    def _handle_exit_click(self):
        """Handle exit button click."""
        DebugLogger.log("Exit requested from sidebar", "info")
        from PySide6.QtWidgets import QApplication
        QApplication.quit()

    def set_active_route(self, route: str, params: dict = None):
        """
        Set the active route and update button states.

        Args:
            route: The current active route
            params: Route parameters (unused for sidebar)
        """
        self._current_route = route

        # Update button states
        for route_path, button in self._nav_buttons.items():
            if route_path == route:
                button.setChecked(True)
            else:
                button.setChecked(False)

        DebugLogger.log(f"Sidebar active route updated: {route}", "info")

    def get_active_route(self) -> Optional[str]:
        """Get the currently active route."""
        return self._current_route

    def add_navigation_button(self, label: str, route: str, icon: Name, position: int = -1):
        """
        Dynamically add a navigation button.

        Args:
            label: Button label
            route: Route path
            icon: Button icon
            position: Position to insert (-1 for end)
        """
        button = NavigationButton(label, route, icon)
        button.clicked.connect(lambda checked, r=route: self._handle_nav_click(r))

        if position == -1:
            # Add before the spacer (find spacer position)
            spacer_index = -1
            for i in range(self.mainLayout.count()):
                item = self.mainLayout.itemAt(i)
                if isinstance(item, QSpacerItem):
                    spacer_index = i
                    break

            if spacer_index >= 0:
                self.mainLayout.insertWidget(spacer_index, button)
            else:
                self.mainLayout.addWidget(button)
        else:
            self.mainLayout.insertWidget(position, button)

        self.nav_button_group.addButton(button)
        self._nav_buttons[route] = button

        DebugLogger.log(f"Added navigation button: {label} -> {route}", "info")

    def remove_navigation_button(self, route: str):
        """
        Remove a navigation button by route.

        Args:
            route: Route path of button to remove
        """
        if route in self._nav_buttons:
            button = self._nav_buttons[route]
            self.nav_button_group.removeButton(button)
            self.mainLayout.removeWidget(button)
            button.deleteLater()
            del self._nav_buttons[route]

            DebugLogger.log(f"Removed navigation button for route: {route}", "info")

    @property
    def buttons(self) -> Dict[str, NavigationButton]:
        """Get all navigation buttons."""
        return self._nav_buttons.copy()

    @property
    def is_expanded(self) -> bool:
        return self._is_expanded

    def toggle(self):
        """Toggle sidebar expansion state."""
        DebugLogger.log(
            f"Toggling sidebar: currently {'expanded' if self._is_expanded else 'collapsed'}"
        )

        start = self.maximumWidth()
        end = END if self._is_expanded else START
        duration = DURATION

        Animator.animate_width(self, start, end, duration)
        self._is_expanded = not self._is_expanded

    def go_back(self):
        """Request backward navigation."""
        self.back_requested.emit()

    def go_forward(self):
        """Request forward navigation."""
        self.forward_requested.emit()

    def _create_avatar(self) -> AvatarLoader:
        """Create the user avatar section."""
        avatar = AvatarLoader(size=QSize(240, 240))
        username = QLabel("@username")
        username.setObjectName("UsernameLabel")
        username.setAlignment(Qt.AlignCenter)
        avatar_wrapper = create_fixed_wrapper(
            widgets=[avatar, username],
            fixed_width=self.width(),
            alignment=Qt.AlignHCenter,
            direction="vertical",
            margins=(0, 40, 0, 30),
        )
        self.mainLayout.addWidget(avatar_wrapper)


# ── Helper Functions ────────────────────────────────────────────────────────────────────────────────────────
def connect_sidebar_navigation(sidebar: Sidebar):
    """
    Connect a sidebar instance to the navigation service.

    Args:
        sidebar: Sidebar instance to connect
    """
    from app.ui.services.navigation_service_v2 import NavigationService

    nav_service = NavigationService.get_instance()
    if nav_service:
        # Connect navigation requests from sidebar to service
        sidebar.navigation_requested.connect(
            lambda route: nav_service.navigate_to(route)
        )

        # Connect route changes from service to sidebar
        nav_service.route_changed.connect(sidebar.set_active_route)

        DebugLogger.log("Connected sidebar to navigation service", "info")
    else:
        DebugLogger.log("Navigation service not available for sidebar connection", "warning")
