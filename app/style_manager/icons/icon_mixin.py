"""Module providing IconMixin for theme-aware button icons.

IconMixin adds support for themed SVG icons on QAbstractButton widgets
such as QPushButton and QToolButton. It applies and updates icons based
on theme changes.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from pathlib import Path
from PySide6.QtCore import QSize
from app.style_manager.icons.icon_factory import IconFactory


# ── Class Definition ─────────────────────────────────────────────────────────────────────────
class IconMixin:
    def _init_themed_icon(
        self,
        icon_path: Path,
        size: QSize,
        variant: str = "DEFAULT"
    ) -> None:
        """Apply themed SVG icon to this button."""
        self._icon_path = icon_path
        self._icon_size = size
        self._icon_variant = variant

        themed_icon = IconFactory(icon_path, size, variant)
        self.setIcon(themed_icon.icon())
        self.setIconSize(size)

    # ── Public Methods ───────────────────────────────────────────────────────────────────────
    def refresh_theme_icon(self, palette: dict) -> None:
        """
        Applies the current theme palette to the icon.
        Should be implemented by subclasses if needed.
        """
        if hasattr(self, "_themed_icon") and self._themed_icon:
            self._themed_icon.refresh(palette)

    def refresh_theme(self, palette: dict) -> None:
        """
        Protocol-compliant wrapper for refresh_theme_icon.
        Used by IconLoader to trigger icon repaints.
        """
        self.refresh_theme_icon(palette)
