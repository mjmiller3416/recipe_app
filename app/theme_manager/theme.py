"""app/theme_manager/theme_manager.py

Manages dynamic Material Design 3 theming for PySide6 applications.

This module provides a system to apply a color palette to a global base
stylesheet and to individual widget-specific stylesheets. It allows for
run-time changes of source color and light/dark modes.
"""

import re
from enum import Enum
from typing import Dict, Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

from app.core.utils import QSingleton
from dev_tools import DebugLogger

from .config import Color, Mode, Qss
from .style_sheet import Stylesheet


class Theme(QSingleton):
    """
    A singleton manager for the application's visual theme.

    It handles the global stylesheet, manages theme state (light/dark mode, source color),
    and orchestrates updates for all registered widgets.
    """
    theme_refresh = Signal(dict)  # emits the new color map

    # Widget styling registry
    _widget_class_registry: Dict[type, Qss] = {}  # Maps widget classes to QSS enums
    _widget_instance_registry: Dict[object, Qss] = {}  # Maps widget instances to QSS enums

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

    def _refresh_widget_instances(self):
        """Refresh stylesheets for all registered widget instances."""
        if not self._current_color_map:
            return
            
        # Create a copy of the registry to avoid issues if widgets are destroyed during iteration
        widget_instances = list(self._widget_instance_registry.items())
        
        for widget, qss_enum in widget_instances:
            try:
                # Check if widget still exists (not destroyed)
                if hasattr(widget, 'setStyleSheet'):
                    stylesheet_content = Stylesheet.read(qss_enum)
                    if stylesheet_content:
                        processed_stylesheet = Stylesheet.inject_theme(stylesheet_content, self._current_color_map)
                        widget.setStyleSheet(processed_stylesheet)
                        DebugLogger.log(
                            f"Refreshed {qss_enum.name} stylesheet for {widget.__class__.__name__}",
                            "debug"
                        )
                else:
                    # Widget was destroyed, remove from registry
                    del self._widget_instance_registry[widget]
            except RuntimeError:
                # Widget was destroyed, remove from registry
                if widget in self._widget_instance_registry:
                    del self._widget_instance_registry[widget]

    def _regenerate_theme_colors(self):
        """Generates the new color map and signals that the theme has changed."""
        self._current_color_map = Stylesheet.generate_material_palette(
            self._theme_color, self._theme_mode
        )
        self._inject_theme_colors()
        self._load_global_stylesheet()
        self._refresh_widget_instances()
        self.theme_refresh.emit(self._current_color_map)


    def _load_global_stylesheet(self):
        """Applies the processed global stylesheet to the application."""
        app = QApplication.instance()
        app.setStyleSheet(self._base_style)


    # ── Public API ───────────────────────────────────────────────────────────────────────────

    # ── Widget Styling ──
    @classmethod
    def registerWidgetStyle(cls, widget_class: type, qss_enum: Qss):
        """
        Register a widget class with its corresponding QSS stylesheet.
        
        Args:
            widget_class: The widget class to register (e.g., TitleBar, SearchBar)
            qss_enum: The QSS enum value for the stylesheet (e.g., Qss.TITLEBAR)
        """
        cls._widget_class_registry[widget_class] = qss_enum
        DebugLogger.log(
            f"Registered widget class {widget_class.__name__} with stylesheet {qss_enum.name}",
            "info"
        )

    @classmethod
    def applyWidgetStyle(cls, widget):
        """
        Apply the registered stylesheet to a widget instance.
        
        Args:
            widget: The widget instance to style
        """
        instance = cls._get_instance()
        widget_class = widget.__class__
        
        # Check if this widget class is registered
        if widget_class not in cls._widget_class_registry:
            DebugLogger.log(
                f"Widget class {widget_class.__name__} not registered for styling",
                "warning"
            )
            return
            
        qss_enum = cls._widget_class_registry[widget_class]
        
        # Read and process the stylesheet
        stylesheet_content = Stylesheet.read(qss_enum)
        if not stylesheet_content:
            DebugLogger.log(
                f"Failed to read stylesheet {qss_enum.name} for {widget_class.__name__}",
                "error"
            )
            return
            
        # Inject current theme colors
        processed_stylesheet = Stylesheet.inject_theme(stylesheet_content, instance._current_color_map)
        
        # Apply to widget
        widget.setStyleSheet(processed_stylesheet)
        
        # Register instance for theme refresh updates
        cls._widget_instance_registry[widget] = qss_enum
        
        DebugLogger.log(
            f"Applied {qss_enum.name} stylesheet to {widget_class.__name__} instance",
            "info"
        )

    # ── Setters ──
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

    # ── Getters ──
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
