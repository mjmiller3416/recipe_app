# coding: utf-8
"""
Material Design 3 Color System for Recipe App Theme Manager

This module provides Material Design 3-compliant color generation using
the material-color-utilities library.
"""

from typing import Dict, Any
from material_color_utilities import theme_from_color


# Material Design 3 Accent Colors (from your vision)
ACCENT_COLORS = {
    "Indigo": "#3F51B5",
    "Blue": "#2196F3",
    "Teal": "#009688",
    "Green": "#4CAF50",
    "Yellow": "#FFEB3B",
    "Orange": "#FF9800",
    "Red": "#F44336",
    "Pink": "#E91E63",
    "Purple": "#9C27B0",
    "Deep Purple": "#673AB7",
    "Brown": "#795548",
    "Gray": "#607D8B",
}


def generate_theme_dict(accent_name_or_hex: str, mode: str = "light") -> Dict[str, str]:
    """
    Generate a complete Material Design 3 theme dictionary from a source color.

    Args:
        accent_name_or_hex: Accent color name (e.g., "Blue") or hex color (e.g., "#2196F3")
        mode: Theme mode - "light" or "dark"

    Returns:
        Dictionary with all 27 Material Design 3 semantic roles mapped to hex colors
    """
    # If it's an accent name, get the hex color
    if accent_name_or_hex in ACCENT_COLORS:
        source_hex = ACCENT_COLORS[accent_name_or_hex]
    else:
        source_hex = accent_name_or_hex

    theme = theme_from_color(source_hex)
    scheme = theme.schemes.light if mode == "light" else theme.schemes.dark

    return {
        # Primary colors
        "primary": scheme.primary,
        "on_primary": scheme.on_primary,
        "primary_container": scheme.primary_container,
        "on_primary_container": scheme.on_primary_container,

        # Secondary colors
        "secondary": scheme.secondary,
        "on_secondary": scheme.on_secondary,
        "secondary_container": scheme.secondary_container,
        "on_secondary_container": scheme.on_secondary_container,

        # Tertiary colors
        "tertiary": scheme.tertiary,
        "on_tertiary": scheme.on_tertiary,
        "tertiary_container": scheme.tertiary_container,
        "on_tertiary_container": scheme.on_tertiary_container,

        # Error colors
        "error": scheme.error,
        "on_error": scheme.on_error,
        "error_container": scheme.error_container,
        "on_error_container": scheme.on_error_container,

        # Background and surface colors
        "background": scheme.background,
        "surface": scheme.surface,
        "on_surface": scheme.on_surface,
        "surface_variant": scheme.surface_variant,
        "on_surface_variant": scheme.on_surface_variant,

        # Utility colors
        "outline": scheme.outline,
        "outline_variant": scheme.outline_variant,
        "shadow": scheme.shadow,
        "scrim": scheme.scrim,
        "inverse_surface": scheme.inverse_surface,
        "inverse_on_surface": scheme.inverse_on_surface,
        "inverse_primary": scheme.inverse_primary,

        # Metadata
        "theme_name": mode,  # for icon suffix
    }


def get_available_accent_colors() -> Dict[str, str]:
    """
    Get the available accent colors for user selection.

    Returns:
        Dictionary of color names to hex values
    """
    return ACCENT_COLORS.copy()


def generate_light_theme(source_hex: str) -> Dict[str, str]:
    """
    Generate a light theme from a source color.

    Args:
        source_hex: Source color in hex format

    Returns:
        Light theme dictionary
    """
    return generate_theme_dict(source_hex, "light")


def generate_dark_theme(source_hex: str) -> Dict[str, str]:
    """
    Generate a dark theme from a source color.

    Args:
        source_hex: Source color in hex format

    Returns:
        Dark theme dictionary
    """
    return generate_theme_dict(source_hex, "dark")


def generate_full_theme(source_hex: str) -> Dict[str, Dict[str, str]]:
    """
    Generate both light and dark themes from a source color.

    Args:
        source_hex: Source color in hex format

    Returns:
        Dictionary with 'light' and 'dark' theme dictionaries
    """
    return {
        "light": generate_light_theme(source_hex),
        "dark": generate_dark_theme(source_hex),
        "source_color": source_hex
    }


# Example usage and testing
if __name__ == "__main__":
    # Test with blue accent color
    blue_hex = ACCENT_COLORS["Blue"]

    print("=== Material Design 3 Color Generation Test ===")
    print(f"Source Color: {blue_hex}")
    print()

    # Generate light theme
    light_theme = generate_light_theme(blue_hex)
    print("Light Theme:")
    for role, color in light_theme.items():
        print(f"  {role}: {color}")
    print()

    # Generate dark theme
    dark_theme = generate_dark_theme(blue_hex)
    print("Dark Theme:")
    for role, color in dark_theme.items():
        print(f"  {role}: {color}")
    print()

    # Generate full theme
    full_theme = generate_full_theme(blue_hex)
    print("Full Theme Structure:")
    print(f"  Source: {full_theme['source_color']}")
    print(f"  Light roles: {len(full_theme['light'])} colors")
    print(f"  Dark roles: {len(full_theme['dark'])} colors")
