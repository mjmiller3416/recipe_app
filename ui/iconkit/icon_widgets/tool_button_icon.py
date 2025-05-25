"""ui/iconkit/icon_widgets/tool_button_icon.py

Defines the ToolButtonIcon class, a QToolButton subclass with theme-aware dynamic SVG icon states.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QToolButton

from config import ICON_SIZE
from theme_loader import IconController
from ui.iconkit.effects import ApplyHoverEffects
from ui.iconkit.icon_mixin import IconMixin


# ── Class Definition ────────────────────────────────────────────────────────────
class ToolButtonIcon(QToolButton, IconMixin):
    def __init__(
        self,
        file_path: Path,
        size: QSize = ICON_SIZE,
        variant: str = "default",
        object_name: str = "",
        checkable: bool = False,
        hover_effects: bool = True,
        parent=None
    ):
        """
        Initializes a ToolButtonIcon instance.

        Args:
            file_path (str): The path to the SVG icon file.
            size (QSize): The size of the icon. Defaults to ICON_SIZE.
            variant (str, optional): The variant of the icon. Defaults to "default".
            object_name (str, optional): The object name for the widget. Defaults to "".
            checked (bool, optional): Whether the button is checked. Defaults to False.
            hover_effects (bool, optional): Whether to apply hover effects. Defaults to True.
            parent: The parent widget. Defaults to None.
        """
        super().__init__(parent)

        if object_name:
            self.setObjectName(object_name)
        elif not self.objectName():
            self.setObjectName(Path(file_path).stem)

        self.setCheckable(checkable)
  

        if hover_effects:
            ApplyHoverEffects.recolor(self, file_path, size, variant)

        self._init_themed_icon(file_path, size, variant)

        # ── Register with IconController ──
        IconController().register(self)
    
    def set_icon_size(self, size: QSize):
        """
        Dynamically update the icon size and refresh the icon rendering.

        Args:
            size (QSize): New size for the icon.
        """
        self.setIconSize(size)      
        self._icon_size = size        
        self.update()                  