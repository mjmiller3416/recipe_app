"""app/theme_manager/style_sheet.py

Material Design 3 Color System for Theme Manager

This module provides Material Design 3-compliant color generation using
the material-color-utilities library.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from typing import Dict, Union

from material_color_utilities import theme_from_argb_color, hex_from_argb, argb_from_hex

from dev_tools.debug_logger import DebugLogger
from .config import Color, Mode, Qss

class Stylesheet:
    """
    Processes a QSS stylesheet by injecting color variables.

    This class takes a QSS string containing placeholders like `{primary}`
    and replaces them with actual color values from a provided color map.
    """

    @classmethod
    def inject_theme(cls, stylesheet_content: str, color_map: Dict[str, str]) -> str:
        """Injects color values into a stylesheet template using `{placeholder}` syntax."""
        result = stylesheet_content # make a copy to avoid mutating the original

        for var_name, color_value in color_map.items():
            placeholder = f"{{{var_name}}}"
            result = result.replace(placeholder, color_value)
        return result


    @classmethod
    def read(cls, path: Qss) -> str:
        """Reads a stylesheet file from the given path."""
        try:
            with open(path.value, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            DebugLogger.log(f"Stylesheet file not found: {path.value}", "Error")
            return ""
        except Exception as e:
            DebugLogger.log(f"Error reading stylesheet: {e}", "Error")
            return ""


    @staticmethod
    def fetch_theme_colors(
        color: Union[Color, str],
        mode: Mode
    ) -> Dict[str, str]:
        """
        Generate a complete Material Design 3 theme dictionary from a theme color.

        Args:
            color: Theme color Enum (e.g., "Blue") or hex color (e.g., "#2196F3")
            mode: Theme mode - "light" or "dark"

        Returns:
            Dictionary with all 27 Material Design 3 semantic roles mapped to hex colors
        """
        try:
            color_hex = color.value if isinstance(color, Color) else color
            theme = theme_from_argb_color(color_hex)
            scheme = theme.schemes.light if mode == Mode.LIGHT else theme.schemes.dark

            return {
                # primary colors
                "primary": hex_from_argb(scheme.primary),
                "surface_tint": hex_from_argb(scheme.surface_tint),
                "on_primary": hex_from_argb(scheme.on_primary),
                "primary_container": hex_from_argb(scheme.primary_container),
                "on_primary_container": hex_from_argb(scheme.on_primary_container),

                # secondary colors
                "secondary": hex_from_argb(scheme.secondary),
                "on_secondary": hex_from_argb(scheme.on_secondary),
                "secondary_container": hex_from_argb(scheme.secondary_container),
                "on_secondary_container": hex_from_argb(scheme.on_secondary_container),

                # tertiary colors
                "tertiary": hex_from_argb(scheme.tertiary),
                "on_tertiary": hex_from_argb(scheme.on_tertiary),
                "tertiary_container": hex_from_argb(scheme.tertiary_container),
                "on_tertiary_container": hex_from_argb(scheme.on_tertiary_container),

                # error colors
                "error": hex_from_argb(scheme.error),
                "on_error": hex_from_argb(scheme.on_error),
                "error_container": hex_from_argb(scheme.error_container),
                "on_error_container": hex_from_argb(scheme.on_error_container),

                # background & surface colors
                "background": hex_from_argb(scheme.background),
                "surface": hex_from_argb(scheme.surface),
                "on_surface": hex_from_argb(scheme.on_surface),
                "surface_variant": hex_from_argb(scheme.surface_variant),
                "on_surface_variant": hex_from_argb(scheme.on_surface_variant),
                "surface_dim": hex_from_argb(scheme.surface_dim),
                "surface_bright": hex_from_argb(scheme.surface_bright),
                "surface_container_lowest": hex_from_argb(scheme.surface_container_lowest),
                "surface_container_low": hex_from_argb(scheme.surface_container_low),
                "surface_container": hex_from_argb(scheme.surface_container),
                "surface_container_high": hex_from_argb(scheme.surface_container_high),
                "surface_container_highest": hex_from_argb(scheme.surface_container_highest),

                # utility colors
                "outline": hex_from_argb(scheme.outline),
                "outline_variant": hex_from_argb(scheme.outline_variant),
                "shadow": hex_from_argb(scheme.shadow),
                "scrim": hex_from_argb(scheme.scrim),

                # inverse colors
                "inverse_surface": hex_from_argb(scheme.inverse_surface),
                "inverse_on_surface": hex_from_argb(scheme.inverse_on_surface),
                "inverse_primary": hex_from_argb(scheme.inverse_primary),

                # fixed colors
                "primary_fixed": hex_from_argb(scheme.primary_fixed),
                "on_primary_fixed": hex_from_argb(scheme.on_primary_fixed),
                "primary_fixed_dim": hex_from_argb(scheme.primary_fixed_dim),
                "on_primary_fixed_variant": hex_from_argb(scheme.on_primary_fixed_variant),

                "secondary_fixed": hex_from_argb(scheme.secondary_fixed),
                "on_secondary_fixed": hex_from_argb(scheme.on_secondary_fixed),
                "secondary_fixed_dim": hex_from_argb(scheme.secondary_fixed_dim),
                "on_secondary_fixed_variant": hex_from_argb(scheme.on_secondary_fixed_variant),

                "tertiary_fixed": hex_from_argb(scheme.tertiary_fixed),
                "on_tertiary_fixed": hex_from_argb(scheme.on_tertiary_fixed),
                "tertiary_fixed_dim": hex_from_argb(scheme.tertiary_fixed_dim),
                "on_tertiary_fixed_variant": hex_from_argb(scheme.on_tertiary_fixed_variant),
            }
        except Exception as e:
            DebugLogger.log(f"Error generating theme colors: {e}", "Error")
            return {}  # return empty dict as fallback
