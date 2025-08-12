""" app/ui/components/layout/card.py

A generic container widget with elevation effects and flexible layout management.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import warnings
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QSizePolicy,
    QWidget,
    QLabel,
    QLayout,
)
from typing import Optional, Tuple

from app.style import Theme, Qss
from app.style.icon import AppIcon, Name
from app.style.effects import Effects, Shadow, Glow


# ── Card Widget ──────────────────────────────────────────────────────────────────────────────
class Card(QFrame):
    """A generic container widget with elevation effects and flexible layout management.

    This class provides a container that automatically scales based on its contents
    with configurable content margins and elevation effects. Supports multiple
    layout types (QVBox, QHBox, QGrid) and provides a clean API for content management.
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        elevation: Shadow = Shadow.ELEVATION_6,
        layout: str = "vbox",
        card_type: str = "Default",
    ):
        """Initialize the Card widget.

        Args:
            parent: Optional parent widget.
            elevation: Shadow elevation level from Shadow enum (default: ELEVATION_6).
            layout: Initial layout type: "vbox" (default), "hbox", or "grid".
            card_type: Card styling type for QSS (default: "Default").
        """
        super().__init__(parent)

        # Register for component-specific styling
        Theme.register_widget(self, Qss.CARD)

        # ── Configure Frame Properties ──
        self._card_type = card_type
        self.setProperty("card", card_type)  # custom property for styling
        self.setAttribute(Qt.WA_StyledBackground)

        # Size to contents by default
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # ── Internal State ──
        self._current_layout: QLayout | None = None
        self._elevation = elevation
        self._elevation_enabled = True

        # Header bits
        self._header_container: QWidget | None = None
        self._header_layout: QHBoxLayout | None = None
        self._header_label: QLabel | None = None
        self._header_icon_widget: QWidget | None = None  # exposed via headerIcon property
        self._subheader_label: QLabel | None = None

        # ── Create Initial Layout ──
        self._add_layout(layout_type=layout, spacing=10)  # defaults to vbox if invalid

        # ── Apply Effects ──
        if self._elevation_enabled:
            Effects.apply_shadow(self, self._elevation)

    # ── Layout Helpers ────────────────────────────────────────────────────────────────────────
    def _clear_current_layout(self) -> None:
        """Remove all child widgets and delete the current layout (internal)."""
        if not self._current_layout:
            return

        while self._current_layout.count():
            item = self._current_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()

        self._current_layout.deleteLater()
        self._current_layout = None

    def _add_layout(self, layout_type: str = "vbox", spacing: int = 10):
        """Create/replace the internal layout. Private API."""
        lt = (layout_type or "vbox").strip().lower()

        self._clear_current_layout()

        if lt == "hbox":
            self._current_layout = QHBoxLayout(self)
        elif lt == "grid":
            self._current_layout = QGridLayout(self)
        else:
            # default fallback to vbox
            self._current_layout = QVBoxLayout(self)

        self._current_layout.setContentsMargins(20, 20, 20, 20)
        self._current_layout.setSpacing(spacing)
        return self._current_layout

    def setLayoutType(self, layout_type: str, *, spacing: Optional[int] = None) -> None:
        """Public wrapper to switch between 'vbox' | 'hbox' | 'grid' at runtime."""
        self._add_layout(layout_type=layout_type, spacing=(spacing if spacing is not None else 10))
        # Reinsert header and subheader if they existed
        if self._header_container and self._current_layout:
            self._current_layout.insertWidget(0, self._header_container)
        if self._subheader_label and self._current_layout:
            insert_index = 1 if self._header_container else 0
            self._current_layout.insertWidget(insert_index, self._subheader_label)


    # ── Public Layout API ─────────────────────────────────────────────────────────────────────
    def addWidget(self, widget: QWidget, *args, **kwargs):
        """Add a widget to the current layout.

        For QGridLayout: row, column, rowSpan=1, columnSpan=1
        For QVBoxLayout/QHBoxLayout: stretch=0, alignment=Qt.Alignment()
        """
        if not self._current_layout:
            self._add_layout("vbox")

        if isinstance(self._current_layout, QGridLayout):
            if len(args) < 2:
                raise ValueError("Grid layout requires at least row and column arguments")
            self._current_layout.addWidget(widget, *args, **kwargs)
        else:
            self._current_layout.addWidget(widget, *args, **kwargs)


    def setContentMargins(self, left: int, top: int, right: int, bottom: int):
        """Set the content margins of the current layout."""
        if self._current_layout:
            self._current_layout.setContentsMargins(left, top, right, bottom)

    def setSpacing(self, spacing: int):
        """Set the spacing between elements in the current layout."""
        if self._current_layout:
            self._current_layout.setSpacing(spacing)

    def getLayout(self) -> QLayout | None:
        """Get the current layout object (QVBoxLayout, QHBoxLayout, or QGridLayout)."""
        return self._current_layout

    def clearWidgets(self):
        """Clear all widgets from the current layout (excludes header container and subheader)."""
        if not self._current_layout:
            return
        # Keep header container and subheader if present
        reserved_widgets = {self._header_container, self._subheader_label}
        widgets_to_remove = []
        
        for i in range(self._current_layout.count()):
            item = self._current_layout.itemAt(i)
            if item and item.widget() and item.widget() not in reserved_widgets:
                widgets_to_remove.append(item.widget())
        
        for widget in widgets_to_remove:
            self._current_layout.removeWidget(widget)
            widget.deleteLater()

    def setElevation(self, elevation: Shadow):
        """Set the elevation effect."""
        self._elevation = elevation
        if self._elevation_enabled:
            Effects.apply_shadow(self, self._elevation)

    def enableElevation(self, enabled: bool = True):
        """Enable or disable elevation effects."""
        self._elevation_enabled = enabled
        if enabled:
            Effects.apply_shadow(self, self._elevation)
        else:
            Effects.apply_shadow(self, Shadow.ELEVATION_0)

    def expandWidth(self, expand: bool = True):
        """Enable or disable width expansion."""
        current_policy = self.sizePolicy()
        if expand:
            self.setSizePolicy(QSizePolicy.Expanding, current_policy.verticalPolicy())
        else:
            self.setSizePolicy(QSizePolicy.Fixed, current_policy.verticalPolicy())

    def expandHeight(self, expand: bool = True):
        """Enable or disable height expansion."""
        current_policy = self.sizePolicy()
        if expand:
            self.setSizePolicy(current_policy.horizontalPolicy(), QSizePolicy.Expanding)
        else:
            self.setSizePolicy(current_policy.horizontalPolicy(), QSizePolicy.Fixed)

    def expandBoth(self, expand: bool = True):
        """Enable or disable both width and height expansion."""
        if expand:
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        else:
            self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    # ── Header (with optional icon) ─────────────────────────────────────────────────────────
    def setHeader(
        self,
        text: str,
        icon: Optional[object] = None,
    ):
        """Set or update the header with optional icon.

        Args:
            text: Header text.
            tag: QSS tag used for styling (defaults to "Header").
            icon: Optional icon. One of:
                  - Name enum (preferred) -> will construct an AppIcon
                  - QWidget (e.g., AppIcon/StateIcon) -> used as-is
                  - None -> text-only header
        """
        # Lazily build a container for [icon][label] the first time
        if self._header_container is None:
            self._header_container = QWidget(self)
            self._header_container.setAttribute(Qt.WA_StyledBackground, False)

            self._header_layout = QHBoxLayout(self._header_container)
            self._header_layout.setContentsMargins(0, 0, 0, 0)
            self._header_layout.setSpacing(8)  # gap between icon and text

            self._header_label = QLabel(text)
            self._header_label.setObjectName("Header")

            # Insert at the top of the card layout
            if self._current_layout:
                self._current_layout.insertWidget(0, self._header_container)

            # Add label last (icon slot is before it)
            self._header_layout.addWidget(self._header_label, 0, Qt.AlignVCenter)
        else:
            # Update text + tag
            self._header_label.setText(text)
            self._header_label.setObjectName("Header")
            # Force style refresh when tag changes
            self._header_label.style().unpolish(self._header_label)
            self._header_label.style().polish(self._header_label)

        # If an icon is provided, apply it; if explicitly None, remove any existing icon
        if icon is not None:
            self.setHeaderIcon(icon)
        elif self._header_icon_widget is not None:
            self.clearHeaderIcon()

    def setHeaderIcon(self, icon: object):
        """Set or replace the header's icon.

        The resulting widget is exposed via the `headerIcon` property for direct calls.

        Args:
            icon:
                - Name enum (preferred): constructs an AppIcon
                - QWidget (AppIcon/StateIcon/etc.): used as-is
        """
        if self._header_container is None or self._header_layout is None:
            # Ensure header base exists (creates label-only if needed)
            self.setHeader(text=(self._header_label.text() if self._header_label else ""))

        # Remove previous icon
        if self._header_icon_widget is not None:
            self._header_layout.removeWidget(self._header_icon_widget)
            self._header_icon_widget.deleteLater()
            self._header_icon_widget = None

        # Accept either a ready-made QWidget or a Name enum
        if isinstance(icon, QWidget):
            self._header_icon_widget = icon
        else:
            created = False
            if Name is not None and hasattr(icon, "spec"):
                if AppIcon is None:
                    raise ImportError(
                        "AppIcon widget not available. Ensure 'app.appearance.icon.icon' is importable."
                    )
                self._header_icon_widget = AppIcon(icon)
                created = True

            if not created:
                raise TypeError(
                    "Unsupported icon type. Pass a Name enum value or a QWidget (e.g., AppIcon/StateIcon)."
                )

        # Insert icon before the label
        self._header_layout.insertWidget(0, self._header_icon_widget, 0, Qt.AlignVCenter)

    def clearHeaderIcon(self):
        """Remove the header icon, leaving text-only."""
        if self._header_icon_widget is not None and self._header_layout is not None:
            self._header_layout.removeWidget(self._header_icon_widget)
            self._header_icon_widget.deleteLater()
            self._header_icon_widget = None

    @property
    def headerIcon(self) -> QWidget | None:
        """Direct access to the header's icon widget, if any."""
        return self._header_icon_widget

    # ── Card Type Management ─────────────────────────────────────────────────────────────────
    def setCardType(self, card_type: str):
        """Set the card type for styling."""
        self._card_type = card_type
        self.setProperty("card", card_type)

        # Force style refresh
        self.style().unpolish(self)
        self.style().polish(self)

    def getCardType(self) -> str:
        """Get the current card type."""
        return self._card_type

    # ── Subheader Management ─────────────────────────────────────────────────────────────────
    def setSubheader(self, text: str):
        """Set or update the subheader text.

        The subheader will be inserted directly below the header if one exists,
        or at the top of the card if no header is present.

        Args:
            text: Subheader text to display.
        """
        if self._subheader_label is None:
            # Create subheader label
            self._subheader_label = QLabel(text)
            self._subheader_label.setObjectName("SubHeader")
            
            # Determine insertion position
            insert_index = 0
            if self._header_container is not None:
                # Insert after header
                insert_index = 1
            
            # Insert into main layout
            if self._current_layout:
                self._current_layout.insertWidget(insert_index, self._subheader_label)
        else:
            # Update existing subheader text
            self._subheader_label.setText(text)

    def clearSubheader(self):
        """Remove the subheader if it exists."""
        if self._subheader_label is not None and self._current_layout is not None:
            self._current_layout.removeWidget(self._subheader_label)
            self._subheader_label.deleteLater()
            self._subheader_label = None

    def getSubheader(self) -> str | None:
        """Get the current subheader text.

        Returns:
            The subheader text if set, None otherwise.
        """
        return self._subheader_label.text() if self._subheader_label else None

