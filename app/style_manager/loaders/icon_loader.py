"""style_manager/loaders/icon_loader.py

Central registry that recolors every theme-aware icon when the palette flips.
"""

# ── Imports ────────────────────────────────────────────────────────────────
from typing import Dict
from weakref import WeakSet

from PySide6.QtCore import QObject, Signal

from app.core.utils import DebugLogger
from app.style_manager.theme_controller import ThemeController
from app.ui.helpers import SingletonMixin
from app.ui.helpers.types import ThemedIcon


# ── Class Definition ────────────────────────────────────────────────────────
class IconLoader(QObject, SingletonMixin):
    """Singleton that stores the active palette and refreshes all registered
    icons when ThemeController broadcasts a change."""

    def __init__(self) -> None:
        super().__init__()

        self._icons: WeakSet[ThemedIcon] = WeakSet()

        tc = ThemeController()
        self._palette: Dict = tc.get_current_palette()
        tc.theme_changed.connect(self._on_theme_changed)

    # ── Public Methods ──────────────────────────────────────────────────────────────
    def register(self, icon: ThemedIcon) -> None:
        """Track a theme-aware icon and paint it immediately."""
        if icon not in self._icons:
            self._icons.add(icon)
            icon.refresh_theme(self._palette)

    def unregister(self, icon: ThemedIcon) -> None:
        if icon in self._icons:
            self._icons.remove(icon)
            DebugLogger.log(f"🟡 Icon unregistered: {icon.objectName()}", "debug")

    # ── Private Methods ─────────────────────────────────────────────────────────────
    def _on_theme_changed(self, new_palette: Dict) -> None:
        """Slot → emits from ThemeController."""
        self._palette = new_palette
        DebugLogger.log(f"🔁 Refreshing {len(self._icons)} icons", "info")

        for icon in tuple(self._icons):  
            icon.refresh_theme(new_palette)

    @property
    def palette(self) -> Dict:
        """Get the current active color palette."""
        return self._palette