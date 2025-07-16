# coding: utf-8
"""
Template Injection System for Material Design 3 Themes

This module provides the template processing system that applies Material Design 3
colors to QSS stylesheets using Python's string formatting.
"""

import re
import weakref
from typing import Dict, Any, List, Optional
from string import Template
from pathlib import Path

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QWidget, QApplication

try:
    from .material_colors import generate_theme_dict, ACCENT_COLORS
except ImportError:
    # For standalone testing
    from material_colors import generate_theme_dict, ACCENT_COLORS


class ThemeTemplate:
    """
    Material Design 3 theme template processor

    Handles variable injection into QSS stylesheets using Material Design 3 colors.
    """

    def __init__(self, template_content: str):
        """
        Initialize template processor with QSS content

        Args:
            template_content: QSS template content with {variable} placeholders
        """
        self.template_content = template_content

    def _load_template(self, template_path: str):
        """Load the QSS template from file."""
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                self.template_content = f.read()
        except FileNotFoundError:
            print(f"Template file not found: {template_path}")
            self.template_content = ""
        except Exception as e:
            print(f"Error loading template: {e}")
            self.template_content = ""

    def apply_theme(self, theme_dict: Dict[str, str]) -> str:
        """Apply theme colors to the template using string replacement."""
        result = self.template_content
        
        # Replace all theme variables with their hex values
        for key, value in theme_dict.items():
            placeholder = f"{{{key}}}"
            result = result.replace(placeholder, value)
        
        return result

    def get_required_variables(self) -> set:
        """
        Get all variables required by this template

        Returns:
            Set of variable names found in the template
        """
        # Find all {variable} patterns in the template (single line only)
        pattern = r'\{([^}\n]+)\}'
        variables = set(re.findall(pattern, self.template_content))
        return variables

    def validate_template(self, source_color: str, mode: str = "light") -> bool:
        """
        Validate that all template variables can be satisfied

        Args:
            source_color: Source color hex string
            mode: Theme mode

        Returns:
            True if all variables can be satisfied, False otherwise
        """
        required_vars = self.get_required_variables()
        available_vars = set(generate_theme_dict(source_color, mode).keys())

        missing_vars = required_vars - available_vars
        if missing_vars:
            print(f"Warning: Missing variables in theme: {missing_vars}")
            return False

        return True


class ThemeTemplateLoader:
    """
    Loads and manages QSS template files
    """

    def __init__(self, base_path: str = None):
        """
        Initialize template loader

        Args:
            base_path: Base directory for template files
        """
        if base_path is None:
            base_path = Path(__file__).parent.parent / "theme_manager"

        self.base_path = Path(base_path)

    def load_template(self, template_name: str) -> ThemeTemplate:
        """
        Load a QSS template file

        Args:
            template_name: Name of the template file (e.g., "base_style.qss")

        Returns:
            ThemeTemplate instance
        """
        template_path = self.base_path / template_name

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract the BASE_QSS content if it's in Python format
            if template_name.endswith('.qss') and 'BASE_QSS' in content:
                # Extract the string content between triple quotes
                start_marker = 'BASE_QSS = """'
                end_marker = '"""'

                start_idx = content.find(start_marker)
                if start_idx != -1:
                    start_idx += len(start_marker)
                    end_idx = content.find(end_marker, start_idx)
                    if end_idx != -1:
                        content = content[start_idx:end_idx]

            return ThemeTemplate(content)

        except FileNotFoundError:
            raise FileNotFoundError(f"Template file not found: {template_path}")
        except Exception as e:
            raise Exception(f"Error loading template {template_name}: {e}")

    def load_base_style(self) -> ThemeTemplate:
        """
        Load the base style template

        Returns:
            ThemeTemplate for base_style.qss
        """
        return self.load_template("base_style.qss")


