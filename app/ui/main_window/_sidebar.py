"""app/ui/main_window/sidebar.py

Sidebar navigation component for the main window.
"""

# ── Imports ──
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QButtonGroup, QLabel, QSizePolicy, QSpacerItem, QVBoxLayout, QWidget

from _dev_tools import DebugLogger
from app.config import SIDEBAR
from app.style.animation import Animator
from app.style.icon.config import Name, Type
from app.ui.utils import create_fixed_wrapper
from app.ui.components.widgets.button import Button
from ._avatar_widget import AvatarWidget

# ── Constants ──
START = SIDEBAR["SETTINGS"]["EXPANDED_WIDTH"]
END = SIDEBAR["SETTINGS"]["COLLAPSED_WIDTH"]
DURATION = SIDEBAR["SETTINGS"]["DURATION"]


class Sidebar(QWidget):
    """A collapsible sidebar widget for navigation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMinimumWidth(0)
        self.setMaximumWidth(START)
        self._is_expanded = True

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        self._create_avatar()

        self.nav_button_group = QButtonGroup(self)
        self.nav_button_group.setExclusive(True)
        self.btn_dashboard = self._create_nav_button("Dashboard")
        self.btn_meal_planner = self._create_nav_button("Meal Planner")
        self.btn_browse_recipes = self._create_nav_button("Browse Recipes")
        self.btn_shopping_list = self._create_nav_button("Shopping List")
        self.btn_add_recipes = self._create_nav_button("Add Recipes")

        self.mainLayout.addItem(
            QSpacerItem(212, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

        self.btn_settings = self._create_nav_button("Settings", is_checkable=False)
        self.btn_exit = self._create_nav_button("Exit", is_checkable=False)

    @property
    def buttons(self) -> dict[str, Button]:
        return {
            "btn_dashboard": self.btn_dashboard,
            "btn_meal_planner": self.btn_meal_planner,
            "btn_browse_recipes": self.btn_browse_recipes,
            "btn_shopping_list": self.btn_shopping_list,
            "btn_add_recipes": self.btn_add_recipes,
            "btn_settings": self.btn_settings,
            "btn_exit": self.btn_exit,
        }

    @property
    def is_expanded(self) -> bool:
        return self._is_expanded

    def toggle(self):
        DebugLogger.log(
            f"Toggling sidebar: currently {'expanded' if self._is_expanded else 'collapsed'}"
        )

        start = self.maximumWidth()
        end = END if self._is_expanded else START
        duration = DURATION

        Animator.animate_width(self, start, end, duration)

        self._is_expanded = not self._is_expanded

    # ── Private Methods ──
    def _create_nav_button(self, label: str, is_checkable: bool = True) -> Button:
        """
        Create a navigation button using the Button class with NavButton-like styling.
        """
        # derive enum key from label (e.g. "Browse Recipes" -> "BROWSE_RECIPES")
        enum_key = label.replace(' ', '_').upper()
        app_icon = Name[enum_key]

        button = Button(
            label=label,
            type=Type.PRIMARY,
            icon=app_icon,
        )

        # button attributes
        button.setObjectName("NavButton")
        button.setCheckable(is_checkable)
        button.setContentsMargins(20,0,0,0)
        button.setFixedHeight(85)
        button.setIconSpacing(30)
        button.addLayoutStretch()

        self.mainLayout.addWidget(button)

        if is_checkable:
            self.nav_button_group.addButton(button)

        return button

    def _create_avatar(self) -> AvatarWidget:
        avatar = AvatarWidget(size=QSize(240, 240))

        # Get username from settings
        from app.core.services.settings_service import SettingsService
        settings_service = SettingsService()
        username_text = settings_service.get("user.username", "User")

        self.username_label = QLabel(f"@{username_text}")
        self.username_label.setObjectName("UsernameLabel")
        self.username_label.setAlignment(Qt.AlignCenter)
        avatar_wrapper = create_fixed_wrapper(
            widgets=[avatar, self.username_label],
            fixed_width=self.width(),
            alignment=Qt.AlignHCenter,
            direction="vertical",
            margins=(0, 40, 0, 30),
        )
        self.mainLayout.addWidget(avatar_wrapper)

    def update_username(self, username: str) -> None:
        """Update the displayed username."""
        if hasattr(self, 'username_label'):
            self.username_label.setText(f"@{username}")
