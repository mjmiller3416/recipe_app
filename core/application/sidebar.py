"""core/application/sidebar.py

Sidebar class for managing the sidebar of the application.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import QSizePolicy, QSpacerItem, QVBoxLayout, QWidget, QLabel

from config import SIDEBAR
from core.helpers.ui_helpers import create_fixed_wrapper
from ui.widgets import CTButton, CTIcon
from ui.components import AvatarLoader

# ── Constants ───────────────────────────────────────────────────────────────────
SETTINGS = SIDEBAR["SETTINGS"]
ICONS = SIDEBAR["ICONS"]

# ── Class Definition ────────────────────────────────────────────────────────────
class Sidebar(QWidget):
    """Sidebar widget for the application.

    Contains the application logo and a vertical stack of navigation buttons,
    including dashboard, meal planning, recipe viewing, shopping list,
    settings, and exit controls.

    Attributes:
        mainLayout: (QVBoxLayout): The main layout for the sidebar.
        logo (CTIcon): The application logo icon.
        btn_dashboard (CTButton): Button for navigating to the dashboard.
        btn_meal_planner (CTButton): Button for navigating to the meal planner.
        btn_view_recipes (CTButton): Button for navigating to view recipes.
        btn_shopping_list (CTButton): Button for navigating to the shopping list.
        btn_add_recipes (CTButton): Button for navigating to add recipes.
        btn_settings (CTButton): Button for accessing application settings.
        btn_exit (CTButton): Button for exiting the application.

    Signals:
        close_app: Emitted when the exit button is clicked.
    """

    # ── Signals ─────────────────────────────────────────────────────────────────────
    close_app = Signal()  # to signal a close event


    def __init__(self, parent=None):
        """Initializes the Sidebar.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)
        # ── Attributes ──
        self.setObjectName("Sidebar")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMinimumWidth(0)

        # ── Main Layout ──
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(0, 42, 0, 18) 
        self.mainLayout.setSpacing(1)

        # ── Logo ──
        self.avatar = AvatarLoader(size=QSize(240, 240))
        self.username = QLabel("@username")
        self.username.setObjectName("UsernameLabel")
        self.avatar_wrapper = create_fixed_wrapper(
            widgets = [self.avatar, self.username],
            fixed_width = 300,
            alignment = Qt.AlignHCenter,  # Centers in vertical stack
            direction = "vertical"
        )
        self.mainLayout.addWidget(self.avatar_wrapper)

        # top spacer
        self.mainLayout.addItem(QSpacerItem(212, 40, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # ── Navigation Buttons ──
        self.btn_dashboard = self._create_nav_button("Dashboard")
        self.btn_meal_planner = self._create_nav_button("Meal Planner")
        self.btn_view_recipes = self._create_nav_button("View Recipes")
        self.btn_shopping_list = self._create_nav_button("Shopping List")
        self.btn_add_recipes = self._create_nav_button("Add Recipes")

        # bottom spacer
        self.mainLayout.addItem(QSpacerItem(212, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # ── Settings & Exit Buttons ──
        self.btn_settings = self._create_nav_button("Settings", is_checkable=False)
        self.btn_exit = self._create_nav_button("Exit", is_checkable=False)

        # connect exit button to close_app signal
        self.btn_exit.clicked.connect(self.close_app.emit) # connect exit button to close_app signal

    @property
    def buttons(self):
        """Provides access to all sidebar buttons.

        Returns:
            dict[str, CTButton]: A dictionary mapping button names (e.g., "btn_dashboard")
                to their corresponding CTButton instances.
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
    
    def _create_nav_button(self, label: str, is_checkable: bool = True) -> CTButton:
        """Helper method to create a navigation button. 

        Must have a label that matches an entry in the ICONS config.

        Args:
            name (str): The name of the button (used for object naming).
            label (str): The text label for the button.

        Returns:
            CTButton: The created navigation button.
        """

        icon_info = ICONS[label.replace(" ", "_").upper()] # get icon info from config
        object_name = f"{label.replace(' ', '_')}Button" # e.g., "Dashboard" -> "DashboardButton"

        button = CTButton(
            file_path = icon_info["PATH"],
            icon_size = icon_info["SIZE"],
            variant   = icon_info["DYNAMIC"],
            label     = label,
            checkable = is_checkable,
        )
        button.setObjectName(object_name)
        button.setFixedHeight(82)
        self.mainLayout.addWidget(button)
        return button