"""
Defines the SidebarWidget class, which contains the application’s main
navigation buttons and logo, styled in a vertical layout.

Classes:
    SidebarWidget

Functions:
    _create_nav_button
"""

from qt_imports import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QSizePolicy, QSpacerItem, 
    QSize, Qt, QIcon, QPixmap)

# 🔹 Local Imports
from style_manager import StyleManager

class SidebarWidget(QWidget):
    """
    Sidebar widget for the application.

    Contains the application logo and a vertical stack of navigation buttons,
    including dashboard, meal planning, recipe viewing, shopping list,
    settings, and exit controls.
    """
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
        self.lbl_logo.setPixmap(QPixmap(":/logo/logo.svg"))
        self.lbl_logo.setScaledContents(True)

        self.logo_layout.addWidget(self.lbl_logo)
        self.verticalLayout.addWidget(self.logo_container)
        self.logo_container.setFixedWidth(215)  # Set fixed width for the logo container

        # 🔹 Top Spacer
        self.verticalLayout.addItem(QSpacerItem(212, 40, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # 🔹 Navigation Buttons
        self.btn_dashboard = self._create_nav_button("btn_dashboard", "Dashboard", ":/icons/dashboard.svg", checked=True)
        self.btn_meal_planner = self._create_nav_button("btn_meal_planner", "Meal Plan", ":/icons/meal_planner.svg")
        self.btn_view_recipes = self._create_nav_button("btn_view_recipes", "View Recipes", ":/icons/view_recipes.svg")
        self.btn_shopping_list = self._create_nav_button("btn_shopping_list", "Shopping List", ":/icons/shopping_list.svg")
        self.btn_add_recipes = self._create_nav_button("btn_add_recipes", "Add Recipes", ":/icons/add_recipes.svg")

        # 🔹 Expanding Spacer
        self.verticalLayout.addItem(QSpacerItem(212, 39, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # 🔹 Settings & Exit Buttons
        self.btn_settings = self._create_nav_button("btn_settings", "Settings", ":/icons/settings.svg")
        self.btn_exit = self._create_nav_button("btn_exit", "Exit", ":/icons/exit.svg")

        # 🔹 Apply styles (hover effects, margins, etc.)
        self.style_manager = StyleManager(self)

    def _create_nav_button(self, object_name, text, icon_path, checked=False):
        """Helper to create navigation buttons.
        
        Args:
            object_name (str): The object name for the button.
            text (str): The display text for the button.
            icon_path (str): The path to the icon file.
            checked (bool): Whether the button should be initially checked.

        Returns:
            QPushButton: The created navigation button.
        """
        btn = QPushButton(text)
        btn.setObjectName(object_name)
        btn.setMinimumSize(215, 50)
        btn.setMaximumSize(215, 50)
        btn.setIcon(QIcon(icon_path))
        btn.setIconSize(QSize(24, 24))
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        btn.setChecked(checked)
        self.verticalLayout.addWidget(btn)
        return btn

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
