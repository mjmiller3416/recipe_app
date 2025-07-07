"""Module providing IconFactory for generating themed icons.

IconFactory creates theme-aware QIcons and QPixmaps from SVG files by
applying color variants based on the current theme.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from typing import Dict
from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon, QPixmap

from app.style_manager.icons.icon_loader import IconLoader
from app.style_manager.icons.svg_loader import SVGLoader


from app.style_manager.icons.base import ThemedIcon

# ── Themed Icon ──────────────────────────────────────────────────────────────────────────────
class IconFactory:
    """Creates a themed QIcon or QPixmap from an SVG file."""

    def __init__(self, file_path: Path, size: QSize, variant: str | dict = "DEFAULT"):
        """
        Initializes a ThemedIcon instance.

        Args:
            file_path (Path): Path to the SVG file.
            size (QSize): Desired size for the icon.
            variant (str | dict): Color variant for the icon.
        """
        self.file_path = file_path
        self.size = size
        if isinstance(variant, str):
            self.variant = variant.upper()
        else:
            self.variant = variant
        self.palette = IconLoader().palette

    def icon_for_state(self, state: str = "DEFAULT") -> QIcon:
        """
        Returns a themed QIcon for a specific state (e.g., 'HOVER', 'CHECKED').

        Args:
            state (str): The state for which to resolve the icon color.
                         Defaults to 'DEFAULT'.

        Returns:
            QIcon: Themed QIcon for the specified state.
        """
        state = state.upper()
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

        state = state.upper()
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
        """Returns a string representation of the ThemedIcon instance."""
        return f"<ThemedIcon path='{self.file_path.name}' variant='{self.variant}'>"
