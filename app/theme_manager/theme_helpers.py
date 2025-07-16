#!/usr/bin/env python3
"""
Theme helpers for easy widget registration and common theme patterns.
Provides convenience functions and decorators for the Material Design 3 theme system.
"""

from typing import Dict, Any, Optional, Callable
from functools import wraps
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QFrame
from .theme_manager import get_theme_manager


def themed_widget(template: str, custom_properties: Optional[Dict[str, Any]] = None):
    """
    Decorator to automatically register a widget with a theme template.

    Usage:
        @themed_widget('''
        QLabel {
            color: {primary};
            background-color: {surface};
        }
        ''')
        class MyLabel(QLabel):
            pass
    """
    def decorator(widget_class):
        original_init = widget_class.__init__

        @wraps(original_init)
        def new_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            theme_manager = get_theme_manager()
            theme_manager.register_widget(self, template, custom_properties)

        widget_class.__init__ = new_init
        return widget_class

    return decorator


def register_widget_theme(widget: QWidget, template: str, custom_properties: Optional[Dict[str, Any]] = None):
    """
    Convenience function to register a widget with a theme template.

    Args:
        widget: The widget to register
        template: QSS template string with {variable} placeholders
        custom_properties: Optional custom properties for this widget
    """
    theme_manager = get_theme_manager()
    theme_manager.register_widget(widget, template, custom_properties)


def apply_theme_to_stylesheet(template: str, custom_properties: Optional[Dict[str, Any]] = None) -> str:
    """
    Apply current theme to a template string without registering a widget.

    Args:
        template: QSS template string with {variable} placeholders
        custom_properties: Optional custom properties to merge with theme

    Returns:
        Processed stylesheet string
    """
    theme_manager = get_theme_manager()
    return theme_manager.apply_theme_to_string(template, custom_properties)


# Common theme templates for different widget types
COMMON_TEMPLATES = {
    'button_primary': '''
    QPushButton {
        background-color: {primary};
        color: {on_primary};
        border: 1px solid {primary};
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: {primary_container};
        color: {on_primary_container};
    }
    QPushButton:pressed {
        background-color: {primary};
        color: {on_primary};
    }
    ''',

    'button_secondary': '''
    QPushButton {
        background-color: {secondary};
        color: {on_secondary};
        border: 1px solid {secondary};
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: {secondary_container};
        color: {on_secondary_container};
    }
    QPushButton:pressed {
        background-color: {secondary};
        color: {on_secondary};
    }
    ''',

    'button_outline': '''
    QPushButton {
        background-color: transparent;
        color: {primary};
        border: 1px solid {outline};
        border-radius: 6px;
        padding: 8px 16px;
    }
    QPushButton:hover {
        background-color: {surface_variant};
        color: {on_surface_variant};
    }
    QPushButton:pressed {
        background-color: {outline_variant};
        color: {on_surface_variant};
    }
    ''',

    'card': '''
    QFrame {
        background-color: {surface};
        border: 1px solid {outline_variant};
        border-radius: 12px;
        padding: 16px;
    }
    ''',

    'card_elevated': '''
    QFrame {
        background-color: {surface};
        border: 1px solid {outline_variant};
        border-radius: 12px;
        padding: 16px;
    }
    ''',

    'label_title': '''
    QLabel {
        color: {on_surface};
        font-size: 22px;
        font-weight: bold;
    }
    ''',

    'label_subtitle': '''
    QLabel {
        color: {on_surface_variant};
        font-size: 16px;
        font-weight: normal;
    }
    ''',

    'label_body': '''
    QLabel {
        color: {on_surface};
        font-size: 14px;
        font-weight: normal;
    }
    ''',

    'label_caption': '''
    QLabel {
        color: {on_surface_variant};
        font-size: 12px;
        font-weight: normal;
    }
    ''',
}


