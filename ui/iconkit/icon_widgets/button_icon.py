"""ui/iconkit/icon_widgets/button_icon.py

Defines the ButtonIcon class, a QPushButton subclass with theme-aware dynamic SVG icon states.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QPushButton

from config import ICON_SIZE
from style_manager import IconLoader
from ui.iconkit.effects import ApplyHoverEffects
from ui.iconkit.icon_mixin import IconMixin


# ── Class Definition ────────────────────────────────────────────────────────────
class ButtonIcon(QPushButton, IconMixin):
    def __init__(
        self,
        file_path: Path,
        size: QSize = ICON_SIZE,
        variant: str = "default",
        label: str = "",
        object_name: str = "",
        checked: bool = False,
        hover_effects: bool = True,
        parent=None
    ):
        """
        Initializes a ButtonIcon instance.

        Args:
            file_path (str): The path to the SVG icon file.
            size (QSize, optional): The size of the icon. Defaults to ICON_SIZE.
            variant (str, optional): The variant of the icon. Defaults to "default".
            label (str, optional): The text label for the button. Defaults to "".
            object_name (str, optional): The object name for the widget. Defaults to "".
            checked (bool, optional): Whether the button is checked. Defaults to False.
            hover_effects (bool, optional): Whether to apply hover effects. Defaults to True.
            parent: The parent widget. Defaults to None.
        """
        super().__init__(label, parent)

        if object_name:
            self.setObjectName(object_name)
        elif not self.objectName():
            self.setObjectName(Path(file_path).stem)

        self.setCheckable(True)
        self.setChecked(checked)

        if hover_effects:
            ApplyHoverEffects.recolor(self, file_path, size, variant)
        
        self._init_themed_icon(file_path, size, variant)

        # ── Register with IconLoader ──
        IconLoader().register(self)
