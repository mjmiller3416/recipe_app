"""core/application/sidebar_widget.py

SidebarWidget class for managing the sidebar of the application.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (QLabel, QPushButton, QSizePolicy, QSpacerItem,
                               QVBoxLayout, QWidget)

from config import ICON_SIZE, AppPaths
from core.controllers import ThemeController
from ui.iconkit import ButtonIcon, Icon


# ── Class Definition ────────────────────────────────────────────────────────────
class SidebarWidget(QWidget):
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
        self.setObjectName("SidebarWidget")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMinimumWidth(0)

        # ── Main Layout ──
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(10)  # space between buttons

        # ── Logo Container ──
        self.logo_container = QWidget()
        self.logo_layout = QVBoxLayout(self.logo_container)
        self.logo_layout.setContentsMargins(0, 0, 0, 0)
        self.logo_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # ── Logo Label ──
        self.lbl_logo = Icon(file_name="logo.svg", size=QSize(215, 215))

        self.logo_layout.addWidget(self.lbl_logo)
        self.verticalLayout.addWidget(self.logo_container)
        self.logo_container.setFixedWidth(215)  # set fixed width for the logo container

        # top spacer
        self.verticalLayout.addItem(QSpacerItem(212, 40, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # ── Navigation Buttons ──
        self.btn_dashboard = ButtonIcon(
            file_name     = "dashboard.svg",
            size          = ICON_SIZE,
            label         = "Dashboard",
            object_name   = "btn_dashboard",
            hover_effects = True,
            checked       = True
        )
        self.verticalLayout.addWidget(self.btn_dashboard)

        self.btn_meal_planner = ButtonIcon( # Meal Planner button
            file_name     = "meal_planner.svg",
            size          = ICON_SIZE,
            label         = "Meal Planner",
            object_name   = "btn_meal_planner",
            hover_effects = True,
            checked       = False
        )
        self.verticalLayout.addWidget(self.btn_meal_planner)

        self.btn_view_recipes = ButtonIcon( # View Recipes button
            file_name     = "view_recipes.svg",
            size          = ICON_SIZE,
            label         = "View Recipes",
            object_name   = "btn_view_recipes",
            hover_effects = True,
            checked       = False
        )
        self.verticalLayout.addWidget(self.btn_view_recipes)

        self.btn_shopping_list = ButtonIcon( # Shopping List button
            file_name     = "shopping_list.svg",
            size          = ICON_SIZE,
            label         = "Shopping List",
            object_name   = "btn_shopping_list",
            hover_effects = True,
            checked       = False
        )
        self.verticalLayout.addWidget(self.btn_shopping_list)

        self.btn_add_recipes = ButtonIcon( # Add Recipes button
            file_name     = "add_recipes.svg",
            size          = ICON_SIZE,
            label         = "Add Recipes",
            object_name   = "btn_add_recipes",
            hover_effects = True,
            checked       = False
        )
        self.verticalLayout.addWidget(self.btn_add_recipes)

        # bottom spacer
        self.verticalLayout.addItem(QSpacerItem(212, 39, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # ── Settings & Exist Buttons ──
        self.btn_settings = ButtonIcon( # Settings button
            file_name     = "settings.svg",
            size          = ICON_SIZE,
            label         = "Settings",
            object_name   = "btn_settings",
            hover_effects = True,
            checked       = False
        )
        self.verticalLayout.addWidget(self.btn_settings)

        self.btn_exit = ButtonIcon( # Exit button
            file_name     = "exit.svg",
            size          = ICON_SIZE,
            label         = "Exit",
            object_name   = "btn_exit",
            hover_effects = True,
            checked       = False
        )
        self.btn_exit.clicked.connect(self.close_app.emit) # connect exit button to close_app signal
        self.verticalLayout.addWidget(self.btn_exit)
        self.verticalLayout.setContentsMargins(0, 18, 0, 18)


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