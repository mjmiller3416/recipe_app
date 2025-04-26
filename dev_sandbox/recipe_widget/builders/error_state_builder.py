# core/ui/recipe_widget/builders/error_state_builder.py
from __future__ import annotations

#🔸Standard Library
from dataclasses import dataclass

#🔸Third-party
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

#🔸Local Imports
from ..constants import LAYOUT_SIZE, LayoutSize

# ────────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class ErrorStateBuilder:
    """
    Builds the **Error-state** frame shown when a recipe fails to load.

    Parameters
    ----------
    size     : LayoutSize
        Card size (SMALL / MEDIUM / LARGE).
    message  : str
        Human-readable error text to display.
    """
    size:    LayoutSize
    message: str = "Failed to load recipe."

    # ── public ──────────────────────────────────────────────────────────────────────
    def build(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("ErrorStateFrame")
        frame.setProperty("layout_size", self.size.value) # for CSS styling
        frame.setFixedSize(LAYOUT_SIZE[self.size.value])

        lyt = QVBoxLayout(frame)
        lyt.setContentsMargins(4, 4, 4, 4)

        lbl = QLabel(self.message)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setWordWrap(True)
        lbl.setStyleSheet("color: red;")

        lyt.addWidget(lbl)

        return frame
