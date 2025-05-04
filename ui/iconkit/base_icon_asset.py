""" ui/iconkit/base_icon_asset.py

Non-widget base class for retrieving themed QIcon/QPixmap assets.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon, QPixmap

from core.controllers.icon_controller import IconController
from ui.iconkit.factory import IconFactory

# ── Class Definition ────────────────────────────────────────────────────────────
class BaseIconAsset:
    """A non-widget class to generate a themed QIcon or QPixmap on demand."""

    def __init__(
            self, 
            file_name: str, 
            size: QSize,
            variant: str = "default"
        ) -> None:
        """
        Initialize the BaseIconAsset with a file name and size.
        
        Args:
            file_name (str): The name of the icon file.
            size (QSize): The size of the icon.
        """
        self.file_name = file_name
        self.size = size
        self.variant = variant

    def get_icon(self) -> QIcon:
        return IconFactory.make_single_icon(
            file_name=self.file_name,
            size=self.size,
            variant=self.variant
        )

    def get_pixmap(self) -> QPixmap:
        """Return a QPixmap version of the icon."""
        return self.get_icon().pixmap(self.size)
