"""
config package

Centralized configuration access for paths, constants, and user preferences.
"""

from .app_config import (
    AppConfig,
    APPLICATION_WINDOW,
    CARD,
    DIETARY_PREFERENCES,
    FALLBACK_COLOR,
    FLOAT_VALIDATOR,
    INGREDIENT_CATEGORIES,
    MEAL_TYPE,
    MEASUREMENT_UNITS,
    NAME_PATTERN,
    RECIPE_CATEGORIES,
    SIDEBAR,
    SORT_OPTIONS,
)
from .app_paths import AppPaths

__all__ = [
    "AppConfig",
    "AppPaths",
    "APPLICATION_WINDOW",
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
