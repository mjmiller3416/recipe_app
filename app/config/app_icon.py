"""app/config/app_icon.py

Defines AppIcon enum and ICON_SPECS mapping for all application icons.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from enum import Enum, auto
from pathlib import Path
from typing import Dict

from PySide6.QtCore import QSize

from app.style_manager.icons.spec import IconSpec
from app.config.paths import AppPaths
from app.style_manager.themes.dark_theme import THEME


# ── AppIcon Enum Definition ──────────────────────────────────────────────────────────────────
class AppIcon(Enum):
    # Title Bar Icons
    LOGO = auto()
    MINIMIZE = auto()
    MAXIMIZE = auto()
    RESTORE = auto()
    CLOSE = auto()
    TOGGLE_SIDEBAR = auto()

    # Sidebar Icons
    DASHBOARD = auto()
    MEAL_PLANNER = auto()
    VIEW_RECIPES = auto()
    SHOPPING_LIST = auto()
    ADD_RECIPES = auto()
    SETTINGS = auto()
    EXIT = auto()

    # Add Recipe Page
    ADD_IMAGE = auto()

    # Meal Planner Page
    MEAL_PLANNER_ADD = auto()

    # Search
    SEARCH = auto()
    CLEAR = auto()

    # Upload Recipe Image
    UPLOAD_IMAGE = auto()

    # Ingredient Widget
    INGREDIENT_ADD = auto()
    INGREDIENT_SUBTRACT = auto()

    # Custom ComboBox
    COMBOBOX_ARROW = auto()

    # Empty State
    ADD_MEAL = auto()

    # Recipe Card
    TOTAL_TIME = auto()
    SERVINGS = auto()
    FAVORITE = auto()
    MEAL_TYPE = auto()
    DIET_PREF = auto()

    # Recipe Dialog
    DIALOG_SERVINGS = auto()
    DIALOG_TOTAL_TIME = auto()
    DIALOG_CATEGORY = auto()

    # Message Dialog
    MESSAGE_INFO = auto()
    MESSAGE_WARNING = auto()
    MESSAGE_ERROR = auto()
    MESSAGE_SUCCESS = auto()

# Mapping of AppIcon to IconSpec
ICON_SPECS: Dict[AppIcon, IconSpec] = {
    # Title Bar Icons
    AppIcon.LOGO: IconSpec(
        path=AppPaths.ICONS_DIR / "logo.svg",
        size=QSize(30, 30),
        variant=THEME["ICON"]["ACCENT"],
    ),
    AppIcon.MINIMIZE: IconSpec(
        path=AppPaths.ICONS_DIR / "minimize.svg",
        size=QSize(16, 16),
        variant=THEME["ICON_STYLES"]["TOOLBUTTON"],
    ),
    AppIcon.MAXIMIZE: IconSpec(
        path=AppPaths.ICONS_DIR / "maximize.svg",
        size=QSize(16, 16),
        variant=THEME["ICON_STYLES"]["TOOLBUTTON"],
    ),
    AppIcon.RESTORE: IconSpec(
        path=AppPaths.ICONS_DIR / "restore.svg",
        size=QSize(16, 16),
        variant=THEME["ICON_STYLES"]["TOOLBUTTON"],
    ),
    AppIcon.CLOSE: IconSpec(
        path=AppPaths.ICONS_DIR / "close.svg",
        size=QSize(16, 16),
        variant=THEME["ICON_STYLES"]["TITLEBAR"],
    ),
    AppIcon.TOGGLE_SIDEBAR: IconSpec(
        path=AppPaths.ICONS_DIR / "toggle_sidebar.svg",
        size=QSize(24, 24),
        variant=THEME["ICON_STYLES"]["TOOLBUTTON"],
    ),

    # Sidebar Icons
    AppIcon.DASHBOARD: IconSpec(
        path=AppPaths.ICONS_DIR / "dashboard.svg",
        size=QSize(36, 36),
        variant=THEME["ICON_STYLES"]["NAV"],
    ),
    AppIcon.MEAL_PLANNER: IconSpec(
        path=AppPaths.ICONS_DIR / "meal_planner.svg",
        size=QSize(36, 36),
        variant=THEME["ICON_STYLES"]["NAV"],
    ),
    AppIcon.VIEW_RECIPES: IconSpec(
        path=AppPaths.ICONS_DIR / "view_recipes.svg",
        size=QSize(36, 36),
        variant=THEME["ICON_STYLES"]["NAV"],
    ),
    AppIcon.SHOPPING_LIST: IconSpec(
        path=AppPaths.ICONS_DIR / "shopping_list.svg",
        size=QSize(36, 36),
        variant=THEME["ICON_STYLES"]["NAV"],
    ),
    AppIcon.ADD_RECIPES: IconSpec(
        path=AppPaths.ICONS_DIR / "add.svg",
        size=QSize(36, 36),
        variant=THEME["ICON_STYLES"]["NAV"],
    ),
    AppIcon.SETTINGS: IconSpec(
        path=AppPaths.ICONS_DIR / "settings.svg",
        size=QSize(36, 36),
        variant=THEME["ICON_STYLES"]["NAV"],
    ),
    AppIcon.EXIT: IconSpec(
        path=AppPaths.ICONS_DIR / "exit.svg",
        size=QSize(36, 36),
        variant=THEME["ICON_STYLES"]["NAV"],
    ),

    # Add Recipe Page
    AppIcon.ADD_IMAGE: IconSpec(
        path=AppPaths.ICONS_DIR / "add.svg",
        size=QSize(200, 200),
        variant=THEME["ICON_STYLES"]["TOOLBUTTON"],
    ),

    # Meal Planner Page
    AppIcon.MEAL_PLANNER_ADD: IconSpec(
        path=AppPaths.ICONS_DIR / "add.svg",
        size=QSize(16, 16),
        variant=THEME["ICON"]["ACCENT"],
    ),

    # Search
    AppIcon.SEARCH: IconSpec(
        path=AppPaths.ICONS_DIR / "search.svg",
        size=QSize(22, 22),
        variant=THEME["ICON"]["ACCENT"],
    ),
    AppIcon.CLEAR: IconSpec(
        path=AppPaths.ICONS_DIR / "clear.svg",
        size=QSize(24, 24),
        variant=THEME["ICON_STYLES"]["TOOLBUTTON"],
    ),

    # Upload Recipe Image
    AppIcon.UPLOAD_IMAGE: IconSpec(
        path=AppPaths.ICONS_DIR / "plus.svg",
        size=QSize(100, 100),
        variant=THEME["ICON_STYLES"]["TOOLBUTTON"],
        button_size=QSize(200, 200),
    ),

    # Ingredient Widget
    AppIcon.INGREDIENT_ADD: IconSpec(
        path=AppPaths.ICONS_DIR / "add.svg",
        size=QSize(20, 20),
        variant=THEME["ICON_STYLES"]["TOOLBUTTON"],
    ),
    AppIcon.INGREDIENT_SUBTRACT: IconSpec(
        path=AppPaths.ICONS_DIR / "subtract.svg",
        size=QSize(20, 20),
        variant=THEME["ICON_STYLES"]["TOOLBUTTON"],
    ),

    # Custom ComboBox
    AppIcon.COMBOBOX_ARROW: IconSpec(
        path=AppPaths.ICONS_DIR / "down_arrow.svg",
        size=QSize(24, 24),
        variant=THEME["ICON_STYLES"]["TOOLBUTTON"],
    ),

    # Empty State
    AppIcon.ADD_MEAL: IconSpec(
        path=AppPaths.ICONS_DIR / "add.svg",
        size=QSize(60, 60),
        variant=THEME["ICON"]["ACCENT"],
    ),

    # Recipe Card
    AppIcon.TOTAL_TIME: IconSpec(
        path=AppPaths.ICONS_DIR / "total_time.svg",
        size=QSize(30, 30),
        variant=THEME["ICON_STYLES"]["NAV"],
    ),
    AppIcon.SERVINGS: IconSpec(
        path=AppPaths.ICONS_DIR / "servings.svg",
        size=QSize(30, 30),
        variant=THEME["ICON"]["ACCENT"],
    ),
    AppIcon.FAVORITE: IconSpec(
        path=AppPaths.ICONS_DIR / "favorite.svg",
        size=QSize(30, 30),
        variant=THEME["ICON"]["ACCENT"],
    ),
    AppIcon.MEAL_TYPE: IconSpec(
        path=AppPaths.ICONS_DIR / "meal_type.svg",
        size=QSize(30, 30),
        variant=THEME["ICON"]["ACCENT"],
    ),
    AppIcon.DIET_PREF: IconSpec(
        path=AppPaths.ICONS_DIR / "diet_pref.svg",
        size=QSize(30, 30),
        variant=THEME["ICON"]["ACCENT"],
    ),

    # Recipe Dialog
    AppIcon.DIALOG_SERVINGS: IconSpec(
        path=AppPaths.ICONS_DIR / "servings.svg",
        size=QSize(30, 30),
        variant=THEME["ICON"]["ACCENT"],
    ),
    AppIcon.DIALOG_TOTAL_TIME: IconSpec(
        path=AppPaths.ICONS_DIR / "total_time.svg",
        size=QSize(30, 30),
        variant=THEME["ICON"]["ACCENT"],
    ),
    AppIcon.DIALOG_CATEGORY: IconSpec(
        path=AppPaths.ICONS_DIR / "category.svg",
        size=QSize(30, 30),
        variant=THEME["ICON"]["ACCENT"],
    ),

    # Message Dialog
    AppIcon.MESSAGE_INFO: IconSpec(
        path=AppPaths.ICONS_DIR / "info.svg",
        size=QSize(50, 50),
        variant=THEME["ICON"]["INFO"],
    ),
    AppIcon.MESSAGE_WARNING: IconSpec(
        path=AppPaths.ICONS_DIR / "warning.svg",
        size=QSize(50, 50),
        variant=THEME["ICON"]["WARNING"],
    ),
    AppIcon.MESSAGE_ERROR: IconSpec(
        path=AppPaths.ICONS_DIR / "error.svg",
        size=QSize(50, 50),
        variant=THEME["ICON"]["ERROR"],
    ),
    AppIcon.MESSAGE_SUCCESS: IconSpec(
        path=AppPaths.ICONS_DIR / "success.svg",
        size=QSize(50, 50),
        variant=THEME["ICON"]["SUCCESS"],
    ),
}
