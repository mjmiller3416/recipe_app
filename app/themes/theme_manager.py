# coding: utf-8
"""
Template Injection System for Material Design 3 Themes

This module provides the template processing system that applies Material Design 3
colors to QSS stylesheets using Python's string formatting.
"""

import re
from typing import Dict, Any
from string import Template
from pathlib import Path

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

    def apply_theme(self, source_color: str, mode: str = "light") -> str:
        """
        Apply Material Design 3 theme colors to the template

        Args:
            source_color: Source color hex string (e.g., "#2196F3")
            mode: Theme mode - "light" or "dark"

        Returns:
            Processed QSS with colors applied
        """
        # Generate Material Design 3 color dictionary
        color_dict = generate_theme_dict(source_color, mode)

        try:
            # Apply colors to template using simple string replacement
            processed_qss = self.template_content

            for variable, color_value in color_dict.items():
                placeholder = f"{{{variable}}}"
                processed_qss = processed_qss.replace(placeholder, color_value)

            return processed_qss

        except Exception as e:
            print(f"Error applying theme template: {e}")
            return self.template_content

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


class ThemeManager:
    """
    Main theme manager for applying Material Design 3 themes
    """

    def __init__(self):
        """Initialize theme manager"""
        self.loader = ThemeTemplateLoader()
        self.current_accent = "Blue"
        self.current_mode = "light"
        self.templates = {}

    def set_accent_color(self, accent_name: str):
        """
        Set the current accent color

        Args:
            accent_name: Name of accent color from ACCENT_COLORS
        """
        if accent_name not in ACCENT_COLORS:
            raise ValueError(f"Unknown accent color: {accent_name}. Available: {list(ACCENT_COLORS.keys())}")

        self.current_accent = accent_name

    def set_theme_mode(self, mode: str):
        """
        Set the current theme mode

        Args:
            mode: "light" or "dark"
        """
        if mode not in ["light", "dark"]:
            raise ValueError(f"Invalid theme mode: {mode}. Must be 'light' or 'dark'")

        self.current_mode = mode

    def get_current_source_color(self) -> str:
        """
        Get the current source color hex value

        Returns:
            Hex color string
        """
        return ACCENT_COLORS[self.current_accent]

    def apply_theme_to_template(self, template_name: str) -> str:
        """
        Apply current theme to a template

        Args:
            template_name: Name of template to process

        Returns:
            Processed QSS string
        """
        # Load template (cache for performance)
        if template_name not in self.templates:
            self.templates[template_name] = self.loader.load_template(template_name)

        template = self.templates[template_name]
        source_color = self.get_current_source_color()

        return template.apply_theme(source_color, self.current_mode)

    def get_base_style_qss(self) -> str:
        """
        Get the base style QSS with current theme applied

        Returns:
            Processed base style QSS
        """
        return self.apply_theme_to_template("base_style.qss")

    def get_available_accents(self) -> Dict[str, str]:
        """
        Get available accent colors

        Returns:
            Dictionary of accent names to hex values
        """
        return ACCENT_COLORS.copy()

    def get_current_theme_dict(self) -> Dict[str, str]:
        """
        Get the current theme color dictionary

        Returns:
            Dictionary of Material Design 3 color roles
        """
        source_color = self.get_current_source_color()
        return generate_theme_dict(source_color, self.current_mode)


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
