"""
config package

Centralized configuration access for paths, constants, and user preferences.
"""

from .config import (DEBUG_LAYOUT_BORDERS, EMPTY_STATE, FLOAT, ICON_COLOR,
                     ICON_SIZE, INGREDIENT_CATEGORIES, INGREDIENT_WIDGET, INT,
                     MEAL_PLANNER, MEASUREMENT_UNITS, NAME, NON_EMPTY,
                     RECIPE_CARD, RECIPE_CATEGORIES, RECIPE_DIALOG, SEARCH,
                     SIDEBAR, TITLE_BAR)
from .paths import AppPaths, QssPaths
from .user_settings import UserSettings

__all__ = [
    "AppPaths", "QssPaths",
    "UserSettings",
    "ICON_SIZE", "INGREDIENT_CATEGORIES",
    "MEASUREMENT_UNITS", "RECIPE_CATEGORIES",
    "DEBUG_LAYOUT_BORDERS", "INT", "NAME",
    "FLOAT", "SEARCH", "NON_EMPTY", "TITLE_BAR",
    "INGREDIENT_WIDGET","MEAL_PLANNER", "RECIPE_WIDGET",
    "EMPTY_STATE", "RECIPE_CARD", "SIDEBAR", "RECIPE_DIALOG",
]
