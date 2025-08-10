""" app/ui/components/layout/card.py

A generic container widget with elevation effects and flexible layout management.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy, QWidget, QLabel)

from app.style.theme.config import Qss
from app.style.theme_controller import Color, Mode, Theme
from app.style.effects import Effects, Shadow, Glow

# ── Card Widget ──────────────────────────────────────────────────────────────────────────────
class Card(QFrame):
    """A generic container widget with elevation effects and flexible layout management.

    This class provides a container that automatically scales based on its contents
    with configurable content margins and elevation effects. Supports multiple
    layout types (QVBox, QHBox, QGrid) and provides a clean API for content management.
    """

    def __init__(self, parent=None, elevation=Shadow.ELEVATION_6):
        """Initialize the Card widget.

        Args:
            parent: The parent widget, if any.
            elevation: Shadow elevation level from Shadow enum (default: ELEVATION_1).
        """
        super().__init__(parent)

        # register for component-specific styling
        Theme.register_widget(self, Qss.CARD)

        # ── Configure Frame Properties ──
        self.setProperty("tag", "Card")  # set a custom property for styling
        self.setAttribute(Qt.WA_StyledBackground)

        # sizing policy to size to contents (not expand beyond necessary)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # ── Initialize Layout Variables ──
        self._current_layout = None
        self._elevation = elevation
        self._elevation_enabled = True
        self._header_label = None

        # ── Create Default Layout ──
        self.addLayout("vbox")  # Default to vertical box layout

        # ── Apply Effects ──
        if self._elevation_enabled:
            Effects.apply_shadow(self, self._elevation)

    def addLayout(self, layout_type: str, spacing: int = 10):
        """Add or replace the current layout.

        Args:
            layout_type (str): Type of layout - 'vbox', 'hbox', or 'grid'.
            spacing (int): Spacing between layout items in pixels.

        Returns:
            The created layout object.
        """
        # Clear existing layout if any
        if self._current_layout:
            # Clear the existing layout
            while self._current_layout.count():
                item = self._current_layout.takeAt(0)
                if item.widget():
                    item.widget().setParent(None)
            self._current_layout.deleteLater()

        # Create new layout based on type
        layout_type = layout_type.lower()
        if layout_type == "vbox":
            self._current_layout = QVBoxLayout(self)
        elif layout_type == "hbox":
            self._current_layout = QHBoxLayout(self)
        elif layout_type == "grid":
            self._current_layout = QGridLayout(self)
        else:
            raise ValueError(f"Unsupported layout type: {layout_type}. Use 'vbox', 'hbox', or 'grid'.")

        # Set default content margins (20px on all sides)
        self._current_layout.setContentsMargins(20, 20, 20, 20)
        self._current_layout.setSpacing(spacing)

        return self._current_layout

    def addWidget(self, widget: QWidget, *args, **kwargs):
        """Add a widget to the current layout.

        Args:
            widget: The widget to add.
            *args, **kwargs: Additional arguments passed to the layout's addWidget method.
                           For QGridLayout: row, column, rowSpan=1, columnSpan=1
                           For QVBoxLayout/QHBoxLayout: stretch=0, alignment=Qt.Alignment()
        """
        if not self._current_layout:
            self.add_layout("vbox")  # Default layout if none exists

        if isinstance(self._current_layout, QGridLayout):
            # For grid layout, expect row, column as minimum args
            if len(args) < 2:
                raise ValueError("Grid layout requires at least row and column arguments")
            self._current_layout.addWidget(widget, *args, **kwargs)
        else:
            # For box layouts
            self._current_layout.addWidget(widget, *args, **kwargs)

    def setContentMargins(self, left: int, top: int, right: int, bottom: int):
        """Set the content margins of the current layout.

        Args:
            left (int): Left margin in pixels.
            top (int): Top margin in pixels.
            right (int): Right margin in pixels.
            bottom (int): Bottom margin in pixels.
        """
        if self._current_layout:
            self._current_layout.setContentsMargins(left, top, right, bottom)

    def setSpacing(self, spacing: int):
        """Set the spacing between elements in the current layout.

        Args:
            spacing (int): The spacing in pixels.
        """
        if self._current_layout:
            self._current_layout.setSpacing(spacing)

    def setElevation(self, elevation: Shadow):
        """Set the elevation effect.

        Args:
            elevation: Shadow elevation level from Shadow enum.
        """
        self._elevation = elevation
        if self._elevation_enabled:
            Effects.apply_shadow(self, self._elevation)

    def enableElevation(self, enabled: bool = True):
        """Enable or disable elevation effects.

        Args:
            enabled (bool): Whether to enable elevation effects.
        """
        self._elevation_enabled = enabled
        if enabled:
            Effects.apply_shadow(self, self._elevation)
        else:
            # Remove shadow effect by applying ELEVATION_0
            Effects.apply_shadow(self, Shadow.ELEVATION_0)

    def getLayout(self):
        """Get the current layout object.

        Returns:
            The current layout (QVBoxLayout, QHBoxLayout, or QGridLayout).
        """
        return self._current_layout

    def clearWidgets(self):
        """Clear all widgets from the current layout."""
        if self._current_layout:
            while self._current_layout.count():
                item = self._current_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

    def expandWidth(self, expand: bool = True):
        """Enable or disable width expansion.

        Args:
            expand (bool): Whether the card should expand horizontally to fill available space.
        """
        current_policy = self.sizePolicy()
        if expand:
            self.setSizePolicy(QSizePolicy.Expanding, current_policy.verticalPolicy())
        else:
            self.setSizePolicy(QSizePolicy.Fixed, current_policy.verticalPolicy())

    def expandHeight(self, expand: bool = True):
        """Enable or disable height expansion.

        Args:
            expand (bool): Whether the card should expand vertically to fill available space.
        """
        current_policy = self.sizePolicy()
        if expand:
            self.setSizePolicy(current_policy.horizontalPolicy(), QSizePolicy.Expanding)
        else:
            self.setSizePolicy(current_policy.horizontalPolicy(), QSizePolicy.Fixed)

    def expandBoth(self, expand: bool = True):
        """Enable or disable both width and height expansion.

        Args:
            expand (bool): Whether the card should expand to fill all available space.
        """
        if expand:
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        else:
            self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def setHeader(self, text: str, tag: str = "Sub-Header"):
        """Set or update the header label for the card.

        Args:
            text (str): The header text to display.
            tag (str): The tag property for styling purposes (default: "Sub-Header").
        """
        if self._header_label is None:
            self._header_label = QLabel(text)
            self._header_label.setProperty("tag", tag)
            # Insert at the top of the layout
            if self._current_layout:
                self._current_layout.insertWidget(0, self._header_label)
        else:
            self._header_label.setText(text)
            self._header_label.setProperty("tag", tag)
            # Force style update to apply new tag
            self._header_label.style().unpolish(self._header_label)
            self._header_label.style().polish(self._header_label)
