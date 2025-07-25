"""app/ui/components/widgets/button/button.py

Module providing Button widget with theme-aware icons.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from PySide6.QtWidgets import QPushButton
from app.theme_manager.icon.config import Name, Type
from app.theme_manager.icon.mixin import IconMixin

# ── Button ───────────────────────────────────────────────────────────────────────────────────
class Button(QPushButton, IconMixin):
    def __init__(
        self,
        icon: Name,
        type: Type = Type.DEFAULT,
        label: str = "",
        checkable: bool = False,
        parent=None
    ):
        """
        A theme-aware QPushButton with dynamic, stateful icons.

        Args:
            icon (Name): The Name enum member specifying the icon.
            label (str): Optional text label.
            checkable (bool): Whether the button is checkable.
            type (Type): The button type (e.g., default, primary, etc.).
            parent: Optional QWidget parent.
        """
        super().__init__(label, parent)
        self.setCheckable(checkable)

        # this single call initializes all icon logic and registers for theme updates.
        self.init_icon(icon, type)
