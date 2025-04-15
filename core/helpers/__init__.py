"""
Helpers Package

Includes general-purpose utility functions and classes for:
- app-level control
- UI interaction/styling
- debug logging
"""

# ─── Application Helpers ────────────────────────────────────────────────────────
from .app_helpers import (
    exit_fullscreen,
    show_message_box,
    populate_combobox,
)

# ─── UI Helpers ────────────────────────────────────────────────────────────────
from .ui_helpers import (
    get_all_buttons,
    get_button_icons,
    svg_loader,
    wrap_layout,
    apply_error_style,
    clear_error_styles,
    dynamic_validation,
    set_scaled_image,
    HoverButton,
    SidebarAnimator,
)

# ─── Debugging ─────────────────────────────────────────────────────────────────
from .debug_logger import DebugLogger

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