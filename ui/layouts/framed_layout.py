"""ui/layouts/framed_layout.py

The layout can be any subclass of QLayout, such as QVBoxLayout or QHBoxLayout.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from typing import Type

from PySide6.QtWidgets import QFrame, QLayout, QSizePolicy, QVBoxLayout


def create_framed_layout(
    layout_cls:    Type[QLayout] = QVBoxLayout, 
    frame_shape:   QFrame.Shape = QFrame.Box,
    frame_shadow:  QFrame.Shadow = QFrame.Plain,
    line_width:    int = 1,
    size_policy:   tuple = (QSizePolicy.Expanding, QSizePolicy.Expanding),
    margins:       tuple = (0, 0, 0, 0),
    spacing:       int = 0,
) -> tuple[QFrame, QLayout]:
    """
    Create a QFrame with a user-defined QLayout (default: QVBoxLayout).

    Args:
        layout_cls (Type[QLayout]): The layout class to instantiate (e.g. QVBoxLayout, QHBoxLayout).
        frame_shape (QFrame.Shape): Shape of the frame (Box, NoFrame, etc.).
        frame_shadow (QFrame.Shadow): Shadow style of the frame.
        line_width (int): Line width for the frame border.
        size_policy (tuple): (horizontal, vertical) QSizePolicy values.
        margins (tuple): Layout margins (left, top, right, bottom).
        spacing (int): Spacing between layout elements.

    Returns:
        tuple[QFrame, QLayout]: The created frame and its layout.
    """
    frame = QFrame()
    frame.setFrameShape(frame_shape)
    frame.setFrameShadow(frame_shadow)
    frame.setLineWidth(line_width)
    frame.setSizePolicy(*size_policy)

    layout = layout_cls(frame)
    layout.setContentsMargins(*margins)
    layout.setSpacing(spacing)

    return frame, layout