""""app/config/config.py

    This module contains configuration settings for the application.
"""
import re
# ── Imports ─────────────────────────────────────────────────────────────────────
from pathlib import Path

from PySide6.QtCore import QRegularExpression, QSize
from PySide6.QtGui import QRegularExpressionValidator

# ── Icon Defaults ──
ICON_SIZE  = QSize(20, 20)
ERROR_COLOR = "#DD0AE0"  # A bright magenta for error states

APPLICATION_WINDOW = {
    "SETTINGS": {
        "APP_NAME": "MealGenie",
        "WINDOW_HEIGHT": 1080,
        "WINDOW_WIDTH":  1800,
        "BTN_SIZE": QSize(58, 58),
    },
}
SIDEBAR = {
    "SETTINGS": {
        "EXPANDED_WIDTH": 360,
        "COLLAPSED_WIDTH": 0,
        "DURATION": 800,  # animation duration in milliseconds
    }
}

# ── Recipe Configs ──
MEASUREMENT_UNITS = [
    "bag", "box", "can", "cap-full", "cup", "gallon", "half", "jar",
    "oz.", "pack", "pinch", "pint", "lb.", "liter", "quarter", "slice",
    "square", "strip", "Tbs", "tsp", "whole",
]
INGREDIENT_CATEGORIES = [
    "produce", "meat", "seafood", "pantry", "dairy", "deli", "frozen",
    "bakery", "baking", "condiments", "spices", "other",
]
MEAL_TYPE = [
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
