"""recipe_card/builders/error_state.py

Defines the ErrorState class for generating error recipe card frames.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from ..constants import LAYOUT_SIZE, LayoutSize


# ── Class Definition ────────────────────────────────────────────────────────────
@dataclass(frozen=True, slots=True)
class ErrorState:
    """Builds the ErrorState frame shown when a recipe fails to load.

    Attributes:
        size (LayoutSize): Target card size (small, medium, or large).
        message (str): Human-readable error text to display.
    """

    size:    LayoutSize
    message: str = "Failed to load recipe."

    # ── Public Methods ──────────────────────────────────────────────────────────────
    def build(self) -> QFrame:
        """Build and return a QFrame displaying an error message.

        Returns:
            QFrame: Frame containing a centered error label.
        """
        # ── Create Frame ──
        frame = QFrame()
        frame.setObjectName("ErrorStateFrame")
        frame.setProperty("layout_size", self.size.value)
        frame.setFixedSize(LAYOUT_SIZE[self.size.value])

        # ── Layout ──
        lyt = QVBoxLayout(frame)
        lyt.setContentsMargins(4, 4, 4, 4)

        # error message
        lbl = QLabel(self.message)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setWordWrap(True)
        lbl.setStyleSheet("color: red;")
        lyt.addWidget(lbl) # add to layout

        return frame
