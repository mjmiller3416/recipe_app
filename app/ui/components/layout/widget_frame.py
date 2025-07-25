"""app/ui/components/layout/widget_frame.py

A container widget that combines QFrame with integrated layout management and optional header.
"""

from typing import Optional, Union

from PySide6.QtCore import Qt
# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtWidgets import (QFrame, QGridLayout, QHBoxLayout, QLabel,
                               QScrollArea, QSizePolicy, QVBoxLayout, QWidget)


class WidgetFrame(QFrame):
    """A QFrame container with integrated layout management and optional header.

    This class provides a convenient way to create framed containers with
    pre-configured layouts and an optional header section for organizing UI components.
    """

    def __init__(self,
                title: Optional[str] = None,
                layout: type = QVBoxLayout,
                scrollable: bool = False,
                frame_shadow: QFrame.Shadow = QFrame.Plain,
                size_policy: tuple = (QSizePolicy.Expanding, QSizePolicy.Expanding),
                margins: tuple = (10, 10, 10, 10),
                spacing: int = 10,
                parent: Optional[QFrame] = None
    ):
        """Initialize the WidgetFrame.

        Args:
            header_text (Optional[str]): Text for the header label, if any
            layout_cls (type): Type of layout to use for the content area (QVBoxLayout, QHBoxLayout, QGridLayout)
            scrollable (bool): Whether the content area should be scrollable
            horizontal_scrollbar (Qt.ScrollBarPolicy): Horizontal scrollbar policy
            vertical_scrollbar (Qt.ScrollBarPolicy): Vertical scrollbar policy
            frame_shape (QFrame.Shape): Shape of the frame
            frame_shadow (QFrame.Shadow): Shadow style of the frame
            line_width (int): Width of the frame line
            size_policy (tuple): Size policy for the frame and content widget
            margins (tuple): Margins for the content layout
            spacing (int): Spacing between items in the content layout
            parent (Optional[QFrame]): Parent widget for this frame
        """
        super().__init__(parent)

        # ── Configure Frame Properties ──
        self.setFrameShadow(frame_shadow)
        self.setSizePolicy(*size_policy)
        self.setProperty("class", "WidgetFrame") # set a custom property for styling
        self.setAttribute(Qt.WA_StyledBackground)


        # ── Create Main Layout ──
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        # ── Create Title ──
        self._title_label = None
        if title:
            self._create_title(title)
            self._title_label.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        # ── Set Scrollable Properties ──
        self._scrollable = scrollable

        # ── Create Content Area ──
        self._content_widget = QWidget()
        self._content_widget.setObjectName("WidgetFrameContent")
        self._content_widget.setProperty("obj", "WidgetFrameContent")
        self._content_layout = layout()  # create the content layout based on the specified type

        # ── configure layout properties ──
        if isinstance(self._content_layout, QVBoxLayout):
            self._content_layout.setAlignment(Qt.AlignTop)
            self._content_layout.setSpacing(spacing)

        elif isinstance(self._content_layout, QHBoxLayout):
            self._content_layout.setAlignment(Qt.AlignLeft)
            self._content_layout.setSpacing(spacing)

        elif isinstance(self._content_layout, QGridLayout):
            self._content_layout.setHorizontalSpacing(spacing)
            self._content_layout.setVerticalSpacing(spacing)

        self._content_layout.setContentsMargins(*margins)  # set margins for content layout

        # ── apply layout  to content widget ──
        self._content_widget.setSizePolicy(*size_policy) # set size policy for content widget
        self._content_widget.setLayout(self._content_layout) # set the content layout

        # ── Add Content Widget to Main Layout ──
        if self._scrollable:
            self._scroll_area = QScrollArea()
            self._scroll_area.setObjectName("WidgetFrameScrollArea")
            self._scroll_area.setProperty("obj", "WidgetFrameScrollArea")
            self._scroll_area.setWidget(self._content_widget)
            self._scroll_area.setWidgetResizable(True)
            self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

            self._main_layout.addWidget(self._scroll_area)
        else:
            self._scroll_area = None
            self._main_layout.addWidget(self._content_widget)

    def _create_title(self, title: str):
        """Create the header section with label.

        Args:
            header_text (str): Text for the header label
        """
        self._title_label = QLabel(title)
        self._title_label.setObjectName("WidgetFrameHeader")
        self._title_label.setProperty("obj", "WidgetFrameHeader")
        self._title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._main_layout.addWidget(self._title_label)

    def addWidget(self, widget, *args, **kwargs):
        """Add a widget to the frame's content layout.

        Args:
            widget: The widget to add
            *args, **kwargs: Additional arguments passed to the layout's addWidget method
        """
        self._content_layout.addWidget(widget, *args, **kwargs)

    def removeWidget(self, widget, *args, **kwargs):
        """Remove a widget from the frame's content layout.

        Args:
            widget: The widget to remove
            *args, **kwargs: Additional arguments passed to the layout's removeWidget method
        """
        self._content_layout.removeWidget(widget, *args, **kwargs)

    def addLayout(self, layout, *args, **kwargs):
        """Add a layout to the frame's content layout.

        Args:
            layout: The layout to add
            *args, **kwargs: Additional arguments passed to the layout's addLayout method
        """
        self._content_layout.addLayout(layout, *args, **kwargs)

    def getLayout(self) -> Union[QVBoxLayout, QHBoxLayout, QGridLayout]:
        """Get the internal content layout object.

        Returns:
            The internal content layout object
        """
        return self._content_layout

    def addStretch(self, stretch: int = 0):
        """Add stretch to the content layout (only works with box layouts).

        Args:
            stretch (int): Stretch factor
        """
        if hasattr(self._content_layout, 'addStretch'):
            self._content_layout.addStretch(stretch)

    def setContentsMargins(self, left: int, top: int, right: int, bottom: int):
        """Set the content layout margins.

        Args:
            left (int): Left margin
            top (int): Top margin
            right (int): Right margin
            bottom (int): Bottom margin
        """
        self._content_layout.setContentsMargins(left, top, right, bottom)

    def setSpacing(self, spacing: int):
        """Set the content layout spacing.

        Args:
            spacing (int): Spacing between layout elements
        """
        self._content_layout.setSpacing(spacing)

    def get_header_label(self) -> Optional[QLabel]:
        """Get the header label widget.

        Returns:
            The header label widget or None if no header was created
        """
        return self._header_label

    def set_header_text(self, text: str):
        """Set the header text.

        Args:
            text (str): New header text
        """
        if self._header_label:
            self._header_label.setText(text)
