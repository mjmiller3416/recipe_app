"""app/ui/components/recipe_card/builders/empty_state.py

Defines the EmptyState class for generating empty recipe card frames.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────
from dataclasses import dataclass

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout

from app.theme_manager.icon import Name, Type
from app.ui.components.widgets import Button

from ..constants import LAYOUT_SIZE, LayoutSize


# ── Class Definition ────────────────────────────────────────────────────────────────────
@dataclass(frozen=True, slots=True)
class EmptyState:
    """Builds the EmptyState frame (big '+ Add Meal' button).

    Attributes:
        size (LayoutSize): Card size to honor (small, medium, or large).
    """

    size: LayoutSize

    # ── Public Methods ──────────────────────────────────────────────────────────────────
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
        btn_add = Button(Type.DEFAULT)
        btn_add.setIcon(Name.ADD_RECIPES)
        btn_add.setObjectName("AddMealButton") # slot looks for this
        btn_add.setCursor(Qt.PointingHandCursor)
        lyt.addWidget(btn_add, 0, Qt.AlignCenter) # add to layout

        return frame
