"""app/ui/components/widgets/button/tool_button.py

Module providing ToolButton widget with theme-aware icons.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QEvent, QSize
from PySide6.QtWidgets import QToolButton

from app.theme_manager.icon.config import Name, Type
from app.theme_manager.icon.mixin import IconMixin

# ── Tool Button ──────────────────────────────────────────────────────────────────────────────
class ToolButton(QToolButton, IconMixin):
    def __init__(
        self,
        type: Type = Type.DEFAULT,
        parent=None
    ):
        """
        A theme-aware QToolButton with dynamic, stateful icons.

        Args:
            type (Type): The button type (e.g., default, primary, etc.).
            parent: QWidget parent.
        """
        super().__init__(parent)

        # store button type for icon setup
        self._button_type = type

        # store sizes for access
        self._button_size = None
        self._custom_icon_size = None

    def setButtonSize(self, width: int, height: int):
        """
        Set the button size.

        Args:
            width (int): Button width in pixels
            height (int): Button height in pixels
        """
        size = QSize(width, height)
        self._button_size = size
        self.setFixedSize(size)

    def setCustomIconSize(self, width: int, height: int):
        """
        Set the icon size.

        Args:
            width (int): Icon width in pixels
            height (int): Icon height in pixels
        """
        size = QSize(width, height)
        self._custom_icon_size = size
        self.setIconSize(size)

    def setButtonCheckable(self, checkable: bool):
        """
        Set whether the button is checkable.

        Args:
            checkable (bool): True if button should be checkable, False otherwise.
        """
        self.setCheckable(checkable)

        # connect toggled signal to update icon state when checked/unchecked
        if checkable:
            # Only connect if not already connected to avoid duplicates
            if not hasattr(self, '_icon_toggle_connected'):
                self.toggled.connect(self._update_icon)
                self._icon_toggle_connected = True

    def setIcon(self, icon_name: Name):
        """
        Set the icon for this button.

        Args:
            icon_name (Name): The Name enum member specifying the icon.
        """
        self.setIconFromName(icon_name)

    def enterEvent(self, event: QEvent) -> None:
        """Handle mouse enter events for hover icon state."""
        IconMixin.enterEvent(self, event)
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        """Handle mouse leave events to restore default icon state."""
        IconMixin.leaveEvent(self, event)
        super().leaveEvent(event)

    def changeEvent(self, event: QEvent) -> None:
        """Handle change events for enabled/disabled icon state."""
        IconMixin.changeEvent(self, event)
        super().changeEvent(event)
