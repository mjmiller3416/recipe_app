"""app/style/theme/custom_color_loader.py

Custom Color Map Loader for Theme Manager

This module provides functionality to load custom color schemes from JSON files
(like Material Theme Builder exports) and convert them to the format expected
by the existing ThemeManager system.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
import json
from pathlib import Path
from typing import Dict, Optional

from _dev_tools.debug_logger import DebugLogger

from .config import Mode


# ── Custom Color Loader ─────────────────────────────────────────────────────────────────────────────────────
class CustomColorLoader:
    """
    Loads custom color schemes from JSON files and converts them to
    the format expected by the existing ThemeManager system.
    """

    # Mapping from JSON scheme keys to ThemeManager variable names
    _COLOR_MAPPING = {
        # Primary colors
        "primary": "primary",
        "surfaceTint": "surface_tint",
        "onPrimary": "on_primary",
        "primaryContainer": "primary_container",
        "onPrimaryContainer": "on_primary_container",

        # Secondary colors
        "secondary": "secondary",
        "onSecondary": "on_secondary",
        "secondaryContainer": "secondary_container",
        "onSecondaryContainer": "on_secondary_container",

        # Tertiary colors
        "tertiary": "tertiary",
        "onTertiary": "on_tertiary",
        "tertiaryContainer": "tertiary_container",
        "onTertiaryContainer": "on_tertiary_container",

        # Error colors
        "error": "error",
        "onError": "on_error",
        "errorContainer": "error_container",
        "onErrorContainer": "on_error_container",

        # Background & surface colors
        "background": "background",
        "surface": "surface",
        "onSurface": "on_surface",
        "surfaceVariant": "surface_variant",
        "onSurfaceVariant": "on_surface_variant",
        "surfaceDim": "surface_dim",
        "surfaceBright": "surface_bright",
        "surfaceContainerLowest": "surface_container_lowest",
        "surfaceContainerLow": "surface_container_low",
        "surfaceContainer": "surface_container",
        "surfaceContainerHigh": "surface_container_high",
        "surfaceContainerHighest": "surface_container_highest",

        # Utility colors
        "outline": "outline",
        "outlineVariant": "outline_variant",
        "shadow": "shadow",
        "scrim": "scrim",

        # Inverse colors
        "inverseSurface": "inverse_surface",
        "inverseOnSurface": "inverse_on_surface",
        "inversePrimary": "inverse_primary",

        # Fixed colors
        "primaryFixed": "primary_fixed",
        "onPrimaryFixed": "on_primary_fixed",
        "primaryFixedDim": "primary_fixed_dim",
        "onPrimaryFixedVariant": "on_primary_fixed_variant",

        "secondaryFixed": "secondary_fixed",
        "onSecondaryFixed": "on_secondary_fixed",
        "secondaryFixedDim": "secondary_fixed_dim",
        "onSecondaryFixedVariant": "on_secondary_fixed_variant",

        "tertiaryFixed": "tertiary_fixed",
        "onTertiaryFixed": "on_tertiary_fixed",
        "tertiaryFixedDim": "tertiary_fixed_dim",
        "onTertiaryFixedVariant": "on_tertiary_fixed_variant",
    }

    @classmethod
    def load_from_file(cls, file_path: str, mode: Mode) -> Optional[Dict[str, str]]:
        """
        Load custom color scheme from a JSON file.

        Args:
            file_path: Path to the JSON file containing color schemes
            mode: Theme mode (LIGHT or DARK) to extract

        Returns:
            Dictionary mapping ThemeManager variable names to hex color values,
            or None if loading fails
        """
        try:
            path = Path(file_path)
            if not path.exists():
                DebugLogger.log(f"Custom color file not found: {file_path}", "error")
                return None

            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return cls._extract_color_scheme(data, mode)

        except json.JSONDecodeError as e:
            DebugLogger.log(f"Invalid JSON in custom color file: {e}", "error")
            return None
        except Exception as e:
            DebugLogger.log(f"Error loading custom color file: {e}", "error")
            return None

    @classmethod
    def _extract_color_scheme(cls, data: dict, mode: Mode) -> Optional[Dict[str, str]]:
        """
        Extract color scheme from loaded JSON data.

        Args:
            data: Parsed JSON data
            mode: Theme mode to extract (LIGHT or DARK)

        Returns:
            Dictionary mapping ThemeManager variable names to hex colors
        """
        try:
            schemes = data.get("schemes", {})

            # Determine which scheme to use based on mode
            scheme_name = "light" if mode == Mode.LIGHT else "dark"
            scheme_data = schemes.get(scheme_name, {})

            if not scheme_data:
                DebugLogger.log(f"No {scheme_name} scheme found in custom color file", "error")
                return None

            # Convert JSON scheme to ThemeManager format
            color_map = {}
            for json_key, theme_var in cls._COLOR_MAPPING.items():
                if json_key in scheme_data:
                    color_value = scheme_data[json_key]
                    # Ensure color value is a hex string
                    if isinstance(color_value, str) and color_value.startswith('#'):
                        color_map[theme_var] = color_value
                    else:
                        DebugLogger.log(f"Invalid color value for {json_key}: {color_value}", "warning")

            DebugLogger.log(f"Extracted {len(color_map)} colors from custom scheme ({scheme_name} mode)", "info")
            return color_map

        except KeyError as e:
            DebugLogger.log(f"Missing required key in custom color file: {e}", "error")
            return None
        except Exception as e:
            DebugLogger.log(f"Error extracting color scheme: {e}", "error")
            return None