class ThemedButton(QPushButton):
    """A button that automatically applies Material Design 3 theme styles."""

    def __init__(self, text: str, button_type: str = "primary", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self._apply_theme()

    def _apply_theme(self):
        """Apply the appropriate theme template based on button type."""
        template_key = f"button_{self.button_type}"
        if template_key in COMMON_TEMPLATES:
            register_widget_theme(self, COMMON_TEMPLATES[template_key])
        else:
            # Fallback to primary button style
            register_widget_theme(self, COMMON_TEMPLATES["button_primary"])


class ThemedLabel(QLabel):
    """A label that automatically applies Material Design 3 theme styles."""

    def __init__(self, text: str, label_type: str = "body", parent=None):
        super().__init__(text, parent)
        self.label_type = label_type
        self._apply_theme()

    def _apply_theme(self):
        """Apply the appropriate theme template based on label type."""
        template_key = f"label_{self.label_type}"
        if template_key in COMMON_TEMPLATES:
            register_widget_theme(self, COMMON_TEMPLATES[template_key])
        else:
            # Fallback to body label style
            register_widget_theme(self, COMMON_TEMPLATES["label_body"])


class ThemedCard(QFrame):
    """A card frame that automatically applies Material Design 3 theme styles."""

    def __init__(self, elevated: bool = False, parent=None):
        super().__init__(parent)
        self.elevated = elevated
        self._apply_theme()

    def _apply_theme(self):
        """Apply the appropriate theme template based on card type."""
        template_key = "card_elevated" if self.elevated else "card"
        register_widget_theme(self, COMMON_TEMPLATES[template_key])


def create_themed_widget(widget_class, template_name: str, *args, **kwargs):
    """
    Factory function to create a themed widget.

    Args:
        widget_class: The widget class to instantiate
        template_name: Name of the template from COMMON_TEMPLATES
        *args, **kwargs: Arguments to pass to the widget constructor

    Returns:
        The themed widget instance
    """
    widget = widget_class(*args, **kwargs)
    if template_name in COMMON_TEMPLATES:
        register_widget_theme(widget, COMMON_TEMPLATES[template_name])
    return widget


def get_theme_color(color_name: str) -> str:
    """
    Get a specific color from the current theme.

    Args:
        color_name: Name of the color (e.g., 'primary', 'surface', 'on_primary')

    Returns:
        Hex color string
    """
    theme_manager = get_theme_manager()
    theme_dict = theme_manager.get_current_theme()
    return theme_dict.get(color_name, "#000000")


def get_current_theme_info() -> Dict[str, Any]:
    """
    Get information about the current theme.

    Returns:
        Dictionary with theme information
    """
    theme_manager = get_theme_manager()
    return {
        'accent': theme_manager.get_current_accent(),
        'mode': theme_manager.get_current_mode(),
        'colors': theme_manager.get_current_theme(),
        'registered_widgets': theme_manager.get_registered_widget_count(),
        'available_accents': theme_manager.get_available_accents()
    }


# Convenience functions for common theme operations
def set_accent_color(accent: str):
    """Set the current accent color."""
    theme_manager = get_theme_manager()
    theme_manager.set_accent_color(accent)


def set_theme_mode(mode: str):
    """Set the current theme mode (light/dark)."""
    theme_manager = get_theme_manager()
    theme_manager.set_theme_mode(mode)


def toggle_theme_mode():
    """Toggle between light and dark mode."""
    theme_manager = get_theme_manager()
    theme_manager.toggle_theme_mode()


def initialize_theme_system(global_template_path: str, initial_accent: str = "Blue", initial_mode: str = "light"):
    """
    Initialize the theme system with global template and initial settings.

    Args:
        global_template_path: Path to the global QSS template file
        initial_accent: Initial accent color name
        initial_mode: Initial theme mode (light/dark)
    """
    theme_manager = get_theme_manager()
    theme_manager.set_global_template(global_template_path)
    theme_manager.set_accent_color(initial_accent)
    theme_manager.set_theme_mode(initial_mode)

    print(f"Theme system initialized:")
    print(f"  Global template: {global_template_path}")
    print(f"  Initial accent: {initial_accent}")
    print(f"  Initial mode: {initial_mode}")
