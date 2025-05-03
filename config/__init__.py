"""
config package

Centralized configuration access for paths, constants, and user preferences.
"""

from .config import (
    ICON_SIZE,
    ICON_COLOR,
    ICON_COLOR_HOVER,
    ICON_COLOR_CHECKED,
    SUCCESS_COLOR,
    ERROR_COLOR,
    WARNING_COLOR,
    INFO_COLOR,
    LOGO_COLOR,
    MEASUREMENT_UNITS,
    INGREDIENT_CATEGORIES,
    RECIPE_CATEGORIES,
    icon_path,
    image_path,
    recipe_image_path,
    DEBUG_LAYOUT_BORDERS,
)

from .user_settings import UserSettings
from .paths import AppPaths, QssPaths

__all__ = [
    "AppPaths", "QssPaths",
    "UserSettings",
    "ICON_SIZE", "ICON_COLOR", "ICON_COLOR_HOVER", "ICON_COLOR_CHECKED",
    "SUCCESS_COLOR", "ERROR_COLOR", "WARNING_COLOR", "INFO_COLOR",
    "LOGO_COLOR", "MEASUREMENT_UNITS", "INGREDIENT_CATEGORIES", "RECIPE_CATEGORIES",
    "icon_path", "image_path", "recipe_image_path",
    "DEBUG_LAYOUT_BORDERS"
]
