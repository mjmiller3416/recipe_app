"""app/theme_manager/config.py

Configuration module for theme management in the application.
Defines color enums, theme modes, and paths to QSS files.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from enum import Enum

from app.config.paths.app_paths import AppPaths


class Color(Enum):
    INDIGO      = "#3F51B5"
    BLUE        = "#2196F3"
    TEAL        = "#009688"
    GREEN       = "#63A002"
    YELLOW      = "#FFDE3F"
    ORANGE      = "#FF9800"
    RED         = "#F44336"
    PINK        = "#E91E63"
    PURPLE      = "#9C27B0"
    DEEP_PURPLE = "#673AB7"
    BROWN       = "#795548"
    GRAY        = "#607D8B"

class Mode(Enum):
    LIGHT = "light"
    DARK = "dark"

class Qss(Enum):
    BASE = AppPaths.BASE_STYLE

    # TODO: Implement feature to load additional custom stylesheets in addition to base

    # Component Styles
    CARD = AppPaths.QSS_DIR / "card.qss"
    COMBOBOX = AppPaths.QSS_DIR / "combobox.qss"
    DIALOG_WINDOW = AppPaths.QSS_DIR / "dialog_window.qss"
    EMPTY_STATE = AppPaths.QSS_DIR / "empty_state.qss"
    INGREDIENT_WIDGET = AppPaths.QSS_DIR / "ingredient_widget.qss"
    RECIPE_CARD = AppPaths.QSS_DIR / "recipe_card.qss"
    RECIPE_DIALOG = AppPaths.QSS_DIR / "recipe_dialog.qss"
    SEARCH_BAR = AppPaths.QSS_DIR / "search_bar.qss"
    UPLOAD_IMAGE = AppPaths.QSS_DIR / "upload_image.qss"

    # View Styles
    ADD_RECIPE = AppPaths.QSS_DIR / "add_recipe.qss"
    DASHBOARD = AppPaths.QSS_DIR / "dashboard.qss"
    MAIN_WINDOW = AppPaths.QSS_DIR / "main_window.qss"
    MEAL_PLANNER = AppPaths.QSS_DIR / "meal_planner.qss"
    SHOPPING_LIST = AppPaths.QSS_DIR / "shopping_list.qss"
    VIEW_RECIPES = AppPaths.QSS_DIR / "view_recipes.qss"

