"""app/ui/components/widgets/button/tool_button.py

Module providing ToolButton widget with theme-aware icons.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from PySide6.QtWidgets import QToolButton
from app.theme_manager.icon.config import AppIcon
from app.theme_manager.icon.mixin import IconMixin

# ── Tool Button ──────────────────────────────────────────────────────────────────────────────
class ToolButton(QToolButton, IconMixin):
    def __init__(
        self,
        icon_enum: AppIcon,
        checkable: bool = False,
        parent=None
    ):
        """
        A theme-aware QToolButton with dynamic, stateful icons.

        Args:
            icon_enum (AppIcon): The AppIcon enum member specifying the icon.
            checkable (bool): Whether the button is checkable.
            parent: QWidget parent.
        """
        super().__init__(parent)
        self.setObjectName(icon_enum.spec.name.value)
        self.setCheckable(checkable)

        # This single call initializes all icon logic and registers for theme updates.
        self.init_icon(icon_enum)
