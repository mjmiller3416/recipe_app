"""core/application/sidebar.py

Sidebar class for managing the sidebar of the application.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import QSizePolicy, QSpacerItem, QVBoxLayout, QWidget

from config import SIDEBAR
from ui.widgets import CTButton, CTIcon

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
        verticalLayout (QVBoxLayout): The main layout for the sidebar.
        logo_container (QWidget): Container for the application logo.
        logo_layout (QVBoxLayout): Layout for the logo container.
        lbl_logo (CTIcon): The application logo icon.
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
        self.mainLayout.setContentsMargins(0, 18, 0, 18) 
        self.mainLayout.setSpacing(1)

        # ── Logo ──
        self.logo = CTIcon(
            file_path = SETTINGS["LOGO"]["PATH"], 
            size      = SETTINGS["LOGO"]["SIZE"],
            variant   = SETTINGS["LOGO"]["STATIC"],
        )
        self.mainLayout.addWidget(self.logo, alignment=Qt.AlignCenter)

        # top spacer
        self.mainLayout.addItem(QSpacerItem(212, 40, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # ── Navigation Buttons ──
        self.btn_dashboard = CTButton(
            file_path      = ICONS["DASHBOARD"]["PATH"],
            icon_size      = ICONS["DASHBOARD"]["SIZE"],
            variant        = ICONS["DASHBOARD"]["DYNAMIC"],
            label          = "Dashboard",
        )
        self.mainLayout.addWidget(self.btn_dashboard)

        self.btn_meal_planner = CTButton( # Meal Planner button
            file_path         = ICONS["MEAL_PLANNER"]["PATH"],
            icon_size         = ICONS["MEAL_PLANNER"]["SIZE"],
            variant           = ICONS["MEAL_PLANNER"]["DYNAMIC"],
            label             = "Meal Planner",
        )
        self.mainLayout.addWidget(self.btn_meal_planner)

        self.btn_view_recipes = CTButton( # View Recipes button
            file_path         = ICONS["VIEW_RECIPES"]["PATH"],
            icon_size         = ICONS["VIEW_RECIPES"]["SIZE"],
            variant           = ICONS["VIEW_RECIPES"]["DYNAMIC"],
            label             = "View Recipes",
        )
        self.mainLayout.addWidget(self.btn_view_recipes)

        self.btn_shopping_list = CTButton( # Shopping List button
            file_path          = ICONS["SHOPPING_LIST"]["PATH"],
            icon_size          = ICONS["SHOPPING_LIST"]["SIZE"],
            variant            = ICONS["SHOPPING_LIST"]["DYNAMIC"],
            label              = "Shopping List",
        )
        self.mainLayout.addWidget(self.btn_shopping_list)

        self.btn_add_recipes = CTButton( # Add Recipes button
            file_path        = ICONS["ADD_RECIPES"]["PATH"],
            icon_size        = ICONS["ADD_RECIPES"]["SIZE"],
            variant          = ICONS["ADD_RECIPES"]["DYNAMIC"],
            label            = "Add Recipes",
        )
        self.mainLayout.addWidget(self.btn_add_recipes)

        # bottom spacer
        self.mainLayout.addItem(QSpacerItem(212, 39, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # ── Settings & Exit Buttons ──
        self.btn_settings = CTButton( # Settings button
            file_path     = ICONS["SETTINGS"]["PATH"],
            icon_size     = ICONS["SETTINGS"]["SIZE"],
            variant       = ICONS["SETTINGS"]["DYNAMIC"],
            label         = "Settings",
        )
        self.mainLayout.addWidget(self.btn_settings)

        self.btn_exit = CTButton( # Exit button
            file_path = ICONS["EXIT"]["PATH"],
            icon_size = ICONS["EXIT"]["SIZE"],
            variant   = ICONS["EXIT"]["DYNAMIC"],
            label     = "Exit",
        )
        self.btn_exit.setObjectName("ExitButton")
        self.btn_exit.clicked.connect(self.close_app.emit) # connect exit button to close_app signal
        self.mainLayout.addWidget(self.btn_exit)

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