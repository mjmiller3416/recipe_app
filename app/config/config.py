""""app/config/config.py

    This module contains configuration settings for the application.
"""
import re
# ── Imports ─────────────────────────────────────────────────────────────────────
from pathlib import Path

from PySide6.QtCore import QRegularExpression, QSize
from PySide6.QtGui import QRegularExpressionValidator

from app.config.paths import AppPaths, QssPaths
from app.style_manager.themes.dark_theme import THEME

# ── Icon Defaults ──
ICON_SIZE  = QSize(20, 20)
ICON_COLOR = THEME["ICON"]["DEFAULT"]

# ── Application Window ──
APPLICATION_WINDOW = {
    "SETTINGS": {
        "APP_NAME": "MealGenie",
        "WINDOW_HEIGHT": 1080,
        "WINDOW_WIDTH":  1800,
        "BTN_SIZE": QSize(58, 58),
        "BTN_STYLE": {
            "DYNAMIC": THEME["ICON_STYLES"]["TOOLBUTTON"],
        }
    },

    "ICONS": {
        "LOGO": {
            "PATH":    AppPaths.ICONS_DIR / "logo.svg",
            "SIZE":    QSize(30, 30),
            "STATIC":  THEME["ICON"]["ACCENT"],
        },
        "MINIMIZE": {
            "PATH":   AppPaths.ICONS_DIR / "minimize.svg",
            "SIZE":    QSize(16, 16),
            "DYNAMIC": THEME["ICON_STYLES"]["TOOLBUTTON"],
        },
        "MAXIMIZE": {
            "PATH":    AppPaths.ICONS_DIR / "maximize.svg",
            "SIZE":    QSize(16, 16),
            "DYNAMIC": THEME["ICON_STYLES"]["TOOLBUTTON"],
        },
        "RESTORE":  {
            "PATH":    AppPaths.ICONS_DIR / "restore.svg",
            "SIZE":    QSize(16, 16),
            "DYNAMIC": THEME["ICON_STYLES"]["TOOLBUTTON"],
        },
        "CLOSE": {
            "PATH":    AppPaths.ICONS_DIR / "close.svg",
            "SIZE":    QSize(16, 16),
            "DYNAMIC": THEME["ICON_STYLES"]["TITLEBAR"],
        },
        "TOGGLE_SIDEBAR": {
            "PATH":    AppPaths.ICONS_DIR / "toggle_sidebar.svg",
            "SIZE":    QSize(24, 24),
            "DYNAMIC": THEME["ICON_STYLES"]["TOOLBUTTON"],
            },
    }
}

# ── Sidebar Widget ──
SIDEBAR = {
    "SETTINGS": {
        "EXPANDED_WIDTH": 360,
        "COLLAPSED_WIDTH": 0,
        "DURATION": 800,  # animation duration in milliseconds
    },

    "ICONS": {
        "DASHBOARD": {
            "PATH": AppPaths.ICONS_DIR / "dashboard.svg",
            "SIZE": QSize(36, 36),
            "DYNAMIC": THEME["ICON_STYLES"]["NAV"]
        },
        "MEAL_PLANNER": {
            "PATH": AppPaths.ICONS_DIR / "meal_planner.svg",
            "SIZE": QSize(36, 36),
            "DYNAMIC": THEME["ICON_STYLES"]["NAV"]
        },
        "VIEW_RECIPES":{
            "PATH": AppPaths.ICONS_DIR / "view_recipes.svg",
            "SIZE": QSize(36, 36),
            "DYNAMIC": THEME["ICON_STYLES"]["NAV"]
        },
        "SHOPPING_LIST":{
            "PATH": AppPaths.ICONS_DIR / "shopping_list.svg",
            "SIZE": QSize(36, 36),
            "DYNAMIC": THEME["ICON_STYLES"]["NAV"]
        },
        "ADD_RECIPES": {
            "PATH": AppPaths.ICONS_DIR / "add_recipes.svg",
            "SIZE": QSize(36, 36),
            "DYNAMIC": THEME["ICON_STYLES"]["NAV"]
        },
        "SETTINGS": {
            "PATH": AppPaths.ICONS_DIR / "settings.svg",
            "SIZE": QSize(36, 36),
            "DYNAMIC": THEME["ICON_STYLES"]["NAV"]
        },
        "EXIT": {
            "PATH": AppPaths.ICONS_DIR / "exit.svg",
            "SIZE": QSize(36, 36),
            "DYNAMIC": THEME["ICON_STYLES"]["NAV"]
        },
    },
}

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
    "STATIC":   THEME["ICON"]["ACCENT"],
}



