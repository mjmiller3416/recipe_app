"""ui/iconkit/themed_icon.py

Provides ThemedIcon, a utility class for generating themed icons (QIcon/QPixmap) from SVG files.
Supports flexible color variants via:
  - direct color dictionaries
  - hex strings
  - named theme keys referencing ICON_STYLES.
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

    Args:
        file_path (Path): SVG file path relative to the icon directory.
        size (QSize): Desired logical size of the icon.
        variant (str | dict): Color styling source:
            - dict: contains keys like 'DEFAULT', 'HOVER', etc.
            - str (hex): direct hex color like '#6AD7CA'
            - str (named style): maps to a variant in ICON_STYLES
    """

    def __init__(self, file_path: Path, size: QSize, variant: str | dict = "DEFAULT"):
        self.file_path = file_path
        self.size = size
        self.variant = variant
        self.palette = IconController().palette

    def icon_for_state(self, state: str = "DEFAULT") -> QIcon:
        """Returns a themed QIcon for a specific state (e.g., 'HOVER', 'CHECKED')."""
        return SVGLoader.load(
            file_path=self.file_path,
            color=self.resolve_color(state),
            size=self.size,
            as_icon=True
        )

    def icon(self) -> QIcon:
        """Returns the default themed QIcon."""
        return SVGLoader.load(
            file_path=self.file_path,
            color=self.resolve_color("DEFAULT"),
            size=self.size,
            as_icon=True
        )

    def pixmap(self) -> QPixmap:
        """Returns the default themed QPixmap."""
        return SVGLoader.load(
            file_path=self.file_path,
            color=self.resolve_color("DEFAULT"),
            size=self.size,
            as_icon=False
        )

    def resolve_color(self, state: str = "DEFAULT") -> str:
        """
        Resolves a color hex code based on the variant type.

        Supports:
            - Direct color dicts (e.g. {"DEFAULT": "#AAA", "HOVER": "#BBB"})
            - Direct hex color (e.g. "#6AD7CA")
            - Named theme variant mapped from ICON_STYLES
        """

        # Case 1: Variant is a color dict
        if isinstance(self.variant, dict):
            return self.variant.get(state, self.variant.get("DEFAULT", "#FFFFFF"))

        # Case 2: Variant is a direct hex color
        if isinstance(self.variant, str) and self.variant.startswith("#"):
            return self.variant

        # Case 3: Variant is a string key into ICON_STYLES
        style_map = self.palette.get("ICON_STYLES", {})
        variant_map = style_map.get(self.variant, {})

        theme_key_or_color = variant_map.get(state) or variant_map.get("DEFAULT")
        if not theme_key_or_color:
            return "#FFFFFF"

        if isinstance(theme_key_or_color, str) and theme_key_or_color.startswith("#"):
            return theme_key_or_color

        return self.palette.get(theme_key_or_color, "#FFFFFF")

    def __repr__(self) -> str:
        return f"<ThemedIcon path='{self.file_path.name}' variant='{self.variant}'>"
