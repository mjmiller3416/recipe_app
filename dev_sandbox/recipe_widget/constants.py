"""recipe_widget/constants.py

Defines constants and enums used across the RecipeWidget layouts.
"""

# ── Imports ─────────────────────────────────────────────────────────────────── #                                                             #
from enum import Enum

from PySide6.QtCore import QSize


# ── Constants ───────────────────────────────────────────────────────────────────
LAYOUT_SIZE = {
    "small": QSize(280, 100),
    "medium": QSize(280, 420),
    "large": QSize(420, 600),
}
ICON_COLOR = "#03B79E"

# ── Enums ───────────────────────────────────────────────────────────────────────
class LayoutSize(Enum):
    """
    Enum to define the target layout size for the RecipeWidget when displaying a recipe.
    """
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


