""" app/ui/components/layout/card.py

A generic container widget with elevation effects and flexible layout management.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QGridLayout,
    QSizePolicy, QWidget, QLabel, QLayout
)
from typing import Optional

from app.style import Theme, Qss
from app.style.icon import AppIcon, Name
from app.style.effects import Effects, Shadow
from app.ui.components.widgets.button import Button


class Card(QFrame):
    """A generic container widget with elevation effects and flexible layout management.

    This class provides a container that automatically scales based on its contents
    with configurable content margins and elevation effects. Supports multiple
    layout types (QVBox, QHBox, QGrid) and provides a clean API for content management.
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        layout: str = "vbox",
        card_type: str = "Default",
    ):
        """Initialize the Card widget.

        Args:
            parent: Optional parent widget.
            layout: Initial layout type: "vbox" (default), "hbox", or "grid".
            card_type: Card styling type for QSS (default: "Default").
        """
        super().__init__(parent)

        Theme.register_widget(self, Qss.CARD)

        self._card_type = card_type
        self.setObjectName("Card")
        self.setProperty("card", card_type)
        self.setAttribute(Qt.WA_StyledBackground)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        self._current_layout: QLayout | None = None
        self._elevation = Shadow.ELEVATION_6  # Default elevation
        self._elevation_enabled = True

        # Header components
        self._header_container: QWidget | None = None
        self._header_main_layout: QVBoxLayout | None = None
        self._header_row_layout: QHBoxLayout | None = None
        self._header_label: QLabel | None = None
        self._header_icon_widget: QWidget | None = None
        self._subheader_label: QLabel | None = None

        # Footer components
        self._footer_button: Button | None = None
        self._button_alignment = Qt.AlignCenter

        self._add_layout(layout, 20)

        if self._elevation_enabled:
            Effects.apply_shadow(self, self._elevation)

    def _clear_current_layout(self) -> None:
        """Remove all child widgets and delete the current layout."""
        if not self._current_layout:
            return

        while self._current_layout.count():
            if w := self._current_layout.takeAt(0).widget():
                w.setParent(None)
                w.deleteLater()

        self._current_layout.deleteLater()
        self._current_layout = None

    def _add_layout(self, layout_type: str = "vbox", spacing: int = 10):
        """Create/replace the internal layout."""
        self._clear_current_layout()

        layout_map = {
            "hbox": QHBoxLayout,
            "grid": QGridLayout,
            "vbox": QVBoxLayout
        }
        layout_class = layout_map.get(layout_type.strip().lower(), QVBoxLayout)
        self._current_layout = layout_class(self)
        self._current_layout.setContentsMargins(20, 20, 20, 20)
        self._current_layout.setSpacing(spacing)
        return self._current_layout

    def setLayoutType(self, layout_type: str, *, spacing: Optional[int] = None) -> None:
        """Switch between 'vbox' | 'hbox' | 'grid' at runtime."""
        self._add_layout(layout_type, spacing if spacing is not None else 10)
        # Reinsert header and footer if they existed
        if self._header_container and self._current_layout:
            self._current_layout.insertWidget(0, self._header_container)
        if self._footer_button and self._current_layout:
            self._current_layout.addWidget(self._footer_button, 0, self._button_alignment)

    def addWidget(self, widget: QWidget, *args, **kwargs):
        """Add a widget to the current layout.

        For QGridLayout: row, column, rowSpan=1, columnSpan=1
        For QVBoxLayout/QHBoxLayout: stretch=0, alignment=Qt.Alignment()
        """
        if not self._current_layout:
            self._add_layout("vbox")

        if isinstance(self._current_layout, QGridLayout) and len(args) < 2:
            raise ValueError("Grid layout requires at least row and column arguments")
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
        """Get the current layout object."""
        return self._current_layout

    def clearWidgets(self):
        """Clear all widgets from the current layout (excludes header container)."""
        if not self._current_layout:
            return

        widgets_to_remove = [
            item.widget() for i in range(self._current_layout.count())
            if (item := self._current_layout.itemAt(i)) and item.widget()
            and item.widget() is not self._header_container
            and item.widget() is not self._footer_button
        ]

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
        Effects.apply_shadow(self, self._elevation if enabled else Shadow.ELEVATION_0)

    def _set_expansion(self, h_policy, v_policy):
        """Helper to set size policy."""
        self.setSizePolicy(h_policy, v_policy)

    def expandWidth(self, expand: bool = True):
        """Enable or disable width expansion."""
        policy = self.sizePolicy()
        self._set_expansion(
            QSizePolicy.Expanding if expand else QSizePolicy.Preferred,
            policy.verticalPolicy()
        )

    def expandHeight(self, expand: bool = True):
        """Enable or disable height expansion."""
        policy = self.sizePolicy()
        self._set_expansion(
            policy.horizontalPolicy(),
            QSizePolicy.Expanding if expand else QSizePolicy.Preferred
        )

    def expandBoth(self, expand: bool = True):
        """Enable or disable both width and height expansion."""
        policy = QSizePolicy.Expanding if expand else QSizePolicy.Preferred
        self._set_expansion(policy, policy)

    def setFixed(self):
        """Set card to fixed size (content-based)."""
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        return self


    def _ensure_header_container(self):
        """Ensure the header container exists with proper nested layout structure."""
        if self._header_container:
            return

        self._header_container = QWidget(self)
        self._header_container.setAttribute(Qt.WA_StyledBackground, False)
        self._header_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)  # Keep header at top

        self._header_main_layout = QVBoxLayout(self._header_container)
        self._header_main_layout.setContentsMargins(0, 0, 0, 0)
        self._header_main_layout.setSpacing(4)

        self._header_row_layout = QHBoxLayout()
        self._header_row_layout.setContentsMargins(0, 0, 0, 0)
        self._header_row_layout.setSpacing(8)

        self._header_main_layout.addLayout(self._header_row_layout)

        if self._current_layout:
            self._current_layout.insertWidget(0, self._header_container)

    def setHeader(self, text: str, icon: Optional[object] = None):
        """Set or update the header with optional icon.

        Args:
            text: Header text.
            icon: Optional icon (Name enum or QWidget).
        """
        self._ensure_header_container()

        if not self._header_label:
            self._header_label = QLabel(text)
            self._header_label.setObjectName("Header")
            self._header_row_layout.addWidget(self._header_label, 0, Qt.AlignVCenter)
        else:
            self._header_label.setText(text)
            self._refresh_style(self._header_label)

        if icon is not None:
            self.setHeaderIcon(icon)

    def setHeaderIcon(self, icon: object):
        """Set or replace the header's icon.

        Args:
            icon: Name enum (constructs AppIcon) or QWidget.
        """
        self._ensure_header_container()

        if self._header_icon_widget:
            self._header_row_layout.removeWidget(self._header_icon_widget)
            self._header_icon_widget.deleteLater()

        if isinstance(icon, QWidget):
            self._header_icon_widget = icon
        elif Name and hasattr(icon, "spec"):
            if not AppIcon:
                raise ImportError("AppIcon widget not available.")
            self._header_icon_widget = AppIcon(icon)
        else:
            raise TypeError("Unsupported icon type. Pass a Name enum or QWidget.")

        self._header_row_layout.insertWidget(0, self._header_icon_widget, 0, Qt.AlignVCenter)

    @property
    def headerIcon(self) -> QWidget | None:
        """Direct access to the header's icon widget."""
        return self._header_icon_widget


    def setSubHeader(self, text: str):
        """Set or update the subheader text."""
        self._ensure_header_container()

        if not self._subheader_label:
            self._subheader_label = QLabel(text)
            self._subheader_label.setObjectName("SubHeader")
            self._header_main_layout.addWidget(self._subheader_label)
        else:
            self._subheader_label.setText(text)

    def getSubHeader(self) -> str | None:
        """Get the current subheader text."""
        return self._subheader_label.text() if self._subheader_label else None

    def _refresh_style(self, widget):
        """Helper to refresh widget styling."""
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    # ── Footer Button Management ─────────────────────────────────────────────────────────────
    def addButton(self, text: str, button_type=None, icon=None, alignment=Qt.AlignCenter):
        """Add a footer button to the card with alignment control.

        Args:
            text: Button text
            button_type: Button type from Type enum (optional)
            icon: Button icon from Name enum (optional)
            alignment: Button alignment (Qt.AlignLeft, Qt.AlignCenter, Qt.AlignRight)
        """
        from app.style.icon.config import Type

        # Remove existing button if present
        if self._footer_button:
            self.removeButton()

        # Create button with default type if not specified
        if button_type is None:
            button_type = Type.PRIMARY

        self._footer_button = Button(text, button_type, icon)
        self._footer_button.setObjectName("CardFooterButton")
        self._button_alignment = alignment

        # Add to layout with alignment
        if self._current_layout:
            self._current_layout.addWidget(self._footer_button, 0, alignment)

    def removeButton(self):
        """Remove the footer button if it exists."""
        if self._footer_button and self._current_layout:
            self._current_layout.removeWidget(self._footer_button)
            self._footer_button.deleteLater()
            self._footer_button = None

    @property
    def button(self) -> Button | None:
        """Direct access to the footer button widget."""
        return self._footer_button
