"""app/ui/components/widgets/button/button.py

Module providing Button widget with theme-aware icons.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QPushButton

from app.theme_manager.icon.config import Name, Type
from app.theme_manager.icon.mixin import IconMixin

# ── Button ───────────────────────────────────────────────────────────────────────────────────
class Button(QPushButton, IconMixin):
    def __init__(
        self,
        type: Type = Type.DEFAULT,
        label: str = "",
        parent=None
    ):
        """
        A theme-aware QPushButton with dynamic, stateful icons.

        Args:
            type (Type): The button type (e.g., default, primary, etc.).
            label (str): Optional text label.
            parent: Optional QWidget parent.
        """
        super().__init__(label, parent)

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
            # disconnect first to avoid duplicate connections
            try:
                self.toggled.disconnect(self._update_icon)
            except TypeError:
                pass  # signal wasn't connected - which is fine
            self.toggled.connect(self._update_icon)

    def setIcon(self, icon_name: Name):
        """
        Set the icon for this button.

        Args:
            icon_name (Name): The Name enum member specifying the icon.
        """
        super().setIcon(icon_name)
