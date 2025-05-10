"""ui/iconkit/themed_icon.py

Provides ThemedIcon a utility class for generating themed icons (QIcon/QPixmap) from SVG files.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon, QPixmap

from core.controllers.icon_controller import IconController
from ui.iconkit.loader import SVGLoader


# ── Class Definition ────────────────────────────────────────────────────────────
class ThemedIcon:
    """
    Creates a themed QIcon or QPixmap from an SVG file, using a color variant from the active theme.
    """

    def __init__(self, file_path: Path, size: QSize, variant: str = "default"):
        """
        Args:
            file_path (Path): SVG file name (relative to icon dir)
            size (QSize): Desired icon size
            variant (str): Variant used in theme's ICON_STYLES (e.g., "default", "nav", etc.)
        """
        self.file_path = file_path
        self.size = size
        self.variant = variant
        self.palette = IconController().palette

    def icon_for_state(self, state: str = "default") -> QIcon:
        """Returns a themed QIcon for the given state (default, hover, checked)."""
        return SVGLoader.load(
            file_path=self.file_path,
            color=self.resolve_color(state),
            size=self.size,
            as_icon=True
        )

    def icon(self) -> QIcon:
        """Returns a themed QIcon"""
        return SVGLoader.load(
            file_path=self.file_path,
            color=self.resolve_color("default"),
            size=self.size,
            as_icon=True
        )

    def pixmap(self) -> QPixmap:
        """Returns a themed QPixmap"""
        return SVGLoader.load(
            file_path=self.file_path,
            color=self.resolve_color("default"),
            size=self.size,
            as_icon=False
        )

    def resolve_color(self, state: str = "default") -> str:
        """
        Resolves a color hex based on the variant type:
        - If variant is a dict, fetch state directly.
        - If variant is a hex color (str), return it directly.
        - If variant is a named theme key, resolve via palette.
        """
        # ── Case 1: Direct color dictionary (e.g., {"normal": "#AAA", "hover": "#BBB"})
        if isinstance(self.variant, dict):
            return self.variant.get(state, "#FFFFFF")

        # ── Case 2: Direct hex string (e.g., "#6AD7CA")
        if isinstance(self.variant, str) and self.variant.startswith("#"):
            return self.variant

        # ── Case 3: Themed variant (e.g., "default", "sidebar")
        style_map = self.palette.get("ICON_STYLES", {})
        variant_map = style_map.get(self.variant, {})
        theme_key = variant_map.get(state, "ICONS.DEFAULT.DEFAULT")
        return self.palette.get(theme_key, "#FFFFFF")
