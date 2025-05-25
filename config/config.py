""""config/config.py

    This module contains configuration settings for the application.
"""
# ── Imports ─────────────────────────────────────────────────────────────────────
from pathlib import Path

from PySide6.QtCore import QRegularExpression, QSize
from PySide6.QtGui import QRegularExpressionValidator

from config.paths import AppPaths
from style_manager.themes.dark_theme import THEME

# ── Icon Defaults ──
ICON_SIZE  = QSize(20, 20)
ICON_COLOR = THEME["ICON"]["DEFAULT"]

# ── Add Recipes ──
ADD_RECIPES = {
    "ADD_IMAGE": {
        "FILE_PATH": AppPaths.ICONS_DIR / "add.svg",
        "ICON_SIZE": QSize(200, 200),
        "DYNAMIC":   THEME["ICON_STYLES"]["TOOLBUTTON"],
    },
}

# ── Meal Planner ──
MEAL_PLANNER = {
    "ICON_SIZE": QSize(16, 16),
    "ICON_ADD":  AppPaths.ICONS_DIR / "add.svg",
    "VARIANT":   THEME["ICON"]["ACCENT"],
}

# ── Sidebar Widget ──
SIDEBAR = {
    "LOGO_SIZE": QSize(180, 180),
    "ICON_DASHBOARD":     AppPaths.ICONS_DIR / "dashboard.svg",
    "ICON_MEAL_PLANNER":  AppPaths.ICONS_DIR / "meal_planner.svg",
    "ICON_VIEW_RECIPES":  AppPaths.ICONS_DIR / "view_recipes.svg",
    "ICON_SHOPPING_LIST": AppPaths.ICONS_DIR / "shopping_list.svg",
    "ICON_ADD_RECIPES":   AppPaths.ICONS_DIR / "add_recipes.svg",
    "ICON_SETTINGS":      AppPaths.ICONS_DIR / "settings.svg",
    "ICON_EXIT":          AppPaths.ICONS_DIR / "exit.svg",
    "LOGO":               AppPaths.ICONS_DIR / "logo.svg",
    "VARIANT":            THEME["ICON_STYLES"]["NAV"]
}

# ── Search Widget ──
SEARCH = {
    "ICON_SEARCH": {
        "FILE_PATH": AppPaths.ICONS_DIR / "search.svg",
        "ICON_SIZE": QSize(16, 16),
        "STATIC":    THEME["ICON"]["ACCENT"],
    },
    "ICON_CLEAR":  {
        "FILE_PATH": AppPaths.ICONS_DIR / "clear.svg",
        "ICON_SIZE": QSize(20, 20),
        "DYNAMIC":   THEME["ICON_STYLES"]["TOOLBUTTON"]
    }
}

# ── Title Bar ──
TITLE_BAR = {
    "ICON_SIZE":           QSize(12, 12),
    "BUTTON_SIZE":         QSize(38, 38),
    "ICON_MINIMIZE":       AppPaths.ICONS_DIR / "minimize.svg",
    "ICON_MAXIMIZE":       AppPaths.ICONS_DIR / "maximize.svg",
    "ICON_RESTORE":        AppPaths.ICONS_DIR / "restore.svg",
    "ICON_CLOSE":          AppPaths.ICONS_DIR / "close.svg",
    "ICON_TOGGLE_SIDEBAR": AppPaths.ICONS_DIR / "toggle_sidebar.svg",
    "VARIANT":             THEME["ICON_STYLES"]["TOOLBUTTON"],
    "APP_NAME":            "MealGenie",
}

# ── Ingredient Widget ──
INGREDIENT_WIDGET = {
    "ICON_SIZE":     QSize(20, 20),
    "ICON_ADD":      AppPaths.ICONS_DIR / "add.svg",
    "ICON_SUBTRACT": AppPaths.ICONS_DIR / "subtract.svg",
    "DYNAMIC":       THEME["ICON_STYLES"]["TOOLBUTTON"],
}