class WidgetStyleManager:
    """
    Manages the styles of registered widgets for theme updates.
    """

    def __init__(self):
        """Initialize the widget style manager."""
        self._registered_widgets: Dict[int, weakref.ref] = {}
        self._widget_templates: Dict[int, str] = {}
        self._widget_custom_properties: Dict[int, Dict[str, Any]] = {}

    def register_widget(self, widget: QWidget, template: str, custom_properties: Optional[Dict[str, Any]] = None):
        """
        Register a widget for automatic theme updates.

        Args:
            widget: The widget to register
            template: QSS template string with {variable} placeholders
            custom_properties: Optional dict of custom properties for this widget
        """
        widget_id = id(widget)

        # Create weak reference with cleanup callback
        def cleanup_callback(ref):
            self._cleanup_widget(widget_id)

        weak_ref = weakref.ref(widget, cleanup_callback)

        # Store widget data
        self._registered_widgets[widget_id] = weak_ref
        self._widget_templates[widget_id] = template
        self._widget_custom_properties[widget_id] = custom_properties or {}

        print(f"Registered widget: {widget.__class__.__name__} (ID: {widget_id})")

    def unregister_widget(self, widget: QWidget):
        """Manually unregister a widget."""
        widget_id = id(widget)
        self._cleanup_widget(widget_id)
        print(f"Unregistered widget: {widget.__class__.__name__} (ID: {widget_id})")

    def _cleanup_widget(self, widget_id: int):
        """Clean up data for a destroyed widget."""
        self._registered_widgets.pop(widget_id, None)
        self._widget_templates.pop(widget_id, None)
        self._widget_custom_properties.pop(widget_id, None)

    def update_all_widgets(self, theme_dict: Dict[str, str]):
        """Update all registered widgets with new theme."""
        dead_widgets = []

        for widget_id, weak_ref in self._registered_widgets.items():
            widget = weak_ref()
            if widget is None:
                dead_widgets.append(widget_id)
                continue

            # Get widget's template and custom properties
            template = self._widget_templates.get(widget_id, "")
            custom_props = self._widget_custom_properties.get(widget_id, {})

            # Merge theme dict with custom properties
            merged_dict = {**theme_dict, **custom_props}

            # Apply theme to template
            stylesheet = self._apply_template(template, merged_dict)

            # Update widget stylesheet
            widget.setStyleSheet(stylesheet)

        # Clean up dead widgets
        for widget_id in dead_widgets:
            self._cleanup_widget(widget_id)

        print(f"Updated {len(self._registered_widgets) - len(dead_widgets)} widgets")

    def _apply_template(self, template: str, theme_dict: Dict[str, str]) -> str:
        """Apply theme variables to a template string."""
        result = template
        for key, value in theme_dict.items():
            placeholder = f"{{{key}}}"
            result = result.replace(placeholder, value)
        return result

    def get_registered_count(self) -> int:
        """Get number of currently registered widgets."""
        return len(self._registered_widgets)

    def get_widget_info(self) -> List[Dict[str, Any]]:
        """Get information about all registered widgets (for debugging)."""
        info = []
        for widget_id, weak_ref in self._registered_widgets.items():
            widget = weak_ref()
            if widget is not None:
                info.append({
                    'id': widget_id,
                    'class': widget.__class__.__name__,
                    'objectName': widget.objectName(),
                    'has_custom_properties': bool(self._widget_custom_properties.get(widget_id))
                })
        return info