# ── Search Widget ──
SEARCH = {
    "ICONS": {
        "SEARCH": {
            "PATH":    AppPaths.ICONS_DIR / "search.svg",
            "SIZE":    QSize(22, 22),
            "STATIC":  THEME["ICON"]["ACCENT"],
        },
        "CLEAR":  {
            "PATH":    AppPaths.ICONS_DIR / "clear.svg",
            "SIZE":    QSize(24, 24),
            "DYNAMIC": THEME["ICON_STYLES"]["TOOLBUTTON"]
        }
    },
}

# ── Upload Image ──
UPLOAD_RECIPE_IMAGE = {
    "ICON_UPLOAD": {
        "FILE_PATH": AppPaths.ICONS_DIR / "plus.svg",
        "ICON_SIZE": QSize(100, 100),
        "BUTTON_SIZE": QSize(200, 200),
        "DYNAMIC":   THEME["ICON_STYLES"]["TOOLBUTTON"],
    },
}

# ── Ingredient Widget ──
INGREDIENT_WIDGET = {
    "ICON_SIZE":     QSize(20, 20),
    "ICON_ADD":      AppPaths.ICONS_DIR / "add.svg",
    "ICON_SUBTRACT": AppPaths.ICONS_DIR / "subtract.svg",
    "DYNAMIC":       THEME["ICON_STYLES"]["TOOLBUTTON"],
}

# ── Smart ComboBox ──
CUSTOM_COMBOBOX = {
    "ICONS": {
        "ARROW":  {
            "PATH":    AppPaths.ICONS_DIR / "down_arrow.svg",
            "SIZE":    QSize(24, 24),
            "DYNAMIC": THEME["ICON_STYLES"]["TOOLBUTTON"]
        },
    },
}

# ── Recipe Widget ──
EMPTY_STATE = {
    "ICON_SIZE":     QSize(60, 60),
    "ICON_ADD_MEAL": AppPaths.ICONS_DIR / "add_meal.svg",
    "STATIC":       THEME["ICON"]["ACCENT"],
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
    "STATIC":         THEME["ICON"]["ACCENT"],
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

# ── Widget Styles ──
STYLES = {
    "WIDGET_FRAME": QssPaths.Components.WIDGET_FRAME,
    "INGREDIENT_WIDGET": QssPaths.Components.INGREDIENT_WIDGET,
    "UPLOAD_IMAGE": QssPaths.Components.UPLOAD_IMAGE,
    "DIALOG_WINDOW": QssPaths.Components.DIALOG_WINDOW,
}

# ── General ──
MEASUREMENT_UNITS = [
    "bag", "box", "can", "cap-full", "cup", "gallon", "half", "jar",
    "oz.", "pack", "pinch", "pint", "lb.", "liter", "quarter", "slice",
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
NAME_PATTERN = re.compile(r"^[a-zA-Z0-9\s\-]+$")
FLOAT_PATTERN = re.compile(r"^\d{1,2}(\.\d{0,2})?$")
INT_PATTERN = re.compile(r"^\d{1,3}$")
NON_EMPTY_PATTERN = re.compile(r"^(?!\s*$).+")

# ── Validators ──
NAME_VALIDATOR = lambda parent: QRegularExpressionValidator(QRegularExpression(NAME_PATTERN.pattern), parent)
FLOAT_VALIDATOR = lambda parent: QRegularExpressionValidator(QRegularExpression(FLOAT_PATTERN.pattern), parent)
INT_VALIDATOR = lambda parent: QRegularExpressionValidator(QRegularExpression(INT_PATTERN.pattern), parent)
NON_EMPTY_VALIDATOR = lambda parent: QRegularExpressionValidator(QRegularExpression(NON_EMPTY_PATTERN.pattern), parent)

# ── Debug Flags ──
DEBUG_LAYOUT_BORDERS = True # set to True to draw layout borders