# ── Smart ComboBox ──
SMART_COMBOBOX = {
    "ICON_ARROW":  {
        "FILE_PATH": AppPaths.ICONS_DIR / "down_arrow.svg",
        "ICON_SIZE": QSize(16, 16),
        "DYNAMIC":   THEME["ICON_STYLES"]["TOOLBUTTON"]
    },
    "ICON_CLEAR":  {
        "FILE_PATH": AppPaths.ICONS_DIR / "clear.svg",
        "ICON_SIZE": QSize(20, 20),
        "DYNAMIC":   THEME["ICON_STYLES"]["TOOLBUTTON"]
    },
}

# ── Recipe Widget ──
EMPTY_STATE = {
    "ICON_SIZE":     QSize(60, 60),
    "ICON_ADD_MEAL": AppPaths.ICONS_DIR / "add_meal.svg",
    "VARIANT":       THEME["ICON"]["ACCENT"],
}
RECIPE_CARD = {
    "ICON_SIZE":       QSize(30, 30),
    "ICON_TOTAL_TIME": AppPaths.ICONS_DIR / "total_time.svg",
    "ICON_SERVINGS":   AppPaths.ICONS_DIR / "servings.svg",
    "ICON_FAVORITE":   AppPaths.ICONS_DIR / "favorite.svg",
    "STATIC":         THEME["ICON"]["ACCENT"],
    "DYNAMIC":        THEME["ICON_STYLES"]["NAV"],
}
RECIPE_DIALOG = {
    "ICON_SIZE":       QSize(30, 30),
    "ICON_SERVINGS":   AppPaths.ICONS_DIR / "servings.svg",
    "ICON_TOTAL_TIME": AppPaths.ICONS_DIR / "total_time.svg",
    "ICON_CATEGORY":   AppPaths.ICONS_DIR / "category.svg",
    "VARIANT":         THEME["ICON"]["ACCENT"],
}

MESSAGE_DIALOG = {
    "ICON_SIZE": QSize(50, 50),
    "ICON_INFO": {
        "ICON_PATH":  AppPaths.ICONS_DIR / "info.svg",
        "ICON_COLOR": THEME["ICON"]["INFO"],
    },
    "ICON_WARNING": {
        "ICON_PATH":  AppPaths.ICONS_DIR / "warning.svg",
        "ICON_COLOR": THEME["ICON"]["WARNING"],
    },
    "ICON_ERROR": {
        "ICON_PATH":  AppPaths.ICONS_DIR / "error.svg",
        "ICON_COLOR": THEME["ICON"]["ERROR"],
    },
    "ICON_SUCCESS": {
        "ICON_PATH":  AppPaths.ICONS_DIR / "success.svg",
        "ICON_COLOR": THEME["ICON"]["SUCCESS"],
    },
}

# ── General ──
MEASUREMENT_UNITS = [
    "bag", "box", "can", "cap-full", "cup", "gallon", "half", "jar",
    "oz.", "pack", "pinch", "pint", "lb.", "quarter", "slice",
    "square", "strip", "Tbs", "tsp", "whole",
]

INGREDIENT_CATEGORIES = [
    "produce", "meat", "seafood", "pantry", "dairy", "deli", "frozen",
    "bakery", "baking", "condiments", "spices", "other",
]

MEAL_CATEGORIES = [
    "All", "Breakfast", "Lunch", "Dinner", "Snack", "Dessert",
]

RECIPE_CATEGORIES = [
    "All", "Ground Beef", "Chicken", "Seafood", "Veggie",
]

SORT_OPTIONS = [
    "A-Z", "Z-A"
]

# ── Validation Rules ──
NAME = lambda parent:      QRegularExpressionValidator(QRegularExpression(r"^[a-zA-Z0-9\s\-]+$"), parent)
FLOAT = lambda parent:     QRegularExpressionValidator(QRegularExpression(r"^\d{1,2}(\.\d{0,2})?$"), parent)
INT = lambda parent:       QRegularExpressionValidator(QRegularExpression(r"^\d{1,3}$"), parent)
NON_EMPTY = lambda parent: QRegularExpressionValidator(QRegularExpression(r"^(?!\s*$).+"), parent)

# ── Debug Flags ──
DEBUG_LAYOUT_BORDERS = True # set to True to draw layout borders
