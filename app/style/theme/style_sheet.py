"""app/style/theme/style_sheet.py

Material Design 3 Color System for Theme Manager

This module provides Material Design 3-compliant color generation using
the material-color-utilities library.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from typing import Dict, Union

from _dev_tools.debug_logger import DebugLogger

from .config import Mode, Qss, Typography


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
