"""app/ui/utils/form_utils.py

Form handling utilities for validation, data collection, and state management.
Consolidates common form patterns used across Recipe App views.

# ── Internal Index ──────────────────────────────────────────
#
# ── Form Validation ─────────────────────────────────────────
# validate_form_field()        -> Validate single form field
# validate_required_fields()   -> Check required fields in form
# clear_validation_errors()    -> Clear error styling from fields
#
# ── Data Collection & Serialization ─────────────────────────
# collect_form_data()          -> Collect data from form widgets
# populate_form_from_data()    -> Populate form with data dict
# serialize_form_payload()     -> Convert form data to DTO/dict
#
# ── Form State Management ───────────────────────────────────
# clear_form_fields()          -> Clear all form inputs
# reset_form_to_defaults()     -> Reset form to default state
# set_form_enabled_state()     -> Enable/disable form widgets
#
# ── Tab Order & Navigation ──────────────────────────────────
# setup_tab_order_chain()      -> Set up keyboard navigation
# create_tab_order_from_list()  -> Create tab order from widget list

"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from PySide6.QtWidgets import QComboBox, QLineEdit, QTextEdit, QWidget

from app.ui.components.widgets import ComboBox
from app.ui.helpers.validation import clear_error_styles

__all__ = [
    # Form Validation
    'validate_form_field', 'validate_required_fields', 'clear_validation_errors',

    # Data Collection & Serialization
    'collect_form_data', 'populate_form_from_data',

    # Form State Management
    'clear_form_fields', 'reset_form_to_defaults', 'set_form_enabled_state',

    # Tab Order & Navigation
    'setup_tab_order_chain', 'create_tab_order_from_list',
]


# ── Form Validation ─────────────────────────────────────────────────────────────────────────────────────────
def validate_form_field(
    widget: QWidget,
    field_name: str,
    validation_rules: Optional[Dict[str, Any]] = None
) -> tuple[bool, str]:
    """
    Validate a single form field based on rules.

    Args:
        widget: Form widget to validate
        field_name: Name of the field for error messages
        validation_rules: Dict of validation rules (required, min_length, pattern, etc.)

    Returns:
        tuple[bool, str]: (is_valid, error_message)

    Examples:
        valid, error = validate_form_field(name_edit, "Recipe Name", {"required": True})
        valid, error = validate_form_field(qty_edit, "Quantity", {"required": True, "numeric": True})
    """
    if validation_rules is None:
        return True, ""

    # Get field value based on widget type
    if isinstance(widget, QLineEdit):
        value = widget.text().strip()
    elif isinstance(widget, QTextEdit):
        value = widget.toPlainText().strip()
    elif isinstance(widget, (QComboBox, ComboBox)):
        value = widget.currentText().strip()
    else:
        return True, ""  # Unknown widget type, skip validation

    # Check required field
    if validation_rules.get("required", False) and not value:
        return False, f"{field_name} is required"

    # Check minimum length
    min_length = validation_rules.get("min_length")
    if min_length and len(value) < min_length:
        return False, f"{field_name} must be at least {min_length} characters"

    # Check maximum length
    max_length = validation_rules.get("max_length")
    if max_length and len(value) > max_length:
        return False, f"{field_name} must be less than {max_length} characters"

    # Check numeric validation
    if validation_rules.get("numeric", False) and value:
        try:
            float(value)
        except ValueError:
            return False, f"{field_name} must be a valid number"

    return True, ""

def validate_required_fields(form_fields: Dict[str, QWidget]) -> tuple[bool, List[str]]:
    """
    Check required fields in a form and return validation status.

    Args:
        form_fields: Dictionary mapping field names to widgets

    Returns:
        tuple[bool, List[str]]: (all_valid, list_of_error_messages)

    Examples:
        fields = {"Recipe Name": recipe_name_edit, "Servings": servings_edit}
        valid, errors = validate_required_fields(fields)
    """
    errors = []

    for field_name, widget in form_fields.items():
        is_valid, error_msg = validate_form_field(widget, field_name, {"required": True})
        if not is_valid:
            errors.append(error_msg)

    return len(errors) == 0, errors

def clear_validation_errors(widgets: Union[QWidget, List[QWidget]]) -> None:
    """
    Clear error styling from form widgets.

    Args:
        widgets: Single widget or list of widgets to clear errors from

    Examples:
        clear_validation_errors(name_edit)
        clear_validation_errors([name_edit, category_combo, servings_edit])
    """
    if isinstance(widgets, QWidget):
        widgets = [widgets]

    for widget in widgets:
        clear_error_styles(widget)


# ── Data Collection & Serialization ─────────────────────────────────────────────────────────────────────────
def collect_form_data(form_mapping: Dict[str, QWidget]) -> Dict[str, Any]:
    """
    Collect data from form widgets into a dictionary.

    Args:
        form_mapping: Dictionary mapping field names to widgets

    Returns:
        Dict[str, Any]: Dictionary of field names to values

    Examples:
        mapping = {"recipe_name": name_edit, "servings": servings_edit}
        data = collect_form_data(mapping)
        # Returns: {"recipe_name": "Pasta", "servings": "4"}
    """
    form_data = {}

    for field_name, widget in form_mapping.items():
        if isinstance(widget, QLineEdit):
            form_data[field_name] = widget.text().strip()
        elif isinstance(widget, QTextEdit):
            form_data[field_name] = widget.toPlainText().strip()
        elif isinstance(widget, (QComboBox, ComboBox)):
            form_data[field_name] = widget.currentText().strip()
        else:
            # For other widget types, try to get text/value
            if hasattr(widget, 'text'):
                form_data[field_name] = widget.text()
            elif hasattr(widget, 'value'):
                form_data[field_name] = widget.value()
            else:
                form_data[field_name] = None

    return form_data

def populate_form_from_data(
    form_mapping: Dict[str, QWidget],
    data: Dict[str, Any]
) -> None:
    """
    Populate form widgets with data from a dictionary.

    Args:
        form_mapping: Dictionary mapping field names to widgets
        data: Dictionary of field names to values

    Examples:
        mapping = {"recipe_name": name_edit, "servings": servings_edit}
        data = {"recipe_name": "Pasta", "servings": 4}
        populate_form_from_data(mapping, data)
    """
    for field_name, widget in form_mapping.items():
        if field_name not in data:
            continue

        value = data[field_name]
        if value is None:
            continue

        if isinstance(widget, QLineEdit):
            widget.setText(str(value))
        elif isinstance(widget, QTextEdit):
            widget.setPlainText(str(value))
        elif isinstance(widget, (QComboBox, ComboBox)):
            # Try to find and select the matching item
            if hasattr(widget, 'findText'):
                index = widget.findText(str(value))
                if index >= 0:
                    widget.setCurrentIndex(index)
            else:
                widget.setCurrentText(str(value))


# ── Form State Management ───────────────────────────────────────────────────────────────────────────────────
def clear_form_fields(widgets: Union[QWidget, List[QWidget], Dict[str, QWidget]]) -> None:
    """
    Clear all form input widgets to empty state.

    Args:
        widgets: Single widget, list of widgets, or dict mapping to widgets

    Examples:
        clear_form_fields(name_edit)
        clear_form_fields([name_edit, servings_edit, notes_edit])
        clear_form_fields({"name": name_edit, "servings": servings_edit})
    """
    # Normalize to list of widgets
    if isinstance(widgets, dict):
        widget_list = list(widgets.values())
    elif isinstance(widgets, QWidget):
        widget_list = [widgets]
    else:
        widget_list = widgets

    for widget in widget_list:
        if isinstance(widget, QLineEdit):
            widget.clear()
        elif isinstance(widget, QTextEdit):
            widget.clear()
        elif isinstance(widget, (QComboBox, ComboBox)):
            widget.setCurrentIndex(-1)
        elif hasattr(widget, 'clear'):
            widget.clear()

def reset_form_to_defaults(
    form_mapping: Dict[str, QWidget],
    default_values: Optional[Dict[str, Any]] = None
) -> None:
    """
    Reset form to default values or empty state.

    Args:
        form_mapping: Dictionary mapping field names to widgets
        default_values: Optional default values for fields

    Examples:
        reset_form_to_defaults(form_fields)
        reset_form_to_defaults(form_fields, {"servings": "4", "meal_type": "Dinner"})
    """
    # First clear all fields
    clear_form_fields(form_mapping)

    # Then populate with defaults if provided
    if default_values:
        populate_form_from_data(form_mapping, default_values)

def set_form_enabled_state(
    widgets: Union[QWidget, List[QWidget], Dict[str, QWidget]],
    enabled: bool
) -> None:
    """
    Enable or disable form widgets.

    Args:
        widgets: Single widget, list of widgets, or dict mapping to widgets
        enabled: Whether widgets should be enabled

    Examples:
        set_form_enabled_state(form_widgets, False)  # Disable form
        set_form_enabled_state([name_edit, servings_edit], True)  # Enable specific fields
    """
    # Normalize to list of widgets
    if isinstance(widgets, dict):
        widget_list = list(widgets.values())
    elif isinstance(widgets, QWidget):
        widget_list = [widgets]
    else:
        widget_list = widgets

    for widget in widget_list:
        widget.setEnabled(enabled)


# ── Tab Order & Navigation ──────────────────────────────────────────────────────────────────────────────────
def setup_tab_order_chain(widgets: List[QWidget]) -> None:
    """
    Set up keyboard tab navigation order for a list of widgets.

    Args:
        widgets: List of widgets in desired tab order

    Examples:
        widgets = [name_edit, time_edit, servings_edit, category_combo]
        setup_tab_order_chain(widgets)
    """
    if len(widgets) < 2:
        return

    for i in range(len(widgets) - 1):
        QWidget.setTabOrder(widgets[i], widgets[i + 1])

def create_tab_order_from_list(
    widget_names: List[str],
    widget_mapping: Dict[str, QWidget]
) -> None:
    """
    Create tab order from list of widget names using a mapping.

    Args:
        widget_names: List of widget names in desired tab order
        widget_mapping: Dictionary mapping widget names to actual widgets

    Examples:
        names = ["recipe_name", "time", "servings", "category"]
        mapping = {"recipe_name": name_edit, "time": time_edit, ...}
        create_tab_order_from_list(names, mapping)
    """
    widgets = []

    for name in widget_names:
        if name in widget_mapping:
            widgets.append(widget_mapping[name])

    setup_tab_order_chain(widgets)
