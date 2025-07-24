"""app/theme_manager/icon/mixin.py

Module providing IconMixin for theme-aware button icons.

IconMixin adds support for themed SVG icons on QAbstractButton widgets
such as QPushButton and QToolButton. It applies and updates icons based
on theme changes.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from app.theme_manager.icon.config import Name, Size, Type
from .factory import IconFactory


# ── Class Definition ─────────────────────────────────────────────────────────────────────────
class IconMixin:
    def _init_themed_icon(
        self,
        icon_name: Name,
        icon_size: Size,
        icon_type: Type = Type.DEFAULT
    ) -> None:
        """Apply themed SVG icon to this button using enum-based config."""
        self._icon_name = icon_name
        self._icon_size = icon_size
        self._icon_type = icon_type

        self._themed_icon = IconFactory(icon_name, icon_size, icon_type)
        self.setIcon(self._themed_icon.icon())
        self.setIconSize(icon_size.value)

    # ── Public Methods ───────────────────────────────────────────────────────────────────────
    def refresh_theme_icon(self, palette: dict) -> None:
        """
        Applies the current theme palette to the icon.
        Used when the theme is updated dynamically.
        """
        if hasattr(self, "_themed_icon") and self._themed_icon:
            self._themed_icon.palette = palette
            self.setIcon(self._themed_icon.icon())
            self.setIconSize(self._icon_size.value)

    def refresh_theme(self, palette: dict) -> None:
        """
        Protocol-compliant wrapper for refresh_theme_icon.
        Used by IconLoader to trigger icon repaints.
        """
        self.refresh_theme_icon(palette)
