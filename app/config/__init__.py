"""
config package

Centralized configuration access for paths, constants, and user preferences.
"""

from .config import (CARD, DIETARY_PREFERENCES, FALLBACK_COLOR,
                     FLOAT_VALIDATOR, INGREDIENT_CATEGORIES, MEAL_TYPE,
                     MEASUREMENT_UNITS, NAME_PATTERN, RECIPE_CATEGORIES,
                     SIDEBAR, SORT_OPTIONS, AppConfig)
from .paths import AppPaths

__all__ = [
    "AppConfig",
    "AppPaths",
    "CARD",
    "DIETARY_PREFERENCES",
    "FALLBACK_COLOR",
    "FLOAT_VALIDATOR",
    "INGREDIENT_CATEGORIES",
    "MEAL_TYPE",
    "MEASUREMENT_UNITS",
    "NAME_PATTERN",
    "RECIPE_CATEGORIES",
    "SIDEBAR",
    "SORT_OPTIONS",
]
