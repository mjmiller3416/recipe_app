# ui\widgets\utilities\icon_mixin.py
"""
Mixin to apply a themed icon to QAbstractButton widgets (QPushButton, QToolButton).
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize

from ui.tools import ThemedIcon


# ── Class Definition ────────────────────────────────────────────────────────────
class IconMixin:
    def _init_themed_icon(
        self,
        file_name: str,
        size: QSize,
        variant: str = "default"
    ):
        """Apply themed icon to this button using ThemedIcon loader."""
        self._icon_file = file_name
        self._icon_size = size
        self._icon_variant = variant

        themed_icon = ThemedIcon(file_name, size, variant)
        self.setIcon(themed_icon.icon())
        self.setIconSize(size)

    # ── Public Methods ──────────────────────────────────────────────────────────────
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