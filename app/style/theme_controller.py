"""app/style/theme_manager.py

Manages dynamic Material Design 3 theming for PySide6 applications.

This module provides a system to apply a color palette to a global base
stylesheet and to individual widget-specific stylesheets. It allows for
run-time changes of source color and light/dark modes.
"""
# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from typing import Dict, Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

from _dev_tools import DebugLogger
from app.core.utils import QSingleton

from .theme.config import Mode, Qss, Typography
from .theme.style_sheet import Stylesheet


# ── Theme Manager ───────────────────────────────────────────────────────────────────────────────────────────
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

        self._theme_mode  : Mode  = None
        self._current_color_map: Dict[str, str] = {}
        self._current_font_map: Dict[str, str] = Typography.generate_font_variables()
        self._theme_name: str = "light"  # default theme name
        self._base_style = None


    @classmethod
    def _get_instance(cls):
        """Get the singleton instance, creating it if necessary."""
        DebugLogger.log("Fetching Theme singleton instance", "debug")
        if cls not in cls._instances:
            cls._instances[cls] = cls()  # this properly calls __new__ and __init__
        return cls._instances[cls]

    def _inject_theme_colors(self) -> str:
        """Injects the current theme colors and fonts into the given stylesheet content."""
        try:
            base_content = Stylesheet.read(Qss.BASE)
            if not base_content:
                DebugLogger.log(f"Failed to load base stylesheet: {Qss.BASE.value}", "error")
                return ""
            DebugLogger.log(f"Loaded base stylesheet: {Qss.BASE.value}", "info")

            # combine all variable maps
            all_variables = self._current_color_map.copy()
            all_variables.update(self._current_font_map)
            all_variables['theme_name'] = self._theme_name

            self._base_style = Stylesheet.inject_theme(base_content, all_variables)
            if not self._base_style:
                DebugLogger.log(f"Failed to process base stylesheet with theme variables", "error")
                return ""
            DebugLogger.log(f"Processed base stylesheet with theme variables for {self._theme_name} mode", "info")
            return self._base_style
        except Exception as e:
            DebugLogger.log(f"Error in _inject_theme_colors: {e}", "error")
            return ""



    def _load_global_stylesheet(self):
        """Applies the processed global stylesheet to the application."""
        try:
            app = QApplication.instance()
            if not app:
                DebugLogger.log("No QApplication instance found for stylesheet application", "error")
                return

            if not self._base_style:
                DebugLogger.log("No base stylesheet available to apply", "error")
                return

            app.setStyleSheet(self._base_style)
            DebugLogger.log(f"Applied global stylesheet to application for {self._theme_name} theme", "info")
        except Exception as e:
            DebugLogger.log(f"Error applying global stylesheet: {e}", "error")





    # ── Public API ───────────────────────────────────────────────────────────────────────────

    @classmethod
    def setThemeMode(cls, mode: Mode):
        """Sets the application theme mode."""
        instance = cls._get_instance()
        instance._theme_mode = mode
        # update theme name based on mode
        instance._theme_name = mode.value if mode else "light"

        # if we have a current color map, reload it with the new mode
        if hasattr(instance, '_current_file_path') and instance._current_file_path:
            cls.setCustomColorMap(instance._current_file_path, mode)

        DebugLogger.log(f"Theme mode changed to: {mode.value}", "info")


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
        from .theme.custom_color_loader import CustomColorLoader

        custom_color_map = CustomColorLoader.load_from_file(file_path, mode)
        if custom_color_map:
            instance = cls._get_instance()
            instance._current_color_map = custom_color_map
            instance._theme_mode = mode
            instance._theme_name = mode.value if mode else "light"
            instance._current_file_path = file_path  # store for mode switching

            instance._inject_theme_colors()
            instance._load_global_stylesheet()

            # auto-connect icon system (only once)
            if not hasattr(cls, '_icon_loader_connected'):
                from app.style.icon.loader import IconLoader
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
    def get_current_theme_mode(cls) -> Mode:
        """Returns the current theme mode."""
        instance = cls._get_instance()
        return instance._theme_mode

