"""app/ui/components/navigation/sidebar.py

Sidebar navigation component for the main window.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from _dev_tools import DebugLogger
from app.config import SIDEBAR
from app.style import Theme
from app.style.animation import Animator
from app.style.icon.config import Name, Type
from app.style.theme.config import Qss
from app.ui.components.images import AvatarLoader
from app.ui.utils.layout_utils import create_fixed_wrapper
from ..widgets.button import Button

# ── Constants ────────────────────────────────────────────────────────────────────────────────
START = SIDEBAR["SETTINGS"]["EXPANDED_WIDTH"]
END = SIDEBAR["SETTINGS"]["COLLAPSED_WIDTH"]
DURATION = SIDEBAR["SETTINGS"]["DURATION"]


# ── Sidebar ──────────────────────────────────────────────────────────────────────────────────
class Sidebar(QWidget):
    """A collapsible sidebar widget for navigation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMinimumWidth(0)
        self.setMaximumWidth(START)
        self._is_expanded = True

        # register for component-specific styling
        Theme.register_widget(self, Qss.SIDEBAR)

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        self._create_avatar()

        self.nav_button_group = QButtonGroup(self)
        self.nav_button_group.setExclusive(True)
        self.btn_dashboard = self._create_nav_button("Dashboard")
        self.btn_meal_planner = self._create_nav_button("Meal Planner")
        self.btn_view_recipes = self._create_nav_button("View Recipes")
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
            "btn_view_recipes": self.btn_view_recipes,
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
        # derive enum key from label (e.g. "View Recipes" -> "VIEW_RECIPES")
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

    def _create_avatar(self) -> AvatarLoader:
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
