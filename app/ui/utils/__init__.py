# File: app/ui/utils/__init__.py

# ── Proxy Models ────────────────────────────────────────────────────────────────────────────
# ── Event Handling Utilities ────────────────────────────────────────────────────────────────
from .event import (FocusEventFilter, TooltipEventFilter,
                    batch_connect_signals, connect_button_actions,
                    connect_form_signals, create_focus_event_filter,
                    create_toggle_handler, create_tooltip_event_filter,
                    install_event_handlers, manage_widget_state_chain,
                    setup_conditional_visibility)
# ── Form Utilities ──────────────────────────────────────────────────────────────────────────
from .form import (apply_error_style, clear_error_styles, clear_form_fields,
                   clear_validation_errors, collect_form_data,
                   create_tab_order_from_list, dynamic_validation,
                   populate_form_from_data, reset_form_to_defaults,
                   set_form_enabled_state, setup_tab_order_chain,
                   validate_form_field, validate_required_fields)
# ── Image Utilities ─────────────────────────────────────────────────────────────────────────
from .image import img_qt_create_placeholder, load_pixmap_or_warn
# ── Layout Utilities ────────────────────────────────────────────────────────────────────────
from .layout import (CornerAnchor, center_on_screen, create_fixed_wrapper,
                     create_form_grid_layout, create_labeled_form_grid,
                     create_scroll_area, create_scroll_content_widget,
                     create_two_column_layout, make_overlay,
                     set_fixed_height_for_layout_widgets, setup_main_scroll_layout)
from .proxy import IngredientProxyModel
# ── Widget Utilities ────────────────────────────────────────────────────────────────────────
from .widget import (CornerAnchor, apply_object_name_pattern, create_button,
                     create_combo_box, create_line_edit, create_text_edit,
                     register_widget_for_theme, setup_form_field,
                     setup_placeholder_text, setup_validation)
__all__ = [
    # Proxy Models
    "IngredientProxyModel",

    # Event Handling
    "FocusEventFilter",
    "TooltipEventFilter",
    "batch_connect_signals",
    "connect_button_actions",
    "connect_form_signals",
    "create_focus_event_filter",
    "create_toggle_handler",
    "create_tooltip_event_filter",
    "install_event_handlers",
    "manage_widget_state_chain",
    "setup_conditional_visibility",
    # Form
    "apply_error_style",
    "clear_error_styles",
    "clear_form_fields",
    "clear_validation_errors",
    "collect_form_data",
    "create_tab_order_from_list",
    "dynamic_validation",
    "populate_form_from_data",
    "reset_form_to_defaults",
    "set_form_enabled_state",
    "setup_tab_order_chain",
    "validate_form_field",
    "validate_required_fields",
    # Image
    "img_qt_create_placeholder",
    "load_pixmap_or_warn",

    # Layout
    "CornerAnchor",
    "center_on_screen",
    "create_fixed_wrapper",
    "create_form_grid_layout",
    "create_labeled_form_grid",
    "create_scroll_area",
    "create_scroll_content_widget",
    "create_two_column_layout",
    "make_overlay",
    "set_fixed_height_for_layout_widgets",
    "setup_main_scroll_layout",
    # Widget
    "CornerAnchor",
    "apply_object_name_pattern",
    "create_button",
    "create_combo_box",
    "create_line_edit",
    "create_text_edit",
    "register_widget_for_theme",
    "setup_form_field",
    "setup_placeholder_text",
    "setup_validation",
]
