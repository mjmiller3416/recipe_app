""" ui/iconkit/icon_widgets/base_icon.py

Base class for all icon widgets.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QLabel
from core.controllers.icon_controller import IconController
from ui.iconkit.factory import IconFactory

# ── Class Definition ────────────────────────────────────────────────────────────
class BaseIcon(QLabel):
    def __init__(
            self, 
            file_name: str, 
            size: QSize, 
            variant: str = "default", 
            parent=None
    ) -> None:
        """
        Initialize the icon with a file name, size, and variant.
        
        Args:
            file_name (str): The name of the SVG file.
            size (QSize): The size of the icon.
            variant (str, optional): The variant of the icon. Defaults to "default".
            parent: Parent widget.
        """
        super().__init__(parent)
        self.file_name = file_name            
        self.size      = size     
        self.variant   = variant               

        self.setFixedSize(self.size)           
        self.setScaledContents(True) 

        IconController().register(self) # auto-tracks this widget          
        self.refresh_theme(IconController().palette)

    # ── Public Methods ──────────────────────────────────────────────────────────────
    def refresh_theme(self, palette: dict) -> None:
        """
        Refresh the icon theme based on the provided palette.
        
        Args:
            palette (dict): The color palette to apply.
        """
        icon = IconFactory.make_single_icon(
            file_name =self.file_name,
            size=self.size,
            variant=self.variant
        )
        self.setPixmap(icon.pixmap(self.size))

