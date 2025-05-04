""""config/config.py

    This module contains configuration settings for the application.
"""
# ── Imports ─────────────────────────────────────────────────────────────────────
from pathlib import Path

from PySide6.QtCore import QRegularExpression, QSize
from PySide6.QtGui import QRegularExpressionValidator

from core.helpers.debug_logger import DebugLogger

# ── Icon Defaults ──
ICON_SIZE = QSize(20, 20)

# ── Combobox Values ──
MEASUREMENT_UNITS = [
    "bag", "box", "can", "cap-full", "cup", "gallon", "half", "jar",
    "oz.", "pack", "pinch", "pint", "lb.", "quarter", "slice",
    "square", "strip", "Tbs", "tsp", "whole"
]

INGREDIENT_CATEGORIES = [
    "bakery", "baking", "dairy", "deli", "oils", "frozen",
    "meat", "pantry", "produce", "seafood", "spices", "other"
]

RECIPE_CATEGORIES = [
    "Breakfast", "Lunch", "Dinner", "Snack", "Dessert"
]

# ── Validation Rules ──
NAME = lambda parent: QRegularExpressionValidator(QRegularExpression(r"^[a-zA-Z0-9\s\-]+$"), parent)
FLOAT = lambda parent: QRegularExpressionValidator(QRegularExpression(r"^\d{1,2}(\.\d{0,2})?$"), parent)
INT = lambda parent: QRegularExpressionValidator(QRegularExpression(r"^\d{1,3}$"), parent)
NON_EMPTY = lambda parent: QRegularExpressionValidator(QRegularExpression(r"^(?!\s*$).+"), parent)

# ── Debug Flags ──
DEBUG_LAYOUT_BORDERS = True # set to True to draw layout borders
