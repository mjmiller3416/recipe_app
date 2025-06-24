"""app/ui/pages/dashboard/widget_sizes.py

Enum defining the available widget sizes for the dashboard grid.
"""

# ── Imports ────────────────────────────────────────────
from enum import Enum


class WidgetSize(Enum):
    """Available widget sizes expressed as (cols, rows)."""

    ONE_BY_ONE = (1, 1)
    ONE_BY_TWO = (1, 2)
    THREE_BY_ONE = (3, 1)
    FOUR_BY_THREE = (4, 3)

    def cols(self) -> int:
        """Return the width of the widget in grid columns."""
        return self.value[0]

    def rows(self) -> int:
        """Return the height of the widget in grid rows."""
        return self.value[1]
