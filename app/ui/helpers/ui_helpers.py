"""app/ui/helpers/ui_helpers.py

Helper functions for creating UI components in PySide6.
"""

from typing import Iterable, Union

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QFrame, QGridLayout, QHBoxLayout, QSizePolicy,
                               QVBoxLayout, QWidget)


# ── Functions ───────────────────────────────────────────────────────────────────
from PySide6.QtWidgets import QLayout, QWidget, QLabel

def set_fixed_height_for_layout_widgets(
    layout: QLayout,
    height: int,
    skip: tuple[type[QWidget], ...] = (QLabel,)
) -> None:
    """Set a fixed height for all widgets in a layout, skipping specified widget types.

    Args:
        layout (QLayout): The layout containing widgets.
        height (int): The fixed height to apply.
        skip (tuple): Widget classes to skip (default: QLabel).
    """
    for i in range(layout.count()):
        item = layout.itemAt(i)
        widget = item.widget()

        if widget is None or isinstance(widget, skip):
            continue

        widget.setFixedHeight(height)

def create_fixed_wrapper(
    widgets: Union[QWidget, Iterable[QWidget]],
    fixed_width: int,
    alignment: Qt.Alignment = Qt.AlignCenter,
    direction: str = "horizontal",
    margins: tuple[int, int, int, int] = (0, 0, 0, 0)
) -> QWidget:
    """
    Wraps one or more widgets inside a QWidget with fixed width and layout.

    Args:
        widgets (QWidget or iterable of QWidget): Widget(s) to wrap.
        fixed_width (int): Fixed width for the wrapper.
        alignment (Qt.Alignment, optional): Alignment for each widget inside the layout.
        direction (str, optional): 'horizontal' or 'vertical'. Defaults to 'horizontal'.
        margins (tuple[int, int, int, int], optional): Margins for the layout (left, top, right, bottom). Defaults to (0, 0, 0, 0).

    Returns:
        QWidget: Wrapper widget with layout and given contents.
    """
    wrapper = QWidget()
    wrapper.setFixedWidth(fixed_width)

    LayoutClass = QVBoxLayout if direction == "vertical" else QHBoxLayout
    layout = LayoutClass(wrapper)
    layout.setContentsMargins(*margins)

    # apply layout-wide alignment only if horizontal
    if direction == "horizontal":
        layout.setAlignment(alignment)

    # add each widget with its own alignment
    if isinstance(widgets, QWidget):
        layout.addWidget(widgets, alignment=alignment)
    else:
        for w in widgets:
            layout.addWidget(w, alignment=alignment)

    return wrapper

def create_hbox_with_widgets(*widgets, parent=None):
    """
    Creates a QHBoxLayout and adds the given widgets to it.
    
    Args:
        *widgets: Variable number of QWidget instances to add to the layout.
        parent (QWidget, optional): Parent widget for the layout. Defaults to None.
    """
    layout = QHBoxLayout(parent)
    for w in widgets:
        layout.addWidget(w)
    return layout

def create_vbox_with_widgets(*widgets, parent=None):
    """
    Creates a QVBoxLayout and adds the given widgets to it.
    
    Args:
        *widgets: Variable number of QWidget instances to add to the layout.
        parent (QWidget, optional): Parent widget for the layout. Defaults to None.
    """
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

    # put the base in cell (0,0)
    grid.addWidget(base_widget, 0, 0)

    # wrap the overlay in its own widget to get padding
    pad = QWidget()
    pad.setStyleSheet("background:transparent;")
    pad.setAttribute(Qt.WA_TranslucentBackground)
    vlyt = QVBoxLayout(pad)
    vlyt.setContentsMargins(*margins)
    vlyt.setSpacing(0)
    vlyt.addWidget(overlay_widget)

    # stack that padded overlay over the base
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
        # create the frame
        frame = QFrame()
        frame.setFrameShape(frame_shape)
        frame.setFrameShadow(frame_shadow)
        frame.setLineWidth(line_width)
        frame.setSizePolicy(*size_policy)

        # set up the layout
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(*margins)
        layout.setSpacing(spacing)

        return frame, layout

