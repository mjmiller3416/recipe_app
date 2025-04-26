# core/helpers/icons/factory.py

#🔸Third-party
from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon

#🔸Local Imports
from core.helpers.debug_logger import DebugLogger

from .loader import SVGLoader, icon_path

# ────────────────────────────────────────────────────────────────────────────────


class IconFactory:
    """Produce (default, hover, checked) QIcons for any named SVG."""
    @staticmethod
    def make_icons(
        path: str,
        size: QSize,
        default_color: str,
        hover_color:   str,
        checked_color: str,
        source: str = "#000",
    ) -> tuple[QIcon, QIcon, QIcon]:
        
        resolved_path = icon_path(path)
        if not resolved_path:
            DebugLogger.log(f"Icon path for '{path}' could not be resolved.", "error")

        return (
            SVGLoader.load(resolved_path, default_color, size, source, as_icon=True),
            SVGLoader.load(resolved_path, hover_color,   size, source, as_icon=True),
            SVGLoader.load(resolved_path, checked_color, size, source, as_icon=True),
        )