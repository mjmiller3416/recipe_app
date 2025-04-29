"""
Defines the SidebarWidget class, which contains the application’s main
navigation buttons and logo, styled in a vertical layout.

Classes:
    SidebarWidget

Functions:
    _create_nav_button
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
# 🔸 Third-Part Imports
from PySide6.QtWidgets import (QLabel, QPushButton, QSizePolicy, QSpacerItem,
                               QVBoxLayout, QWidget)

# 🔸 Local Application Imports
from core.application.config import (ICON_COLOR, ICON_SIZE, LOGO_COLOR,
                                     icon_path, image_path)
from core.helpers.ui_helpers import get_all_buttons, svg_loader
from core.managers.style_manager import StyleManager


class SidebarWidget(QWidget):
    """
    Sidebar widget for the application.

    Contains the application logo and a vertical stack of navigation buttons,
    including dashboard, meal planning, recipe viewing, shopping list,
    settings, and exit controls.
    """

    # 🔹 Signals
    close_app = Signal()  # To signal a close event


    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("SidebarWidget")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMinimumWidth(0)

        # 🔹 Main vertical layout
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(10)  # Space between buttons

        # 🔹 Logo Container
        self.logo_container = QWidget()
        self.logo_layout = QVBoxLayout(self.logo_container)
        self.logo_layout.setContentsMargins(0, 0, 0, 0)
        self.logo_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # 🔹 Logo Label
        self.lbl_logo = QLabel()
        self.lbl_logo.setObjectName("lbl_logo")
        self.lbl_logo.setFixedSize(180, 180)
        self.lbl_logo.setScaledContents(True)

        self.logo_layout.addWidget(self.lbl_logo)
        self.verticalLayout.addWidget(self.logo_container)
        self.logo_container.setFixedWidth(215)  # Set fixed width for the logo container

        # 🔹 Top Spacer
        self.verticalLayout.addItem(QSpacerItem(212, 40, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # 🔹 Navigation Buttons
        self.btn_dashboard = self._create_nav_button( # Dashboard button
            "btn_dashboard",
            "Dashboard",
            self.get_sidebar_icon("dashboard"),
            checked=True
        )
        self.verticalLayout.addWidget(self.btn_dashboard)

        self.btn_meal_planner = self._create_nav_button( # Meal Planner button
            "btn_meal_planner",
            "Meal Plan",
            self.get_sidebar_icon("meal_planner")
        )
        self.verticalLayout.addWidget(self.btn_meal_planner)

        self.btn_view_recipes = self._create_nav_button( # View Recipes button
            "btn_view_recipes",
            "View Recipes",
            self.get_sidebar_icon("view_recipes")
        )
        self.verticalLayout.addWidget(self.btn_view_recipes)

        self.btn_shopping_list = self._create_nav_button( # Shopping List button
            "btn_shopping_list",
            "Shopping List",
            self.get_sidebar_icon("shopping_list")
        )
        self.verticalLayout.addWidget(self.btn_shopping_list)

        self.btn_add_recipes = self._create_nav_button( # Add Recipes button
            "btn_add_recipes",
            "Add Recipes",
            self.get_sidebar_icon("add_recipes")
        )
        self.verticalLayout.addWidget(self.btn_add_recipes)

        # 🔹 Expanding Spacer
        self.verticalLayout.addItem(QSpacerItem(212, 39, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # 🔹 Settings & Exit Buttons
        self.btn_settings = self._create_nav_button( # Settings button
            "btn_settings",
            "Settings",
            self.get_sidebar_icon("settings")
        )
        self.verticalLayout.addWidget(self.btn_settings)

        self.btn_exit = self._create_nav_button( # Exit button
            "btn_exit",
            "Exit",
            self.get_sidebar_icon("exit")
        )
        self.btn_exit.clicked.connect(self.close_app.emit) # Connect exit button to close_app signal

        self.verticalLayout.addWidget(self.btn_exit)

        # 🔹 Apply local sidebar-specific styles
        self._apply_local_styles()

    def get_sidebar_icon(self, name: str) -> QIcon:
        return svg_loader(icon_path(name), ICON_COLOR, size=ICON_SIZE, return_type=QIcon, source_color="#000")

    def _create_nav_button(self, name, label, icon: QIcon = None, checked=False):
        """Helper to create navigation buttons.

        Args:
            object_name (str): The object name for the button.
            text (str): The display text for the button.
            icon_path (str): The path to the icon file.
            checked (bool): Whether the button should be initially checked.

        Returns:
            QPushButton: The created navigation button.
        """
        button = QPushButton(label)
        button.setObjectName(name)
        button.setCheckable(True)
        button.setChecked(checked)
        if icon:
            button.setIcon(icon)
            button.setIconSize(ICON_SIZE)
        return button

    def _apply_local_styles(self):
        """
        Applies Sidebar-specific styles like logo coloring, layout margins,
        and hover effects for navigation buttons.
        """

        # Update the logo color dynamically
        img_logo = svg_loader(
            image_path("logo"),
            LOGO_COLOR,
            size=self.lbl_logo.size(),
            return_type=QPixmap,
            source_color="#000"
        )
        self.lbl_logo.setPixmap(img_logo)

        # Apply sidebar margins
        self.verticalLayout.setContentsMargins(0, 18, 0, 18)

        # Apply hover effects to all buttons
        StyleManager.apply_hover_effects(get_all_buttons(self), (24, 24))

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
