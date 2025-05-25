"""core/controllers/icon_controller.py

Central registry that recolors every theme-aware icon when the palette flips.
"""

from typing import Dict
# ── Imports ────────────────────────────────────────────────────────────────
from weakref import WeakSet

from PySide6.QtCore import QObject, Signal

from theme_loader import ThemeController
from core.helpers.debug_logger import DebugLogger
from theme_loader.utils import SingletonMixin
from core.helpers.types import ThemedIcon


# ── Class Definition ────────────────────────────────────────────────────────
class IconController(QObject, SingletonMixin):
    """Singleton that stores the active palette and refreshes all registered
    icons when ThemeController broadcasts a change."""

    def __init__(self) -> None:
        super().__init__()             # SingletonMixin

        self._icons: WeakSet[ThemedIcon] = WeakSet()

        tc = ThemeController()
        self._palette: Dict = tc.get_current_palette()
        tc.theme_changed.connect(self._on_theme_changed)

    # ── Public Methods ──────────────────────────────────────────────────────────────
    def register(self, icon: ThemedIcon) -> None:
        """Track a theme-aware icon and paint it immediately."""
        if icon not in self._icons:
            self._icons.add(icon)
            #DebugLogger.log(f"🟢 Icon registered: {icon.objectName()}", "debug")
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

        for icon in tuple(self._icons):          # tuple() guards against GC
            icon.refresh_theme(new_palette)

    @property
    def palette(self) -> Dict:
        """Get the current active color palette."""
        return self._palette