# core\application\sidebar.py
"""Sidebar widget for the application's main navigation panel.

Provides user avatar, navigation buttons, and settings/exit controls.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import QSizePolicy, QSpacerItem, QVBoxLayout, QWidget, QLabel, QButtonGroup

from config import SIDEBAR
from core.controllers import AnimationController
from core.helpers.ui_helpers import create_fixed_wrapper
from ui.widgets import NavButton
from ui.components import AvatarLoader

# ── Constants ───────────────────────────────────────────────────────────────────
ICONS = SIDEBAR["ICONS"]
SETTINGS = SIDEBAR["SETTINGS"]

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

    Signals:
        close_app: emitted when the exit button is clicked.
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
        self._is_expanded = True

        # main layout setup
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        # avatar section
        self.avatar = AvatarLoader(size=QSize(240, 240))
        self.username = QLabel("@username")  # placeholder for username, set dynamically
        self.username.setObjectName("UsernameLabel")
        self.username.setAlignment(Qt.AlignCenter)
        self.avatar_wrapper = create_fixed_wrapper(
            widgets     = [self.avatar, self.username],
            fixed_width = 360,
            alignment   = Qt.AlignHCenter,
            direction   = "vertical",
            margins= (0, 40, 0, 30)
        )
        self.mainLayout.addWidget(self.avatar_wrapper)

        # button group for exclusive selection
        self.nav_button_group = QButtonGroup(self)
        self.nav_button_group.setExclusive(True)

        # navigation buttons
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
        target_width = SETTINGS["COLLAPSED_WIDTH"] if self._is_expanded else SETTINGS["EXPANDED_WIDTH"]
        AnimationController.animate_sidebar(self, self.width(), target_width)
        self._is_expanded = not self._is_expanded


    # ── Private Methods ─────────────────────────────────────────────────────────────
    def _create_nav_button(self, label: str, is_checkable: bool = True) -> NavButton:
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
        self.mainLayout.addWidget(button)

        if is_checkable:
            self.nav_button_group.addButton(button)

        print(icon_info)

        return button