"""Module providing IconLoader for managing themed icons.

IconLoader is a singleton registry that stores the active theme palette
and refreshes all registered icons when the application theme changes.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from typing import Dict
from weakref import WeakSet

from PySide6.QtCore import QObject

from app.core.utils import SingletonMixin
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.theme_manager.theme_controller import ThemeController
from dev_tools import DebugLogger
from .base import ThemedIcon


# ── Icon Loader ──────────────────────────────────────────────────────────────────────────────
class IconLoader(QObject, SingletonMixin):
    """Singleton to manage and refresh theme-aware icons.

    It stores the active palette and refreshes all registered icons when
    the theme changes.
    """

    def __init__(self) -> None:
        # only initialize once (SingletonMixin still calls __init__ on each instantiation)
        if getattr(self, "_initialized", False):
            return
        super().__init__()
        self._icons: WeakSet[ThemedIcon] = WeakSet()
        # initialize with empty palette to allow early registration before theme is set
        self._palette: Dict = {}
        self._initialized = True

    # ── Properties ───────────────────────────────────────────────────────────────────────────
    @property
    def palette(self) -> Dict:
        """Get the current active color palette."""
        return self._palette

    # ── Public Methods ───────────────────────────────────────────────────────────────────────
    def connect_theme_controller(self, theme_controller: 'ThemeController') -> None:
        """Connects the loader to a ThemeController instance (lazy to avoid circular imports)."""
        # Capture the initial palette and subscribe to future changes
        self._palette = theme_controller.get_current_palette()
        theme_controller.theme_changed.connect(self._on_theme_changed)

        # immediately refresh all icons
        for icon in tuple(self._icons):
            icon.refresh_theme(self._palette)


    def register(self, icon: ThemedIcon) -> None:
        """Track a theme-aware icon and paint it immediately."""
        if icon not in self._icons:
            self._icons.add(icon)
            icon.refresh_theme(self._palette)

    def unregister(self, icon: ThemedIcon) -> None:
        if icon in self._icons:
            self._icons.remove(icon)
            DebugLogger.log(f"Icon unregistered: {icon.objectName()}", "debug")

    # ── Private Methods ──────────────────────────────────────────────────────────────────────
    def _on_theme_changed(self, new_palette: Dict) -> None:
        """Slot → emits from ThemeController."""
        self._palette = new_palette
        DebugLogger.log(f"Refreshing {len(self._icons)} icons", "debug")

        for icon in tuple(self._icons):
            icon.refresh_theme(new_palette)
