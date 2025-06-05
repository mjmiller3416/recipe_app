"""core/helpers/ui_helpers.py

Helper functions for creating UI components in PySide6.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QFrame, QGridLayout, QHBoxLayout, QSizePolicy,
                               QVBoxLayout, QWidget)

def create_hbox_with_widgets(*widgets, parent=None):
    layout = QHBoxLayout(parent)
    for w in widgets:
        layout.addWidget(w)
    return layout

def create_vbox_with_widgets(*widgets, parent=None):
    layout = QVBoxLayout(parent)
    for w in widgets:
        layout.addWidget(w)
    return layout

def make_overlay(base_widget: QWidget,
                 overlay_widget: QWidget,
                 margins: tuple[int,int,int,int] = (0, 8, 8, 0),
                 align: Qt.AlignmentFlag = Qt.AlignTop | Qt.AlignRight
) -> QWidget:
    """
    Stacks `overlay_widget` on top of `base_widget` at the given alignment,
    with optional padding (left, top, right, bottom).

    Args:
        base_widget (QWidget): The base widget to overlay on.
        overlay_widget (QWidget): The widget to overlay on top of the base.
        margins (tuple[int, int, int, int]): Padding around the overlay (left, top, right, bottom).
        align (Qt.AlignmentFlag): Alignment for the overlay widget.
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

def create_framed_layout(
        frame_shape:  QFrame.Shape = QFrame.Box,
        frame_shadow: QFrame.Shadow = QFrame.Plain,
        line_width:   int = 1,
        size_policy:  tuple = (QSizePolicy.Expanding, QSizePolicy.Expanding),
        margins:      tuple = (0, 0, 0, 0),
        spacing:      int = 0,
    ) -> tuple[QFrame, QVBoxLayout]:
        """Create a QFrame with a QVBoxLayout inside, with standardized styling.

        Args:
            frame_shape (QFrame.Shape): Shape of the frame (Box, NoFrame, etc.)
            frame_shadow (QFrame.Shadow): Shadow style of the frame.
            line_width (int): Line width for the frame border.
            size_policy (tuple): (horizontal, vertical) QSizePolicy values.
            margins (tuple): Layout margins (left, top, right, bottom).
            spacing (int): Spacing between layout elements.

        Returns:
            tuple[QFrame, QVBoxLayout]: The created frame and its layout.
        """
        # ── Create Frame & Layout ──
        frame = QFrame()
        frame.setFrameShape(frame_shape)
        frame.setFrameShadow(frame_shadow)
        frame.setLineWidth(line_width)
        frame.setSizePolicy(*size_policy)

        # ── Set Frame Properties ──
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(*margins)
        layout.setSpacing(spacing)

        return frame, layout

