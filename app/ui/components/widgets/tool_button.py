"""app/ui/components/widgets/button/tool_button.py

Module providing ToolButton widget with theme-aware icons.
"""

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
        parent=None
    ):
        """
        A theme-aware QToolButton with dynamic, stateful icons.

        Args:
            icon_enum (Name): The Name enum member specifying the icon.
            checkable (bool): Whether the button is checkable.
            type (Type): The button type (e.g., default, primary, etc.).
            parent: QWidget parent.
        """
        super().__init__(parent)
        self.setObjectName(icon.spec.name.value)
        self.setCheckable(checkable)

        # this single call initializes all icon logic and registers for theme updates.
        self.init_icon(icon, type)
