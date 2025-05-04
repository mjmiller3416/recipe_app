"""core/application/sidebar_widget.py

SidebarWidget class for managing the sidebar of the application.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (QLabel, QPushButton, QSizePolicy, QSpacerItem,
                               QVBoxLayout, QWidget,)

from config import AppPaths, ICON_SIZE
from core.controllers import ThemeController
from ui.iconkit import SVGLoader, ButtonIcon

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

        # ── Fetch Theme ──
        self.theme = ThemeController().get_current_palette()
        self.logo_color = self.theme["LOGO_COLOR"]
        self.icon_color = self.theme["ICON_COLOR"]

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
        self.lbl_logo = QLabel()
        self.lbl_logo.setObjectName("lbl_logo")
        self.lbl_logo.setFixedSize(180, 180)
        self.lbl_logo.setScaledContents(True)

        self.logo_layout.addWidget(self.lbl_logo)
        self.verticalLayout.addWidget(self.logo_container)
        self.logo_container.setFixedWidth(215)  # set fixed width for the logo container

        # top spacer
        self.verticalLayout.addItem(QSpacerItem(212, 40, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # ── Navigation Buttons ──
        self.btn_dashboard = self._create_nav_button(
            "dashboard.svg", 
            "Dashboard", 
            "btn_dashboard",
            checked=True
        )
        self.verticalLayout.addWidget(self.btn_dashboard)

        self.btn_meal_planner = self._create_nav_button( # Meal Planner button
            "meal_planner.svg",
            "Meal Plan",
            "btn_meal_planner",
            checked=False
        )
        self.verticalLayout.addWidget(self.btn_meal_planner)

        self.btn_view_recipes = self._create_nav_button( # View Recipes button
            "view_recipes.svg",
            "View Recipes",
            "btn_view_recipes",
            checked=False
        )
        self.verticalLayout.addWidget(self.btn_view_recipes)

        self.btn_shopping_list = self._create_nav_button( # Shopping List button
            "shopping_list.svg",
            "Shopping List",
            "btn_shopping_list",
            checked=False
        )
        self.verticalLayout.addWidget(self.btn_shopping_list)

        self.btn_add_recipes = self._create_nav_button( # Add Recipes button
            "add_recipes.svg",
            "Add Recipes",
            "btn_add_recipes",
            checked=False
        )
        self.verticalLayout.addWidget(self.btn_add_recipes)

        # bottom spacer
        self.verticalLayout.addItem(QSpacerItem(212, 39, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # ── Settings & Exist Buttons ──
        self.btn_settings = self._create_nav_button( # Settings button
            "settings.svg",
            "Settings",
            "btn_settings",
        )
        self.verticalLayout.addWidget(self.btn_settings)

        self.btn_exit = self._create_nav_button( # Exit button
            "exit.svg",
            "Exit",
            "btn_exit",
            checked=False
        )
        self.btn_exit.clicked.connect(self.close_app.emit) # connect exit button to close_app signal

        self.verticalLayout.addWidget(self.btn_exit)

    def apply_local_styles(self):
        """
        Applies Sidebar-specific styles like logo coloring, layout margins,
        and hover effects for navigation buttons.
        """

        # Update the logo color dynamically
        img_logo = SVGLoader.load(
            AppPaths.IMAGES_DIR("logo.svg"),
            self.logo_color,
            size=self.lbl_logo.size(),
            return_type=QPixmap,
            source_color="#000"
        )
        self.lbl_logo.setPixmap(img_logo)

        # Apply sidebar margins
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

    # ── Private Methods ─────────────────────────────────────────────────────────────
    def _create_nav_button(
            self, 
            file_name: str,
            size: QSize,
            variant: str = "default",
            label: str = "",
            object_name: str = "",
            checked: bool = False,
    ) -> ButtonIcon:
        return ButtonIcon(
            file_name=file_name,
            size=ICON_SIZE,
            variant=variant,
            label=label,
            object_name=object_name,
            checked=checked,
        )