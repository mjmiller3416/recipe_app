"""app/theme_manager/icon/ct_tool_button.py

Defines the Custom-Themed ToolButton class, a QToolButton subclass with theme-aware dynamic SVG icon states.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QToolButton

from app.theme_manager.icon.mixin import IconMixin
from app.theme_manager.icon.state import IconState
from app.theme_manager.icon.loader import IconLoader

from app.theme_manager.icon.config import Name, Size, Type

# ── Class Definition ────────────────────────────────────────────────────────────
class ToolButton(QToolButton, IconMixin):
    def __init__(
        self,
        icon_name: Name,
        icon_size: Size = Size.MEDIUM,
        button_size: QSize = None,
        icon_type: Type = Type.TBTN,
        checkable: bool = False,
        hover_effects: bool = True,
        parent=None
    ):
        """
        Initializes a ToolButton instance using enum-driven icon config.

        Args:
            icon_name (Name): Enum representing the icon.
            icon_size (Size): Enum for icon dimensions.
            button_size (QSize, optional): Fixed button size. If None, auto-sized to icon.
            icon_type (Type): Enum for icon color behavior.
            checkable (bool): Whether the button is checkable.
            hover_effects (bool): Apply hover/checked icon states.
            parent: QWidget parent.
        """
        super().__init__(parent)
        self.setObjectName(icon_name.value)
        self.setCheckable(checkable)

        # ── Apply hover/checked/disabled states ──
        if hover_effects and icon_type != Type.STATIC:
            IconState.recolor(
                button=self,
                icon_path=icon_name.path,
                size=icon_size.value,
                variant=icon_type.state_map
            )

        # ── Apply default icon ──
        self._init_themed_icon(icon_name, icon_size, icon_type)

        # ── Set size ──
        if button_size is not None:
            self.setFixedSize(button_size)
        else:
            icon_px = icon_size.value
            self.setFixedSize(icon_px.width(), icon_px.height())

        # ── Register for theme updates ──
        IconLoader.register(self)

    def set_icon_size(self, icon_size: QSize):
        """
        Dynamically update the icon size and refresh the icon rendering.

        Args:
            icon_size (QSize): New icon size.
        """
        self.setIconSize(icon_size)
        self._icon_size = icon_size
        self.update()
