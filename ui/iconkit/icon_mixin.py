"""ui/iconkit/icon_mixin.py

Mixin to apply a themed icon to QAbstractButton widgets (QPushButton, QToolButton).
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize

from ui.iconkit.themed_icon import ThemedIcon


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

    def refresh_theme_icon(self):
        """Refreshes the icon using the current theme."""
        themed_icon = ThemedIcon(self._icon_file, self._icon_size, self._icon_variant)
        self.setIcon(themed_icon.icon())
