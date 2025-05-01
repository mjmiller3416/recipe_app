"""
Helpers Package

Includes general-purpose utility functions and classes for:
- app-level control
- UI interaction/styling
- debug logging
"""

# ─── Application Helpers ────────────────────────────────────────────────────────
from .app_helpers import (exit_fullscreen, load_and_apply_stylesheet,
                          load_stylesheet_for_widget, populate_combobox,
                          show_message_box)
# ─── Debugging ─────────────────────────────────────────────────────────────────
from ...helpers.app_helpers.debug_logger import DebugLogger
# ─── UI Helpers ────────────────────────────────────────────────────────────────
from .ui_helpers import (HoverButton, SidebarAnimator, apply_error_style,
                         clear_error_styles, dynamic_validation,
                         get_all_buttons, get_button_icons, set_scaled_image,
                         svg_loader, wrap_layout)

__all__ = [
    # app_helpers
    "exit_fullscreen", "show_message_box", "populate_combobox",

    # ui_helpers
    "get_all_buttons", "get_button_icons", "svg_loader",
    "apply_error_style", "clear_error_styles", "dynamic_validation",
    "set_scaled_image", "HoverButton", "SidebarAnimator", "wrap_layout",

    # debug_logger
    "DebugLogger",
]
