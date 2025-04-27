"""core/helpers/icon_helpers/factory.py

Provides the IconFactory class for generating QIcons with dynamic color variants (default, hover, checked).
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon

from core.helpers.debug_logger import DebugLogger
from .loader import SVGLoader, icon_path

# ── Class Definition ────────────────────────────────────────────────────────────
class IconFactory:
    """Provides static methods to generate QIcons for different button states.

    Produces default, hover, and checked color variants for a given SVG asset.
    """
    @staticmethod
    def make_icons(
        path: str,
        size: QSize,
        default_color: str,
        hover_color:   str,
        checked_color: str,
        source: str = "#000",
    ) -> tuple[QIcon, QIcon, QIcon]:
        """Generate QIcons for default, hover, and checked states from an SVG file.

        Args:
            path (str): The name or path of the SVG file.
            size (QSize): Desired size for the icons.
            default_color (str): Color for the default icon.
            hover_color (str): Color for the hover icon.
            checked_color (str): Color for the checked icon.
            source (str, optional): Original color value to replace. Defaults to "#000".

        Returns:
            tuple[QIcon, QIcon, QIcon]: A tuple containing (default_icon, hover_icon, checked_icon).
        """
        # ── Resolve File Path ──
        resolved_path = icon_path(path)
        if not resolved_path:
            DebugLogger.log(f"Icon path for '{path}' could not be resolved.", "error")

        # ── Load Icon ──
        return (
            SVGLoader.load(resolved_path, default_color, size, source, as_icon=True),
            SVGLoader.load(resolved_path, hover_color,   size, source, as_icon=True),
            SVGLoader.load(resolved_path, checked_color, size, source, as_icon=True),
        )
