"""style_manager/loaders/widget_loader.py

Simplified WidgetLoader that reuses ThemeLoader for per-widget styling."""
from typing import Optional

from PySide6.QtWidgets import QWidget

from app.core.utils import DebugLogger
from app.style_manager.theme_controller import ThemeController


class WidgetLoader:
    """
    Simplified helper for applying per-widget styles using ThemeController's ThemeLoader.

    Usage:
        WidgetLoader.apply_widget_style(widget, "path/to/widget.qss")
    """

    @classmethod
    def apply_widget_style(cls, widget: QWidget, style_path: str) -> None:
        """
        Apply a widget-specific stylesheet via ThemeController's ThemeLoader.

        Args:
            widget: QWidget to style.
            style_path: Path to the QSS file.
        """
        if not style_path:
            DebugLogger.log(f"[WidgetLoader] No style path for {widget.__class__.__name__}", "warning")
            return

        tc = ThemeController()
        try:
            # Delegate to ThemeLoader for injection & caching
            qss = tc._loader.load(style_path)
            if qss:
                widget.setStyleSheet(qss)
                DebugLogger.log(f"[WidgetLoader] Applied style {style_path} to {widget.__class__.__name__}", "debug")
            else:
                DebugLogger.log(f"[WidgetLoader] Empty QSS for {style_path}", "warning")
        except Exception as e:
            DebugLogger.log(f"[WidgetLoader] Error applying style: {e}", "error")

    @classmethod
    def clear_cache(cls) -> None:
        """
        Clear the ThemeLoader's internal cache to force reprocessing on theme change.
        """
        tc = ThemeController()
        try:
            tc._loader._cache.clear()
            DebugLogger.log("[WidgetLoader] Cleared widget style cache via ThemeLoader", "info")
        except Exception as e:
            DebugLogger.log(f"[WidgetLoader] Error clearing cache: {e}", "error")

class WidgetStyle(QWidget):
    """
    Base class for QWidgets to automatically apply per-widget QSS and respond to theme changes.
    """
    def __init__(self, parent: Optional[QWidget] = None, widget_style_path: Optional[str] = None):
        super().__init__(parent)
        self._style_path = widget_style_path
        self._tc = ThemeController()
        # Listen for theme changes
        self._tc.theme_changed.connect(self._apply_style)
        # Initial apply
        if self._style_path:
            self._apply_style(self._tc.get_current_palette())

    def set_widget_style_path(self, path: str) -> None:
        """Update style path and immediately apply."""
        self._style_path = path
        self._apply_style(self._tc.get_current_palette())

    def _apply_style(self, *_):
        """Internal slot to apply style using WidgetLoader."""
        if not self._style_path:
            DebugLogger.log(f"[WidgetStyle] No style path for {self.__class__.__name__}", "debug")
            return
        WidgetLoader.clear_cache()
        WidgetLoader.apply_widget_style(self, self._style_path)
