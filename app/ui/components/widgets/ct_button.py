"""app/ui/widgets/ct_button.py

Defines the Custom-Themed Buttom class, a QPushButton subclass with theme-aware dynamic SVG icon states.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QPushButton

from app.config import ICON_SIZE
from app.style_manager import IconLoader

from app.style_manager.icons import ButtonEffects, IconMixin


# ── Class Definition ────────────────────────────────────────────────────────────
class CTButton(QPushButton, IconMixin):
    def __init__(
        self,
        file_path: Path,
        icon_size: QSize = ICON_SIZE,
        variant: str = "DEFAULT",
        height: int = 55,
        label: str = "",
        checkable: bool = True,
        hover_effects: bool = True,
        parent=None
    ):
        """
        Initializes a CTButton instance.

        Args:
            file_path (str): The path to the SVG icon file.
            size (QSize, optional): The size of the icon. Defaults to ICON_SIZE.
            variant (str, optional): The variant of the icon. Defaults to "DEFAULT".
            label (str, optional): The text label for the button. Defaults to "".
            object_name (str, optional): The object name for the widget. Defaults to "".
            checked (bool, optional): Whether the button is checked. Defaults to False.
            hover_effects (bool, optional): Whether to apply hover effects. Defaults to True.
            parent: The parent widget. Defaults to None.
        """
        super().__init__(label, parent)

        self.setCheckable(checkable)
        self.setFixedHeight(height)

        if hover_effects:
            ButtonEffects.recolor(self, file_path, icon_size, variant)

        self._init_themed_icon(file_path, icon_size, variant)

        # ── Register with IconLoader ──
        IconLoader().register(self)
