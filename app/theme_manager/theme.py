"""app/theme_manager/theme_manager.py

Manages dynamic Material Design 3 theming for PySide6 applications.

This module provides a system to apply a color palette to a global base
stylesheet and to individual widget-specific stylesheets. It allows for
run-time changes of source color and light/dark modes.
"""

import re
from typing import  Dict, Optional
from enum import Enum

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

from dev_tools import DebugLogger
from .config import Color, Mode, Qss
from .style_sheet import Stylesheet

class QSingleton(QObject):
    """A singleton base class for QObject-derived classes."""
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__new__(cls)
        return cls._instances[cls]


class Theme(QSingleton):
    """
    A singleton manager for the application's visual theme.

    It handles the global stylesheet, manages theme state (light/dark mode, source color),
    and orchestrates updates for all registered widgets.
    """
    theme_refresh = Signal(dict)  # emits the new color map

    def __init__(self, parent: Optional[QObject] = None):
        # prevent re-initialization
        if hasattr(self, '_initialized'):
            return
        super().__init__(parent)
        self._initialized = True

        self._theme_color = Color.INDIGO
        self._theme_mode = Mode.LIGHT
        self._current_color_map: Dict[str, str] = {}
        self._base_style = None

        self._regenerate_theme_colors()

    def _inject_theme_colors(self) -> str:
        """Injects the current theme colors into the given stylesheet content."""
        base_content = Stylesheet.read(Qss.BASE)
        self._base_style = Stylesheet.inject_theme(base_content, self._current_color_map)
        return self._base_style

    def _regenerate_theme_colors(self):
        """Generates the new color map and signals that the theme has changed."""
        self._current_color_map = Stylesheet.fetch_theme_colors(
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
    def set_theme(self, mode: Mode):
        """Sets the application theme."""
        self._theme_mode = mode
        self._regenerate_theme_colors()
        DebugLogger.log(f"Theme mode changed to: {mode.value}", "Info")

    def set_theme_color(self, theme_color: Color):
        """Changes the theme color and updates the application theme."""
        if isinstance(theme_color, Color):
            self._theme_color = theme_color
            self._regenerate_theme_colors()
            DebugLogger.log(f"Theme color changed to: {self._theme_color}", "Info")

    def toggle_theme_mode(self):
        """Toggles between light and dark mode."""
        current_mode = Mode.DARK if self._theme_mode == Mode.LIGHT else Mode.LIGHT
        self.set_theme(current_mode)
