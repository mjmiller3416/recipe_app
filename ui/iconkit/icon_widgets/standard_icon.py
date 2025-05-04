"""ui/iconkit/icon_widgets/standard_icon.py

Defines the StandardIcon class, a QLabel subclass for displaying SVG icons with dynamic color support.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize
from ui.iconkit.base_icon import BaseIcon

# ── Class Definition ────────────────────────────────────────────────────────────
class StandardIcon(BaseIcon):
    """A flat, non-interactive icon – inherits everything from BaseIcon."""
    def __init__(
            self, 
            file_name: str, 
            size: QSize, 
            variant: str = "default",
            parent=None
    ) -> None:
        """
        Initialize the StandardIcon with a file path, size, and optional parent widget.
        
        Args:
            file_path (str): Path to the SVG file.
            size (QSize): Size of the icon.
            variant (str): Variant of the icon. Defaults to "default".
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(file_name, size, variant, parent)

