"""recipe_widget/builders/empty_state_builder.py

Defines the EmptyStateBuilder class for generating empty recipe card frames.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from dataclasses import dataclass

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout

from helpers.icon_helpers.widgets import IconButton

from ..constants import LAYOUT_SIZE, LayoutSize

# ── Constants ───────────────────────────────────────────────────────────────────
ICON_SIZE = QSize(60, 60)

# ── Class Definition ────────────────────────────────────────────────────────────
@dataclass(frozen=True, slots=True)
class EmptyStateBuilder:
    """Builds the EmptyState frame (big '+ Add Meal' button).

    Attributes:
        size (LayoutSize): Card size to honor (small, medium, or large).
    """

    size: LayoutSize

    # ── Public Methods ──────────────────────────────────────────────────────────────
    def build(self) -> QFrame:
        """Build and return a QFrame representing an empty recipe card.

        Returns:
            QFrame: Frame containing a centered 'Add Meal' button.
        """
        # ── Create Frame ──
        frame = QFrame()
        frame.setObjectName("EmptyStateFrame")
        frame.setProperty("layout_size", self.size.value)
        frame.setFixedSize(LAYOUT_SIZE[self.size.value])

        # ── Layout ──
        lyt = QVBoxLayout(frame)
        lyt.setContentsMargins(0, 0, 0, 0)

        # add meal button
        btn_add = IconButton(
            path="add_meal.svg",
            size=ICON_SIZE
        )
        btn_add.setObjectName("AddMealButton") # slot looks for this
        btn_add.setCursor(Qt.PointingHandCursor)
        lyt.addWidget(btn_add, 0, Qt.AlignCenter) # add to layout

        return frame
