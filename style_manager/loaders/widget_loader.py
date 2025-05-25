"""style_manager/loaders/widget_loader.py

Utility module for loading and applying widget-specific stylesheets.
"""

from pathlib import Path
from typing import Dict, Optional
from PySide6.QtWidgets import QWidget

from core.helpers.debug_logger import DebugLogger
from style_manager.theme_controller import ThemeController

class WidgetLoader:
    """
    Handles per-widget styling that takes precedence over global stylesheets.
    Styles are applied directly to widgets using setStyleSheet().
    """
    
    _widget_styles: Dict[str, str] = {}  # Cache for loaded widget styles
    
    @classmethod
    def load_widget_style(cls, style_path: str, theme: dict) -> str:
        """
        Load and cache a widget-specific stylesheet with theme injection.
        
        Args:
            style_path (str): Path to the widget's QSS file
            theme (dict): Theme dictionary for variable injection
            
        Returns:
            str: Processed stylesheet content
        """
        cache_key = f"{style_path}_{hash(frozenset(theme.items()))}"
        
        if cache_key in cls._widget_styles:
            return cls._widget_styles[cache_key]
            
        try:
            raw_qss = Path(style_path).read_text(encoding="utf-8")
            
            # Inject theme variables (same logic as ThemeLoader)
            for key, value in theme.items():
                if key in {"ICON_STYLES"}:  # Skip complex objects
                    continue
                if not isinstance(value, str):
                    continue

                placeholder = f"{{{key}}}"
                if placeholder in raw_qss:
                    raw_qss = raw_qss.replace(placeholder, value)
            
            cls._widget_styles[cache_key] = raw_qss
            DebugLogger.log(f"[WidgetStyleManager] Loaded widget style: {style_path}", "debug")
            return raw_qss
            
        except FileNotFoundError:
            DebugLogger.log(f"[WidgetStyleManager] Widget style not found: {style_path}", "error")
            return ""
        except Exception as e:
            DebugLogger.log(f"[WidgetStyleManager] Failed to load widget style: {e}", "error")
            return ""
    
    @classmethod
    def apply_widget_style(cls, widget: QWidget, style_path: str, theme: dict) -> None:
        """
        Apply a widget-specific stylesheet that overrides global styles.
        
        Args:
            widget (QWidget): The widget to style
            style_path (str): Path to the widget's QSS file
            theme (dict): Theme dictionary for variable injection
        """
        stylesheet = cls.load_widget_style(style_path, theme)
        if stylesheet:
            widget.setStyleSheet(stylesheet)
            DebugLogger.log(f"[WidgetStyleManager] Applied widget style to {widget.__class__.__name__}", "debug")
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear the widget style cache (useful for theme changes)."""
        cls._widget_styles.clear()
        DebugLogger.log("[WidgetStyleManager] Style cache cleared", "debug")

class BaseWidgetStyle(QWidget):
    """
    Base class for widgets that require widget-specific styling.
    Automatically applies and updates styles when themes change.
    """
    
    def __init__(self, parent: Optional[QWidget] = None, widget_style_path: Optional[str] = None):
        super().__init__(parent)
        self._widget_style_path = widget_style_path
        
        # Connect to theme changes
        theme_controller = ThemeController()
        theme_controller.theme_changed.connect(self._on_theme_changed)
        
        # Apply initial styling if path provided
        if self._widget_style_path:
            self._apply_widget_style()
    
    def set_widget_style_path(self, style_path: str) -> None:
        """Set the widget-specific style path and apply it."""
        self._widget_style_path = style_path
        self._apply_widget_style()
    
    def _apply_widget_style(self) -> None:
        """Apply the widget-specific stylesheet."""
        if not self._widget_style_path:
            return
            
        theme_controller = ThemeController()
        current_palette = theme_controller.get_current_palette()
        WidgetLoader.apply_widget_style(self, self._widget_style_path, current_palette)
    
    def _on_theme_changed(self, palette: dict) -> None:
        """Handle theme changes by reapplying widget styles."""
        if self._widget_style_path:
            # Clear cache to force reload with new theme
            WidgetLoader.clear_cache()
            self._apply_widget_style()