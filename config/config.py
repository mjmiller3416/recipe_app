""""config/config.py

    This module contains configuration settings for the application.
"""
# ── Imports ─────────────────────────────────────────────────────────────────────
from pathlib import Path

from PySide6.QtCore import QRegularExpression, QSize
from PySide6.QtGui import QRegularExpressionValidator

from core.helpers.debug_logger import DebugLogger

# ── Directory Paths ──
BASE_DIR = Path(__file__).resolve().parents[2]
ASSETS_DIR = BASE_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
IMAGES_DIR = ASSETS_DIR / "images"
RECIPE_DIR = ASSETS_DIR / "recipe_images"

# ── Icon Defaults ──
ICON_SIZE = QSize(20, 20)
ICON_COLOR = "#949aa7"
ICON_COLOR_HOVER = "#6ad7ca"
ICON_COLOR_CHECKED = "#6ad7ca"

# ── Dialog Colors ──
SUCCESS_COLOR = "#5cde42"
ERROR_COLOR = "#ff4d4d"
WARNING_COLOR = "#ffcc00"
INFO_COLOR = "#6ad7ca"

# ── Logo Colors ──
LOGO_COLOR = "#949aa7"

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

# ── Public Methods ──────────────────────────────────────────────────────────────
def icon_path(name: str) -> str:
    if not name:
        DebugLogger.log("[ERROR] [icon_path] Empty name passed to icon_path()", "error")
        return "invalid.svg"  # or a default fallback path?
    return str(ICONS_DIR / f"{name}.svg")

def image_path(name: str) -> str:
    return str(IMAGES_DIR / f"{name}.svg")  # all images must be SVG

def recipe_image_path(name: str) -> str:
    return str(IMAGES_DIR / f"{name}.png")  # all recipe images must be PNG

