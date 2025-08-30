"""app/theme_manager/theme_manager.py

Manages dynamic Material Design 3 theming for PySide6 applications.

This module provides a system to apply a color palette to a global base
stylesheet and to individual widget-specific stylesheets. It allows for
run-time changes of source color and light/dark modes.
"""
import weakref
# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from typing import Dict, Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication, QWidget

from app.core.utils import QSingleton
from _dev_tools import DebugLogger

from .theme.config import Color, Mode, Qss, Typography
from .theme.style_sheet import Stylesheet


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
        self._current_font_map: Dict[str, str] = Typography.generate_font_variables()
        self._theme_name: str = "light"  # default theme name
        self._base_style = None

        # widget registry for per-widget styling
        self._registered_widgets = weakref.WeakKeyDictionary()  # {widget: qss_type}
        self._component_styles_cache: Dict[Qss, str] = {}  # cache for processed component styles

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

    def _regenerate_theme_colors(self):
        """Generates the new color map and signals that the theme has changed."""
        self._current_color_map = Stylesheet.generate_material_palette(
            self._theme_color, self._theme_mode
        )
        # update theme name based on mode
        self._theme_name = self._theme_mode.value if self._theme_mode else "light"

        self._inject_theme_colors()
        self._load_global_stylesheet()

        # clear component styles cache and update registered widgets
        self._component_styles_cache.clear()
        self._update_registered_widgets()

        self.theme_refresh.emit(self._current_color_map)


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

    def _get_component_style(self, qss_type: Qss) -> str:
        """Get processed stylesheet for a component type, using cache when possible."""
        try:
            if qss_type in self._component_styles_cache:
                DebugLogger.log(f"Retrieved cached component stylesheet: {qss_type.value}", "info")
                return self._component_styles_cache[qss_type]

            # read and process the component stylesheet
            component_content = Stylesheet.read(qss_type)
            if component_content:
                DebugLogger.log(f"Loaded component stylesheet: {qss_type.value}", "info")
                # combine all variable maps
                all_variables = self._current_color_map.copy()
                all_variables.update(self._current_font_map)
                all_variables['theme_name'] = self._theme_name

                processed_style = Stylesheet.inject_theme(component_content, all_variables)
                if not processed_style:
                    DebugLogger.log(f"Failed to process component stylesheet: {qss_type.value}", "error")
                    return ""

                self._component_styles_cache[qss_type] = processed_style
                DebugLogger.log(f"Processed and cached component stylesheet: {qss_type.value}", "info")
                return processed_style
            else:
                DebugLogger.log(f"Failed to load component stylesheet: {qss_type.value}", "error")
                return ""
        except Exception as e:
            DebugLogger.log(f"Error processing component stylesheet {qss_type.value}: {e}", "error")
            return ""

    def _update_registered_widgets(self):
        """Update all registered widgets with their component-specific styles."""
        for widget, qss_type in list(self._registered_widgets.items()):
            if widget is not None:  # ensure widget still exists
                self._apply_component_style(widget, qss_type)

    def _apply_component_style(self, widget: QWidget, qss_type: Qss):
        """Apply component-specific stylesheet to a widget."""
        try:
            component_style = self._get_component_style(qss_type)
            if component_style:
                widget.setStyleSheet(component_style)
                DebugLogger.log(f"Applied {qss_type.name} stylesheet to {widget.objectName()}", "info")
            else:
                DebugLogger.log(f"No stylesheet available for {qss_type.name} component on {widget.objectName()}", "warning")
        except Exception as e:
            DebugLogger.log(f"Error applying stylesheet to {widget.objectName()}: {e}", "error")


    # ── Public API ───────────────────────────────────────────────────────────────────────────
    @classmethod
    def setTheme(cls, theme_color: Color, mode: Mode):
        """Sets both the theme color and mode, regenerating the theme."""
        instance = cls._get_instance()
        instance._theme_color = theme_color
        instance._theme_mode = mode
        instance._regenerate_theme_colors()

        # auto-connect icon system (only once)
        if not hasattr(cls, '_icon_loader_connected'):
            from app.style.icon.loader import IconLoader
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
        from .theme.custom_color_loader import CustomColorLoader

        custom_color_map = CustomColorLoader.load_from_file(file_path, mode)
        if custom_color_map:
            instance = cls._get_instance()
            instance._current_color_map = custom_color_map
            instance._theme_mode = mode
            instance._theme_color = None  # mark as custom (not from predefined colors)

            instance._inject_theme_colors()
            instance._load_global_stylesheet()

            # clear component styles cache and update registered widgets
            instance._component_styles_cache.clear()
            instance._update_registered_widgets()

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
    def get_current_theme_color(cls) -> Color:
        """Returns the current theme color."""
        instance = cls._get_instance()
        return instance._theme_color

    @classmethod
    def get_current_theme_mode(cls) -> Mode:
        """Returns the current theme mode."""
        instance = cls._get_instance()
        return instance._theme_mode

    @classmethod
    def register_widget(cls, widget: QWidget, qss_type: Qss):
        """
        Register a widget for component-specific styling.

        Args:
            widget: The widget to apply styling to
            qss_type: The Qss enum specifying which stylesheet to use
        """
        instance = cls._get_instance()
        instance._registered_widgets[widget] = qss_type

        # apply the style immediately if we have a color map
        if instance._current_color_map:
            instance._apply_component_style(widget, qss_type)

        DebugLogger.log(f"Registered {widget.objectName()} for {qss_type.name} styling", "debug")
