"""app/ui/components/widgets/button/tool_button.py

Module providing ToolButton widget with theme-aware icons.
"""

from PySide6.QtCore import QSize
# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from PySide6.QtWidgets import QToolButton

from app.theme_manager.icon.config import Name, Type
from app.theme_manager.icon.mixin import IconMixin


# ── Tool Button ──────────────────────────────────────────────────────────────────────────────
class ToolButton(QToolButton, IconMixin):
    def __init__(
        self,
        icon: Name,
        type: Type = Type.DEFAULT,
        checkable: bool = False,
        button_size: QSize = None,
        icon_size: QSize = None,
        parent=None
    ):
        """
        A theme-aware QToolButton with dynamic, stateful icons.

        Args:
            icon (Name): The Name enum member specifying the icon.
            checkable (bool): Whether the button is checkable.
            type (Type): The button type (e.g., default, primary, etc.).
            button_size (QSize): Custom button size. If None, uses default size.
            icon_size (QSize): Custom icon size. If None, uses icon's default size.
            parent: QWidget parent.
        """
        super().__init__(parent)
        self.setObjectName(icon.spec.name.value)
        self.setCheckable(checkable)

        # store sizes for access
        self._button_size = button_size
        self._custom_icon_size = icon_size


        # set custom button size if specified
        if button_size:
            self.setFixedSize(button_size)

        # initialize icon logic
        self.init_icon(icon, type)

        # set custom icon size if specified (must be after init_icon)
        if icon_size:
            self.setIconSize(icon_size)

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
