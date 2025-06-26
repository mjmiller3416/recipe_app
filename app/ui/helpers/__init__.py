# app/ui/helpers/__init__.py

from .types import ThemedIcon as ThemedIconProtocol  # Rename to avoid conflict
from .ui_helpers import (create_fixed_wrapper, create_framed_layout,
                         create_hbox_with_widgets, create_vbox_with_widgets,
                         make_overlay, center_on_screen)
from .validation import (apply_error_style, clear_error_styles,
                         dynamic_validation)

__all__ = [
    # From types.py
    "ThemedIconProtocol",

    # From ui_helpers.py
    "create_fixed_wrapper", "create_framed_layout", "create_hbox_with_widgets",
    "create_vbox_with_widgets", "make_overlay", "center_on_screen",

    # From validation.py
    "apply_error_style", "clear_error_styles", "dynamic_validation"
]