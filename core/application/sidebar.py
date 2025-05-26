"""core/application/sidebar.py

Sidebar class for managing the sidebar of the application.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import QSizePolicy, QSpacerItem, QVBoxLayout, QWidget

from config import ICON_COLOR, ICON_SIZE, SIDEBAR
from ui.iconkit import ButtonIcon, Icon


# ── Class Definition ────────────────────────────────────────────────────────────
class Sidebar(QWidget):
    """
    Sidebar widget for the application.

    Contains the application logo and a vertical stack of navigation buttons,
    including dashboard, meal planning, recipe viewing, shopping list,
    settings, and exit controls.
    """

    # ── Signals ─────────────────────────────────────────────────────────────────────
    close_app = Signal()  # to signal a close event


    def __init__(self, parent=None):
        super().__init__(parent)
        # ── Attributes ──
        self.setObjectName("Sidebar")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMinimumWidth(0)

        # ── Main Layout ──
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 18, 0, 18) 
        self.verticalLayout.setSpacing(1)  # space between buttons

        # ── Logo Container ──
        self.logo_container = QWidget()
        self.logo_layout = QVBoxLayout(self.logo_container)
        self.logo_layout.setContentsMargins(18, 0, 18, 0)
        self.logo_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # ── Logo Label ──
        self.lbl_logo = Icon(
            file_path = SIDEBAR["LOGO"], 
            size      = SIDEBAR["LOGO_SIZE"],
            variant   = ICON_COLOR,
        )

        self.logo_layout.addWidget(self.lbl_logo)
        self.verticalLayout.addWidget(self.logo_container)
        self.logo_container.setFixedWidth(215)  # set fixed width for the logo container

        # top spacer
        self.verticalLayout.addItem(QSpacerItem(212, 40, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # ── Navigation Buttons ──
        self.btn_dashboard = ButtonIcon(
            file_path      = SIDEBAR["ICON_DASHBOARD"],
            size           = ICON_SIZE,
            label          = "Dashboard",
            variant        = SIDEBAR["DYNAMIC"],
        )
        self.btn_dashboard.setFixedHeight(55)  # set fixed height for the button
        self.verticalLayout.addWidget(self.btn_dashboard)

        self.btn_meal_planner = ButtonIcon( # Meal Planner button
            file_path         = SIDEBAR["ICON_MEAL_PLANNER"],
            size              = ICON_SIZE,
            label             = "Meal Planner",
            variant           = SIDEBAR["DYNAMIC"],
        )
        self.btn_meal_planner.setFixedHeight(55)  # set fixed height for the button
        self.verticalLayout.addWidget(self.btn_meal_planner)

        self.btn_view_recipes = ButtonIcon( # View Recipes button
            file_path         = SIDEBAR["ICON_VIEW_RECIPES"],
            size              = ICON_SIZE,
            label             = "View Recipes",
            variant           = SIDEBAR["DYNAMIC"],
        )
        self.btn_view_recipes.setFixedHeight(55)  # set fixed height for the button
        self.verticalLayout.addWidget(self.btn_view_recipes)

        self.btn_shopping_list = ButtonIcon( # Shopping List button
            file_path          = SIDEBAR["ICON_SHOPPING_LIST"],
            size               = ICON_SIZE,
            label              = "Shopping List",
            variant            = SIDEBAR["DYNAMIC"],
        )
        self.btn_shopping_list.setFixedHeight(55)  # set fixed height for the button
        self.verticalLayout.addWidget(self.btn_shopping_list)

        self.btn_add_recipes = ButtonIcon( # Add Recipes button
            file_path        = SIDEBAR["ICON_ADD_RECIPES"],
            size             = ICON_SIZE,
            label            = "Add Recipes",
            variant          = SIDEBAR["DYNAMIC"],
        )
        self.btn_add_recipes.setFixedHeight(55)  # set fixed height for the button
        self.verticalLayout.addWidget(self.btn_add_recipes)

        # bottom spacer
        self.verticalLayout.addItem(QSpacerItem(212, 39, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # ── Settings & Exit Buttons ──
        self.btn_settings = ButtonIcon( # Settings button
            file_path     = SIDEBAR["ICON_SETTINGS"],
            size          = ICON_SIZE,
            label         = "Settings",
            variant       = SIDEBAR["DYNAMIC"],
        )
        self.btn_settings.setFixedHeight(55)  # set fixed height for the button
        self.verticalLayout.addWidget(self.btn_settings)

        self.btn_exit = ButtonIcon( # Exit button
            file_path = SIDEBAR["ICON_EXIT"],
            size      = ICON_SIZE,
            label     = "Exit",
            variant   = SIDEBAR["DYNAMIC"],
        )
        self.btn_exit.setFixedHeight(55)  # set fixed height for the button
        self.btn_exit.clicked.connect(self.close_app.emit) # connect exit button to close_app signal
        self.verticalLayout.addWidget(self.btn_exit)

    @property
    def buttons(self):
        """
        Exposes all sidebar buttons in a dictionary.

        Returns:
            dict: A mapping of sidebar button names to their corresponding QPushButton objects.
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