# recipe_widget/builders/empty_state_builder.py
# ────────────────────────────────────────────────────────────────────────────────

#🔸Standard Library
from dataclasses import dataclass

#🔸Third-party
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QFrame, QPushButton, QVBoxLayout

from helpers.icons.widgets import IconButton

#🔸Local Imports
from ..constants import LAYOUT_SIZE, LayoutSize

#🔸Constants
ICON_SIZE = QSize(60, 60) 
# ────────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class EmptyStateBuilder:
    """
    Builds the **Empty-state** frame (big “+ Add Meal” button).

    Parameters
    ----------
    size : LayoutSize
        Card size to honour (SMALL / MEDIUM / LARGE).
    """
    size: LayoutSize

    # ── public ──────────────────────────────────────────────────────────────────────
    def build(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("EmptyStateFrame")
        frame.setProperty("layout_size", self.size.value) # for CSS styling
        frame.setFixedSize(LAYOUT_SIZE[self.size.value])

        lyt = QVBoxLayout(frame)
        lyt.setContentsMargins(0, 0, 0, 0)

        btn_add = QPushButton()
        btn_add.setObjectName("AddMealButton")     # <- slot looks for this
        btn_add.setFixedSize(60, 60)
        btn_add.setCursor(Qt.PointingHandCursor)

        btn_add = IconButton(path="add_meal.svg", size=ICON_SIZE)

        lyt.addStretch(1)
        lyt.addWidget(btn_add, 0, Qt.AlignCenter)
        lyt.addStretch(1)

        return frame