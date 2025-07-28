
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

    # Widget-specific stylesheets
    TITLEBAR = AppPaths.QSS_DIR / "titlebar.qss"
    RECIPE_CARD = AppPaths.QSS_DIR / "recipe_card.qss"
    SEARCH_BAR = AppPaths.QSS_DIR / "search_bar.qss"
    COMBOBOX = AppPaths.QSS_DIR / "combobox.qss"
    CARD = AppPaths.QSS_DIR / "card.qss"
    MAIN_WINDOW = AppPaths.QSS_DIR / "main_window.qss"
    DASHBOARD = AppPaths.QSS_DIR / "dashboard.qss"
    MEAL_PLANNER = AppPaths.QSS_DIR / "meal_planner.qss"
    SHOPPING_LIST = AppPaths.QSS_DIR / "shopping_list.qss"
    VIEW_RECIPES = AppPaths.QSS_DIR / "view_recipes.qss"
    INGREDIENT_WIDGET = AppPaths.QSS_DIR / "ingredient_widget.qss"
    DIALOG_WINDOW = AppPaths.QSS_DIR / "dialog_window.qss"
    UPLOAD_IMAGE = AppPaths.QSS_DIR / "upload_image.qss"
