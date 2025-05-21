"""core/helpers/ui_helpers.py

Helper functions for creating UI components in PySide6.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QGridLayout, QVBoxLayout, QWidget)

def make_overlay(base_widget: QWidget,
                 overlay_widget: QWidget,
                 margins: tuple[int,int,int,int] = (0, 8, 8, 0),
                 align: Qt.AlignmentFlag = Qt.AlignTop | Qt.AlignRight
) -> QWidget:
    """
    Stacks `overlay_widget` on top of `base_widget` at the given alignment,
    with optional padding (left, top, right, bottom).
    """
    container = QWidget()
    grid = QGridLayout(container)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setSpacing(0)

    # 1) put the base in cell (0,0)
    grid.addWidget(base_widget, 0, 0)

    # 2) wrap the overlay in its own widget to get padding
    pad = QWidget()
    pad.setStyleSheet("background:transparent;")
    pad.setAttribute(Qt.WA_TranslucentBackground)
    vlyt = QVBoxLayout(pad)
    vlyt.setContentsMargins(*margins)
    vlyt.setSpacing(0)
    vlyt.addWidget(overlay_widget)

    # 3) stack that padded overlay over the base
    grid.addWidget(pad, 0, 0, alignment=align)

    return container