# core\application\sidebar.py
"""Sidebar widget for the application's main navigation panel.

Provides user avatar, navigation buttons, and settings/exit controls.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QSizePolicy, QSpacerItem, QVBoxLayout, 
    QWidget, QButtonGroup, QLabel
)

from config import SIDEBAR
from core.controllers import AnimationController
from core.utils import DebugLogger
from core.helpers.ui_helpers import create_fixed_wrapper
from ui.animations import SidebarAnimator
from ui.components import AvatarLoader
from ui.widgets import NavButton

# ── Constants ───────────────────────────────────────────────────────────────────
ICONS = SIDEBAR["ICONS"]
START = SIDEBAR["SETTINGS"]["EXPANDED_WIDTH"]
END = SIDEBAR["SETTINGS"]["COLLAPSED_WIDTH"]
DURATION = SIDEBAR["SETTINGS"]["DURATION"]

# ── Class Definition ────────────────────────────────────────────────────────────
class Sidebar(QWidget):
    """Sidebar widget for the application main window.

    Provides the user avatar, username and a vertical stack of navigation buttons.
    includes dashboard, meal planner, recipe viewing, shopping list, add recipes, settings, and exit controls.

    Attributes:
        mainLayout (QVBoxLayout): main layout for the sidebar.
        avatar (AvatarLoader): widget displaying the user avatar.
        username (QLabel): label displaying the username.
        avatar_wrapper (QWidget): wrapper for avatar and username.
        btn_dashboard (NavButton): button for dashboard navigation.
        btn_meal_planner (NavButton): button for meal planner navigation.
        btn_view_recipes (NavButton): button for viewing recipes.
        btn_shopping_list (NavButton): button for shopping list navigation.
        btn_add_recipes (NavButton): button for adding recipes.
        btn_settings (NavButton): button for accessing settings.
        btn_exit (NavButton): button for exiting the application.

    """

    def __init__(self, parent=None):
        """Initialize the Sidebar widget.

        Args:
            parent (QWidget, optional): parent widget. Defaults to None.
        """
        super().__init__(parent)
        # properties
        self.setObjectName("Sidebar")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMinimumWidth(0)
        self.setMaximumWidth(START)  # start expanded
        self._is_expanded = True

        # main layout setup
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        # avatar and username
        self._create_avatar()

        # navigation buttons
        self.nav_button_group = QButtonGroup(self) # button group for exclusive selection
        self.nav_button_group.setExclusive(True)
        self.btn_dashboard = self._create_nav_button("Dashboard")
        self.btn_meal_planner = self._create_nav_button("Meal Planner")
        self.btn_view_recipes = self._create_nav_button("View Recipes")
        self.btn_shopping_list = self._create_nav_button("Shopping List")
        self.btn_add_recipes = self._create_nav_button("Add Recipes")

        # bottom spacer to push settings/exit to the bottom
        self.mainLayout.addItem(QSpacerItem(212, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # settings and exit buttons
        self.btn_settings = self._create_nav_button("Settings", is_checkable=False)
        self.btn_exit = self._create_nav_button("Exit", is_checkable=False)

    @property
    def buttons(self) -> dict[str, NavButton]:
        """Get all sidebar navigation and control buttons.

        Returns:
            dict[str, CTButton]: mapping of button names to CTButton instances.
        """
        return {
            "btn_dashboard": self.btn_dashboard,
            "btn_meal_planner": self.btn_meal_planner,
            "btn_view_recipes": self.btn_view_recipes,
            "btn_shopping_list": self.btn_shopping_list,
            "btn_add_recipes": self.btn_add_recipes,
            "btn_settings": self.btn_settings,
            "btn_exit": self.btn_exit,
        }
    
    @property
    def is_expanded(self) -> bool:
        """Check if the sidebar is currently expanded.

        Returns:
            bool: True if expanded, False if collapsed.
        """
        return self._is_expanded
    
    def toggle(self):
        """Toggle the sidebar's expanded/collapsed state."""
        DebugLogger.log(f"Toggling sidebar: currently {'expanded' if self._is_expanded else 'collapsed'}")

        start = self.maximumWidth()
        end = END if self._is_expanded else START
        duration = DURATION

        AnimationController.animate_width(self, start, end, duration)

        self._is_expanded = not self._is_expanded
        
    # ── Private Methods ─────────────────────────────────────────────────────────────
    def _create_nav_button(
            self, 
            label: str, 
            is_checkable: bool = True
    ) -> NavButton:
        """Create a navigation button for the sidebar.

        the label must match an entry in the ICONS config.

        Args:
            label (str): text label for the button.
            is_checkable (bool, optional): whether the button is checkable. Defaults to True.

        Returns:
            NavButton: the created navigation button.
        """
        icon_info = ICONS[label.replace(" ", "_").upper()]
        object_name = f"{label.replace(' ', '_')}Button"

        button = NavButton(
            file_path = icon_info["PATH"],
            icon_size = icon_info["SIZE"],
            variant   = icon_info["DYNAMIC"],
            text      = label,
            checkable = is_checkable,
            height    = 82,
        )
        button.setObjectName(object_name)
        print(object_name)
        self.mainLayout.addWidget(button)

        if is_checkable:
            self.nav_button_group.addButton(button)

        print(icon_info)

        return button
    
    def _create_avatar(self) -> AvatarLoader:
        avatar = AvatarLoader(size=QSize(240, 240))
        username = QLabel("@username")  # placeholder for username, set dynamically
        username.setObjectName("UsernameLabel")
        username.setAlignment(Qt.AlignCenter)
        avatar_wrapper = create_fixed_wrapper(
            widgets     = [avatar, username],
            fixed_width = self.width(),
            alignment   = Qt.AlignHCenter,
            direction   = "vertical",
            margins= (0, 40, 0, 30)
        )
        self.mainLayout.addWidget(avatar_wrapper)