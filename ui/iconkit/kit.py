"""ui/iconkit/kit.py

Provides IconKit utilities for generating multiple themed QIcons from SVG files.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon

from config import AppPaths
from core.helpers import DebugLogger
from ui.iconkit.loader import SVGLoader


# ── Class Definition ────────────────────────────────────────────────────────────
class IconKit:
    """
    Generates themed QIcons for button states (default, hover, checked).
    Used primarily by hover effect handlers.
    """

    @staticmethod
    def make_icons(
        file_name: str,
        size: QSize,
        default_color: str,
        hover_color: str,
        checked_color: str,
        source: str = "#000",
    ) -> tuple[QIcon, QIcon, QIcon]:
        """
        Generate QIcons for default, hover, and checked states from an SVG file.

        Args:
            file_name (str): Name of the SVG file in the icon directory.
            size (QSize): Size of the icons.
            default_color (str): Default state color.
            hover_color (str): Hover state color.
            checked_color (str): Checked state color.
            source (str): The color in the SVG to be replaced (default is "#000").

        Returns:
            tuple[QIcon, QIcon, QIcon]: Icons for default, hover, and checked states.
        """
        resolved_path = AppPaths.ICONS_DIR / file_name
        if not resolved_path.exists():
            DebugLogger.log(f"Icon path for '{file_name}' could not be resolved.", "error")

        return (
            SVGLoader.load(resolved_path, default_color, size, source, as_icon=True),
            SVGLoader.load(resolved_path, hover_color,   size, source, as_icon=True),
            SVGLoader.load(resolved_path, checked_color, size, source, as_icon=True),
        )
