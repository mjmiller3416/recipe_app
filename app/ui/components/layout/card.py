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
    with a title, optional subtitle, and a content area for other widgets.
    """

    def __init__(self, title: str = "", subtitle: str = "", parent=None):
        """Initialize the Card widget.

        Args:
            title (str): The main title of the card.
            subtitle (str): An optional subtitle for the card.
            parent: The parent widget, if any.
        """
        super().__init__(parent)

        # Register for component-specific styling
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
        if title:
            self._title_label = QLabel(title)
            self._title_label.setProperty("font", "Header")
            self._title_label.setAttribute(Qt.WA_StyledBackground)
            self._layout.addWidget(self._title_label)

        if subtitle:
            self._subtitle_label = QLabel(subtitle)
            self._subtitle_label.setProperty("font", "Subheader")
            self._subtitle_label.setAttribute(Qt.WA_StyledBackground)
            self._layout.addWidget(self._subtitle_label)

        # ── Content Area ──
        self.content_area = QVBoxLayout()
        self.content_area.setContentsMargins(0, 0, 0, 0)
        self.content_area.setSpacing(10)
        self._layout.addLayout(self.content_area)

        # ── Apply Effects ──
        Effects.apply_shadow(self, Shadow.ELEVATION_6)

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
