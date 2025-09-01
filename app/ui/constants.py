"""app/ui/constants.py

Configuration constants for the application.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from typing_extensions import Final


# ── Layout Constants ────────────────────────────────────────────────────────────────────────────────────────
class LayoutConstants:
    """Layout constants for consistent spacing and sizing throughout the application."""

    # Content margins and spacing
    CONTENT_MARGINS: Final[tuple[int, int, int, int]] = (130, 30, 130, 30)
    PAGE_SPACING: Final[int] = 25
    CONTENT_SECTION_SPACING: Final[int] = 30

    # Fixed heights
    FIXED_INPUT_HEIGHT: Final[int] = 60

    # Card configuration
    CARD_MARGINS: Final[tuple[int, int, int, int]] = (25, 25, 25, 25)
    CARD_SPACING: Final[int] = 15
    CARD_ICON_SIZE: Final[tuple[int, int]] = (30, 30)

    # Tags and info sections
    TAG_SPACING: Final[int] = 20
    INFO_CONTAINER_MARGINS: Final[tuple[int, int, int, int]] = (20, 10, 20, 10)
    INFO_CONTAINER_SPACING: Final[int] = 40

    # Ingredient list styling
    INGREDIENT_LIST_SPACING: Final[int] = 12
    INGREDIENT_GRID_SPACING: Final[int] = 10
    INGREDIENT_QTY_WIDTH: Final[int] = 60
    INGREDIENT_UNIT_WIDTH: Final[int] = 50

    # Directions list styling
    DIRECTIONS_LIST_SPACING: Final[int] = 15
    DIRECTIONS_ITEM_SPACING: Final[int] = 12
    DIRECTIONS_NUMBER_WIDTH: Final[int] = 30

    # Section headers
    SECTION_HEADER_SPACING: Final[int] = 10
    SECTION_ICON_SIZE: Final[tuple[int, int]] = (24, 24)

