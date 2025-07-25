"""
config package

Centralized configuration access for paths, constants, and user preferences.
"""

from .config import (APPLICATION_WINDOW, DEBUG_LAYOUT_BORDERS, FLOAT_PATTERN,
                     FLOAT_VALIDATOR, INGREDIENT_CATEGORIES, INT_PATTERN,
                     INT_VALIDATOR, MEAL_TYPE, MEASUREMENT_UNITS,
                     NAME_PATTERN, NAME_VALIDATOR, NON_EMPTY_PATTERN,
                     RECIPE_CATEGORIES, SIDEBAR, SORT_OPTIONS, ERROR_COLOR)
from .paths import AppPaths, QssPaths

__all__ = [
    "AppPaths", "QssPaths",
    "INGREDIENT_CATEGORIES",
    "MEASUREMENT_UNITS", "RECIPE_CATEGORIES",
    "DEBUG_LAYOUT_BORDERS",
    "APPLICATION_WINDOW",
    "SIDEBAR", "SORT_OPTIONS",
    "NAME_VALIDATOR", "FLOAT_VALIDATOR", "INT_VALIDATOR",
    "NON_EMPTY_PATTERN", "INT_PATTERN", "FLOAT_PATTERN", "NAME_PATTERN",
    "MEAL_TYPE", "ERROR_COLOR"
]
