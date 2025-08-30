"""Module providing IconLoader for managing themed icons.

IconLoader is a singleton registry that stores the active theme palette
and refreshes all registered icons when the application theme changes.
"""

# Protocol for theme-aware icons
# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from typing import Dict, Optional, Protocol
from weakref import WeakSet

from PySide6.QtCore import QObject

from app.core.utils import QSingleton
from app.style.theme_controller import Theme
from _dev_tools import DebugLogger


class ThemedIcon(Protocol):
    """Protocol for any theme-aware icon-like object."""
    def refresh_theme(self, palette: dict[str, str]) -> None: ...
    def objectName(self) -> str: ...


# ── Icon Loader ──────────────────────────────────────────────────────────────────────────────
class IconLoader(QSingleton):
    """Singleton to manage and refresh theme-aware icons.

    It stores the active palette and refreshes all registered icons when
    the theme changes.
    """

    def __init__(self, parent: Optional[QObject] = None) -> None:
        """Initialize the IconLoader."""
        super().__init__(parent)
        self._icons: WeakSet[ThemedIcon] = WeakSet()
        self._palette: Dict = {}
        self._initialized = True

    # ── Private Methods ──────────────────────────────────────────────────────────────────────
    def _initialize_palette(self) -> None:
        """Initialize the color palette for icons."""
        self._palette = Theme.get_current_color_map()

    def _on_theme_refresh(self, new_palette: Dict) -> None:
        """Slot → emits from ThemeController."""
        self._palette = new_palette
        DebugLogger.log(f"Refreshing {len(self._icons)} icons", "debug")

        # Clear SVG cache once before refreshing all icons
        from app.style.icon.svg_loader import SVGLoader
        SVGLoader.clear_cache()

        for icon in tuple(self._icons):
            icon.refresh_theme(new_palette)


    # ── Public Methods ───────────────────────────────────────────────────────────────────────
    @classmethod
    def _get_instance(cls):
        """Get the singleton instance, creating it if necessary."""
        if cls not in cls._instances:
            cls._instances[cls] = cls()  # this properly calls __new__ and __init__
        return cls._instances[cls]

    @classmethod
    def connect_theme_controller(cls, theme: Theme) -> None:
        """Connects the loader to a ThemeController instance."""
        # capture the initial palette and subscribe to future changes
        DebugLogger.log("Connecting IconLoader to ThemeController", "debug")
        instance = cls._get_instance()
        instance._palette = theme.get_current_color_map()
        theme.theme_refresh.connect(instance._on_theme_refresh)

        # Clear cache once and immediately refresh all icons
        from app.style.icon.svg_loader import SVGLoader
        SVGLoader.clear_cache()

        for icon in tuple(instance._icons):
            icon.refresh_theme(instance._palette)

        DebugLogger.log("Initialized IconLoader with palette: {instance._palette}", "debug")

    @classmethod
    def register(cls, icon: ThemedIcon) -> None:
        """Track a theme-aware icon and paint it immediately."""
        instance = cls._get_instance()
        if icon not in instance._icons:
            instance._icons.add(icon)
            icon.refresh_theme(instance._palette)

    @classmethod
    def unregister(cls, icon: ThemedIcon) -> None:
        instance = cls._get_instance()
        if icon in instance._icons:
            instance._icons.remove(icon)
            DebugLogger.log(f"Icon unregistered: {icon.objectName()}", "debug")

    @classmethod
    def get_palette(cls) -> Dict:
        """Get the current active color palette."""
        return cls._get_instance()._palette
