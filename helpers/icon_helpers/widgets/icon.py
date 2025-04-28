"""helpers/icon_helpers/widgets/icon_label.py

Defines the Icon class, a QLabel subclass for displaying SVG icons with dynamic color support.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QLabel

from core.application.config import ICON_COLOR
from core.helpers.debug_logger import DebugLogger

from ..loader import SVGLoader, icon_path

# ── Class Definition ────────────────────────────────────────────────────────────
class Icon(QLabel):
    """A QLabel subclass that displays an SVG icon with color and size customization.

    Automatically loads the SVG and centers it within the label.
    """

    def __init__(
        self,
        name:   str,
        size:   QSize,
        color:  str = ICON_COLOR,
        source: str = "#000",
        parent=None
    ):
        """Initialize the Icon with the specified SVG, color, and size.

        Args:
            name (str): Name of the SVG file with extension (e.g., "icon.svg").
            size (QSize): Desired icon size.
            color (str, optional): Color to apply to the SVG. Defaults to ICON_COLOR.
            source (str, optional): Source color of the original SVG for color replacement. Defaults to "#000".
            parent (QWidget, optional): Parent widget.
        """
        super().__init__(parent)

        # ── Resolve SVG Path ──
        full_path = icon_path(name)
        if not full_path:
            DebugLogger.log(f"Icon path for '{name}' could not be resolved.", "error")
            return

        # ── Load SVG Icon ──
        pix = SVGLoader.load(full_path, color, size, source, as_icon=False)

        # ── Set Icon Properties ──
        self.setPixmap(pix)
        self.setAlignment(Qt.AlignCenter)
        self.setContentsMargins(0,0,0,0)
        self.setStyleSheet("background:transparent;")
