"""app/ui/widgets/ct_tool_button.py

Defines the Custom-Themed ToolButton class, a QToolButton subclass with theme-aware dynamic SVG icon states.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QToolButton

from app.config import ICON_SIZE
from app.style_manager import IconLoader

from .helpers import ButtonEffects, IconMixin

# ── Constants ───────────────────────────────────────────────────────────────────  
PADDING = 4  # Padding around the icon

# ── Class Definition ────────────────────────────────────────────────────────────
class CTToolButton(QToolButton, IconMixin):
    def __init__(
        self,
        file_path: Path,
        icon_size: QSize = ICON_SIZE,
        button_size: QSize = None,  
        padding: int = PADDING,
        variant: str = "default",
        object_name: str = "",
        checkable: bool = False,
        hover_effects: bool = True,
        parent=None
    ):
        """
        Initializes a CTToolButton instance.

        Args:
            file_path (str): The path to the SVG icon file.
            icon_size (QSize): The size of the icon. Defaults to ICON_SIZE.
            button_size (QSize, optional): The fixed size for the button. If None, uses icon size + padding. 
            variant (str, optional): The variant of the icon. Defaults to "default".
            object_name (str, optional): The object name for the widget. Defaults to "".
            checked (bool, optional): Whether the button is checked. Defaults to False.
            hover_effects (bool, optional): Whether to apply hover effects. Defaults to True.
            text (str, optional): The button label text. Defaults to empty string.
            parent: The parent widget. Defaults to None.
        """
        super().__init__(parent)

        if object_name:
            self.setObjectName(object_name)
        elif not self.objectName():
            self.setObjectName(Path(file_path).stem)

        self.setCheckable(checkable)
        self.button_size = button_size
  
        if hover_effects:
            ButtonEffects.recolor(self, file_path, icon_size, variant)

        self._init_themed_icon(file_path, icon_size, variant)
        # Set fixed icon_size for the button, using button_size if provided
        if button_size is not None:
            self.setFixedSize(button_size)
        else:
            self.setFixedSize(icon_size.width() + padding, icon_size.height())

        # ── Register with IconLoader ──
        IconLoader().register(self)
    
    def set_icon_size(self, icon_size: QSize):
        """
        Dynamically update the icon icon_size and refresh the icon rendering.

        Args:
            size (QSize): New size for the icon.
        """
        self.setIconSize(icon_size)      
        self._icon_size = icon_size        
        self.update()