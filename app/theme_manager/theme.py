"""app/theme_manager/theme_manager.py

Manages dynamic Material Design 3 theming for PySide6 applications.

This module provides a system to apply a color palette to a global base
stylesheet and to individual widget-specific stylesheets. It allows for
run-time changes of source color and light/dark modes.
"""
# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from typing import Dict, Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

from app.core.utils import QSingleton
from dev_tools import DebugLogger

from .config import Color, Mode, Qss
from .style_sheet import Stylesheet

# ── Theme Manager ────────────────────────────────────────────────────────────────────────────
class Theme(QSingleton):
    """
    A singleton manager for the application's visual theme.

    It handles the global stylesheet, manages theme state (light/dark mode, source color),
    and orchestrates updates for all registered widgets.
    """
    theme_refresh = Signal(dict)  # emits the new color map

    def __init__(self, parent: Optional[QObject] = None):
        """Initialize the Theme manager."""
        super().__init__(parent)

        self._theme_color : Color = None
        self._theme_mode  : Mode  = None
        self._current_color_map: Dict[str, str] = {}
        self._base_style = None

    @classmethod
    def _get_instance(cls):
        """Get the singleton instance, creating it if necessary."""
        DebugLogger.log("Fetching Theme singleton instance", "debug")
        if cls not in cls._instances:
            cls._instances[cls] = cls()  # this properly calls __new__ and __init__
        return cls._instances[cls]

    def _inject_theme_colors(self) -> str:
        """Injects the current theme colors into the given stylesheet content."""
        base_content = Stylesheet.read(Qss.BASE)
        self._base_style = Stylesheet.inject_theme(base_content, self._current_color_map)
        return self._base_style

    def _regenerate_theme_colors(self):
        """Generates the new color map and signals that the theme has changed."""
        self._current_color_map = Stylesheet.generate_material_palette(
            self._theme_color, self._theme_mode
        )
        self._inject_theme_colors()
        self._load_global_stylesheet()
        self.theme_refresh.emit(self._current_color_map)


    def _load_global_stylesheet(self):
        """Applies the processed global stylesheet to the application."""
        app = QApplication.instance()
        app.setStyleSheet(self._base_style)


    # ── Public API ───────────────────────────────────────────────────────────────────────────
    @classmethod
    def setTheme(cls, theme_color: Color, mode: Mode):
        """Sets both the theme color and mode, regenerating the theme."""
        instance = cls._get_instance()
        instance._theme_color = theme_color
        instance._theme_mode = mode
        instance._regenerate_theme_colors()

        # Auto-connect icon system (only once)
        if not hasattr(cls, '_icon_loader_connected'):
            from app.theme_manager.icon.loader import IconLoader
            IconLoader.connect_theme_controller(instance)
            cls._icon_loader_connected = True
            DebugLogger.log("IconLoader auto-connected to Theme system", "info")

        DebugLogger.log(
            "Theme set to color: {instance._theme_color}, mode: {instance._theme_mode}",
            "info"
        )

    @classmethod
    def setThemeMode(cls, mode: Mode):
        """Sets the application theme mode."""
        instance = cls._get_instance()
        instance._theme_mode = mode
        instance._regenerate_theme_colors()
        DebugLogger.log("Theme mode changed to: {mode.value}", "info")

    @classmethod
    def setThemeColor(cls, theme_color: Color):
        """Changes the theme color and updates the application theme."""
        if isinstance(theme_color, Color):
            instance = cls._get_instance()
            instance._theme_color = theme_color
            instance._regenerate_theme_colors()
            DebugLogger.log("Theme color changed to: {instance._theme_color}", "info")

    @classmethod
    def toggleThemeMode(cls):
        """Toggles between light and dark mode."""
        instance = cls._get_instance()
        current_mode = Mode.DARK if instance._theme_mode == Mode.LIGHT else Mode.LIGHT
        cls.setThemeMode(current_mode)

    @classmethod
    def setCustomColorMap(cls, file_path: str, mode: Mode):
        """
        Set theme using custom color map from JSON file.

        Args:
            file_path: Path to JSON file containing color schemes
            mode: Theme mode (LIGHT or DARK) to apply
        """
        from .custom_color_loader import CustomColorLoader

        custom_color_map = CustomColorLoader.load_from_file(file_path, mode)
        if custom_color_map:
            instance = cls._get_instance()
            instance._current_color_map = custom_color_map
            instance._theme_mode = mode
            instance._theme_color = None  # Mark as custom (not from predefined colors)

            instance._inject_theme_colors()
            instance._load_global_stylesheet()

            # Auto-connect icon system (only once)
            if not hasattr(cls, '_icon_loader_connected'):
                from app.theme_manager.icon.loader import IconLoader
                IconLoader.connect_theme_controller(instance)
                cls._icon_loader_connected = True
                DebugLogger.log("IconLoader auto-connected to Theme system", "info")

            instance.theme_refresh.emit(instance._current_color_map)

            DebugLogger.log(f"Applied custom color map from {file_path} in {mode.value} mode", "info")
        else:
            DebugLogger.log(f"Failed to load custom color map from {file_path}", "error")


    @classmethod
    def get_current_color_map(cls) -> Dict[str, str]:
        """Returns the current color map."""
        instance = cls._get_instance()
        return instance._current_color_map.copy()

    @classmethod
    def get_current_theme_color(cls) -> Color:
        """Returns the current theme color."""
        instance = cls._get_instance()
        return instance._theme_color

    @classmethod
    def get_current_theme_mode(cls) -> Mode:
        """Returns the current theme mode."""
        instance = cls._get_instance()
        return instance._theme_mode
