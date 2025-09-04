"""app/style/theme/style_sheet.py

Material Design 3 Color System for Theme Manager

This module provides Material Design 3-compliant color generation using
the material-color-utilities library.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from typing import Dict, Union

from material_color_utilities import argb_from_hex, theme_from_argb_color

from _dev_tools.debug_logger import DebugLogger
from .config import Color, Mode, Qss, Typography

class Stylesheet:
    """
    Processes a QSS stylesheet by injecting color variables.

    This class takes a QSS string containing placeholders like `{primary}`
    and replaces them with actual color values from a provided color map.
    """

    @classmethod
    def inject_theme(
        cls,
        stylesheet_content: str,
        color_map: Dict[str, str],
        font_map: Dict[str, str] = None
    ) -> str:
        """Injects color and font values into a stylesheet template using `{placeholder}` syntax."""
        result = stylesheet_content  # make a copy to avoid mutating the original

        # combine color and font maps
        variable_map = color_map.copy()
        if font_map:
            variable_map.update(font_map)

        # track successful and failed injections
        successful_injections = 0
        failed_injections = []

        # replace placeholders starting with longest names first to avoid partial matches
        for var_name in sorted(variable_map.keys(), key=lambda name: len(name), reverse=True):
            var_value = variable_map[var_name]
            placeholder = f"{{{var_name}}}"

            # check if placeholder exists in stylesheet before replacement
            if placeholder in result:
                result = result.replace(placeholder, var_value)
                successful_injections += 1
                DebugLogger.log(
                    "Successfully injected {placeholder} with value {var_value}",
                    "debug"
                )
            else:
                # only log as failed if the placeholder was expected but not found
                # (don't spam logs for unused variables)
                pass

        # log summary of successful injections
        if successful_injections > 0:
            DebugLogger.log(
                f"Theme injection completed: {successful_injections} variables successfully injected",
                "debug"
            )

        # check for any remaining unmatched placeholders in the result
        # only match placeholders that look like variables (alphanumeric + underscore, no spaces/special chars)
        import re
        remaining_placeholders = re.findall(r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}', result)
        if remaining_placeholders:
            for placeholder in remaining_placeholders:
                DebugLogger.log(
                    f"Warning: Placeholder {{{placeholder}}} found in stylesheet but no matching variable provided",
                    "warning"
                )

        return result


    @classmethod
    def read(cls, path: Qss) -> str:
        """Reads a stylesheet file from the given path."""
        try:
            with open(path.value, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            DebugLogger.log("Stylesheet file not found: {path.value}", "error")
            return ""
        except Exception as e:
            DebugLogger.log("Error reading stylesheet: {e}", "error")
            return ""


    @staticmethod
    def generate_material_palette(
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
        import time
        start_time = time.time()

        try:
            color_hex = color.value if isinstance(color, Color) else color
            # convert hex string to ARGB integer
            color_argb = argb_from_hex(color_hex)
            theme = theme_from_argb_color(color_argb)
            scheme = theme.schemes.light if mode == Mode.LIGHT else theme.schemes.dark

            # build color map and log for debugging
            color_map = {
                # primary colors
                "primary": scheme.primary,
                "surface_tint": scheme.surface_tint,
                "on_primary": scheme.on_primary,
                "primary_container": scheme.primary_container,
                "on_primary_container": scheme.on_primary_container,

                # secondary colors
                "secondary": scheme.secondary,
                "on_secondary": scheme.on_secondary,
                "secondary_container": scheme.secondary_container,
                "on_secondary_container": scheme.on_secondary_container,

                # tertiary colors
                "tertiary": scheme.tertiary,
                "on_tertiary": scheme.on_tertiary,
                "tertiary_container": scheme.tertiary_container,
                "on_tertiary_container": scheme.on_tertiary_container,

                # error colors
                "error": scheme.error,
                "on_error": scheme.on_error,
                "error_container": scheme.error_container,
                "on_error_container": scheme.on_error_container,

                # background & surface colors
                "background": scheme.background,
                "surface": scheme.surface,
                "on_surface": scheme.on_surface,
                "surface_variant": scheme.surface_variant,
                "on_surface_variant": scheme.on_surface_variant,
                "surface_dim": scheme.surface_dim,
                "surface_bright": scheme.surface_bright,
                "surface_container_lowest": scheme.surface_container_lowest,
                "surface_container_low": scheme.surface_container_low,
                "surface_container": scheme.surface_container,
                "surface_container_high": scheme.surface_container_high,
                "surface_container_highest": scheme.surface_container_highest,

                # utility colors
                "outline": scheme.outline,
                "outline_variant": scheme.outline_variant,
                "shadow": scheme.shadow,
                "scrim": scheme.scrim,

                # inverse colors
                "inverse_surface": scheme.inverse_surface,
                "inverse_on_surface": scheme.inverse_on_surface,
                "inverse_primary": scheme.inverse_primary,

                # fixed colors
                "primary_fixed": scheme.primary_fixed,
                "on_primary_fixed": scheme.on_primary_fixed,
                "primary_fixed_dim": scheme.primary_fixed_dim,
                "on_primary_fixed_variant": scheme.on_primary_fixed_variant,

                "secondary_fixed": scheme.secondary_fixed,
                "on_secondary_fixed": scheme.on_secondary_fixed,
                "secondary_fixed_dim": scheme.secondary_fixed_dim,
                "on_secondary_fixed_variant": scheme.on_secondary_fixed_variant,

                "tertiary_fixed": scheme.tertiary_fixed,
                "on_tertiary_fixed": scheme.on_tertiary_fixed,
                "tertiary_fixed_dim": scheme.tertiary_fixed_dim,
                "on_tertiary_fixed_variant": scheme.on_tertiary_fixed_variant,
            }
            duration = time.time() - start_time
            DebugLogger.log("Generated theme colors in {duration:.3f}s: {color_map}", "info")
            return color_map
        except Exception as e:
            DebugLogger.log("Error generating theme colors: {e}", "error")
            return {}  # return empty dict as fallback

    @staticmethod
    def generate_font_variables() -> Dict[str, str]:
        """
        Generate font variables from Typography enum for stylesheet injection.

        Returns:
            Dictionary with font variable names mapped to CSS values
        """
        try:
            font_map = Typography.generate_font_variables()
            DebugLogger.log("Generated font variables: {font_map}", "info")
            return font_map
        except Exception as e:
            DebugLogger.log("Error generating font variables: {e}", "error")
            return {}  # return empty dict as fallback
