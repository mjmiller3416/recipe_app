"""core/helpers/icon_helpers/factory.py

Provides the IconFactory class for generating QIcons with dynamic color variants (default, hover, checked).
"""


# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon

from config import AppPaths 
from core.helpers import DebugLogger
from .loader import SVGLoader
from core.controllers.icon_controller import IconController

# ── Class Definition ────────────────────────────────────────────────────────────
class IconFactory:
    """Provides static methods to generate QIcons for different button states.

    Produces default, hover, and checked color variants for a given SVG asset.
    """
    @staticmethod
    def make_single_icon(file_name: str, size: QSize, variant: str = "default") -> QIcon:
        from core.controllers.icon_controller import IconController

        palette = IconController().palette
        styles = palette.get("ICON_STYLES", {})

        # NEW: Check if the style is a dict (style set) or a direct color key
        style = styles.get(variant, "ICON_COLOR")
        if isinstance(style, dict):
            default_key = style.get("default", "ICON_COLOR")
        else:
            default_key = style

        effective_color = palette.get(default_key, "#FFFFFF")

        return SVGLoader.load(
            AppPaths.ICONS_DIR / file_name,
            effective_color,
            size,
            source="#000",
            as_icon=True
        )

    @staticmethod
    def make_icons(
        file_name: str,
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
        resolved_path = AppPaths.ICONS_DIR / file_name
        if not resolved_path.exists():
            DebugLogger.log(f"Icon path for '{file_name}' could not be resolved.", "error")

        # ── Load Icon ──
        return (
            SVGLoader.load(resolved_path, default_color, size, source, as_icon=True),
            SVGLoader.load(resolved_path, hover_color,   size, source, as_icon=True),
            SVGLoader.load(resolved_path, checked_color, size, source, as_icon=True),
        )