class ThemeManager(QObject):
    """
    Central theme manager that handles global theme state and widget registration.
    Provides QFluentWidgets-style per-widget theme management.
    """
    # Signal emitted when theme changes
    theme_changed = Signal(dict)  # Emits the new theme dictionary
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one ThemeManager exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        super().__init__()
        self._initialized = True
        
        # Current theme state
        self._current_accent = "Blue"
        self._current_mode = "light"
        self._current_theme_dict = {}
        
        # Widget management
        self._widget_manager = WidgetStyleManager()
        
        # Global template (for app-wide styles)
        self._global_template = None
        
        # Initialize with default theme
        self._update_theme()
        
        # Connect signal to widget updates
        self.theme_changed.connect(self._widget_manager.update_all_widgets)
    
    def set_global_template(self, template_path: str):
        """Set the global QSS template file."""
        self._global_template = ThemeTemplate(template_path)
        self._update_global_stylesheet()
    
    def set_accent_color(self, accent_name: str):
        """Change the accent color and update all themes."""
        if accent_name in ACCENT_COLORS:
            self._current_accent = accent_name
            self._update_theme()
            print(f"Theme accent changed to: {accent_name}")
        else:
            print(f"Unknown accent color: {accent_name}")
    
    def set_theme_mode(self, mode: str):
        """Change between light and dark mode."""
        if mode in ["light", "dark"]:
            self._current_mode = mode
            self._update_theme()
            print(f"Theme mode changed to: {mode}")
        else:
            print(f"Unknown theme mode: {mode}")
    
    def toggle_theme_mode(self):
        """Toggle between light and dark mode."""
        new_mode = "dark" if self._current_mode == "light" else "light"
        self.set_theme_mode(new_mode)
    
    def _update_theme(self):
        """Update the current theme dictionary and emit signals."""
        self._current_theme_dict = generate_theme_dict(
            self._current_accent, 
            self._current_mode
        )
        
        # Update global stylesheet
        self._update_global_stylesheet()
        
        # Emit signal to update all registered widgets
        self.theme_changed.emit(self._current_theme_dict)
    
    def _update_global_stylesheet(self):
        """Update the application's global stylesheet."""
        if self._global_template:
            stylesheet = self._global_template.apply_theme(self._current_theme_dict)
            QApplication.instance().setStyleSheet(stylesheet)
    
    def register_widget(self, widget: QWidget, template: str, custom_properties: Optional[Dict[str, Any]] = None):
        """
        Register a widget for automatic theme updates.
        
        Args:
            widget: The widget to register
            template: QSS template string with {variable} placeholders  
            custom_properties: Optional dict of custom properties for this widget
            
        Example:
            manager = ThemeManager()
            button_template = '''
            QPushButton {
                background-color: {primary};
                color: {on_primary};
                border: 1px solid {outline};
                border-radius: {border_radius}px;
            }
            QPushButton:hover {
                background-color: {primary_container};
            }
            '''
            manager.register_widget(my_button, button_template, {'border_radius': '8'})
        """
        self._widget_manager.register_widget(widget, template, custom_properties)
        
        # Apply current theme immediately
        merged_dict = {**self._current_theme_dict, **(custom_properties or {})}
        stylesheet = self._widget_manager._apply_template(template, merged_dict)
        widget.setStyleSheet(stylesheet)
    
    def unregister_widget(self, widget: QWidget):
        """Manually unregister a widget from theme updates."""
        self._widget_manager.unregister_widget(widget)
    
    def get_current_theme(self) -> Dict[str, str]:
        """Get the current theme dictionary."""
        return self._current_theme_dict.copy()
    
    def get_current_accent(self) -> str:
        """Get the current accent color name."""
        return self._current_accent
    
    def get_current_mode(self) -> str:
        """Get the current theme mode (light/dark)."""
        return self._current_mode
    
    def get_available_accents(self) -> List[str]:
        """Get list of available accent colors."""
        return list(ACCENT_COLORS.keys())
    
    def get_registered_widget_count(self) -> int:
        """Get number of registered widgets."""
        return self._widget_manager.get_registered_count()
    
    def get_widget_info(self) -> List[Dict[str, Any]]:
        """Get debug information about registered widgets."""
        return self._widget_manager.get_widget_info()
    
    def apply_theme_to_string(self, template: str, custom_properties: Optional[Dict[str, Any]] = None) -> str:
        """
        Apply current theme to a template string without registering a widget.
        Useful for one-time stylesheet generation.
        """
        merged_dict = {**self._current_theme_dict, **(custom_properties or {})}
        return self._widget_manager._apply_template(template, merged_dict)


# Convenience function for getting the singleton instance
def get_theme_manager() -> ThemeManager:
    """Get the global ThemeManager instance."""
    return ThemeManager()


# Example usage and testing
if __name__ == "__main__":
    print("=== Material Design 3 Theme Manager Test ===")

    # Initialize theme manager
    theme_manager = ThemeManager()

    # Test different accent colors
    for accent in ["Blue", "Green", "Purple"]:
        print(f"\n--- Testing {accent} Accent ---")
        theme_manager.set_accent_color(accent)

        # Test light and dark modes
        for mode in ["light", "dark"]:
            theme_manager.set_theme_mode(mode)

            try:
                # Get base style QSS
                qss = theme_manager.get_base_style_qss()
                print(f"{accent} {mode.capitalize()}: {len(qss)} characters of QSS generated")

                # Show a sample of the generated QSS
                lines = qss.split('\n')[:5]
                print("Sample QSS:")
                for line in lines:
                    if line.strip():
                        print(f"  {line}")

            except Exception as e:
                print(f"Error with {accent} {mode}: {e}")

    print("\n=== Theme Color Dictionary ===")
    theme_manager.set_accent_color("Blue")
    theme_manager.set_theme_mode("light")

    color_dict = theme_manager.get_current_theme_dict()
    print("Current theme colors:")
    for role, color in color_dict.items():
        print(f"  {role}: {color}")

    print(f"\nAvailable accents: {list(theme_manager.get_available_accents().keys())}")
