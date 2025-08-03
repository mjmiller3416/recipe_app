""" app/ui/components/layout/card.py

A card widget with a header, sub-header and content area.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QFrame, QLabel, QVBoxLayout, QSizePolicy)

from app.appearance.config import Qss
from app.appearance.theme import Color, Mode, Theme
from app.appearance.effects import Effects, Shadow, Glow

# ── Card Widget ──────────────────────────────────────────────────────────────────────────────
class Card(QFrame):
    """A card widget with a header, sub-header and content area.

    This class provides a convenient way to create card-like UI components
    with a header, optional subheader, and a content area for other widgets.
    """

    def __init__(self, header: str = "", subheader: str = "", parent=None):
        """Initialize the Card widget.

        Args:
            header (str): The main header of the card.
            subheader (str): An optional subheader for the card.
            parent: The parent widget, if any.
        """
        super().__init__(parent)

        # register for component-specific styling
        Theme.register_widget(self, Qss.CARD)

        # ── Configure Frame Properties ──
        self.setProperty("tag", "Card")  # set a custom property for styling
        self.setAttribute(Qt.WA_StyledBackground)
        self._spacing = 10

        # sizing policy to prevent unnecessary stretching, card will only take needed space
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)


        # ── Create Layout ──
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(15, 15, 15, 15)
        self._layout.setSpacing(self._spacing)

        # ── Create Header ──
        self._header_container = QVBoxLayout()
        self._header_container.setContentsMargins(0, 0, 0, 0)
        self._header_container.setSpacing(6)
        if header:
            self._header_label = QLabel(header)
            self._header_label.setObjectName("Header")
            self._header_container.addWidget(self._header_label)

        if subheader:
            self._subheader_label = QLabel(subheader)
            self._subheader_label.setObjectName("Subheader")
            self._header_container.addWidget(self._subheader_label)

        self._layout.addLayout(self._header_container)

        # ── Content Area ──
        self.content_area = QVBoxLayout()
        self.content_area.setContentsMargins(0, 0, 0, 0)
        self.content_area.setSpacing(10)
        self._layout.addLayout(self.content_area)

        # ── Apply Effects ──
        Effects.apply_shadow(self, Shadow.ELEVATION_12)

    def add_widget(self, widget):
        """Add a widget to the content area of the card.

        Args:
            widget: The widget to add to the content area.
        """
        self.content_area.addWidget(widget)

    def setSpacing(self, spacing: int):
        """Set the spacing between elements in the card.

        Args:
            spacing (int): The spacing in pixels.
        """
        self._spacing = spacing
        self._layout.setSpacing(spacing)
        self.content_area.setSpacing(spacing)
