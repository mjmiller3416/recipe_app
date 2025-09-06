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

from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import QComboBox, QLineEdit, QTextEdit, QWidget

from app.ui.components.widgets import ComboBox

__all__ = [
    # Form Validation
    'validate_form_field', 'validate_required_fields', 'clear_validation_errors',

    # Data Collection & Serialization
    'collect_form_data', 'populate_form_from_data',

    # Form State Management
    'clear_form_fields', 'reset_form_to_defaults', 'set_form_enabled_state',

    # Tab Order & Navigation
    'setup_tab_order_chain', 'create_tab_order_from_list',
    
    # ViewModel Form Integration
    'create_dto_field_mapping', 'create_validation_rules', 'extract_form_validation_data',
    'apply_viewmodel_error_styling', 'clear_viewmodel_error_styling', 'setup_viewmodel_field_validation_connections',
]


# ── Form Validation ─────────────────────────────────────────────────────────────────────────────────────────
def apply_error_style(widget: QWidget, error_message: str = None):
    """
    Highlights the invalid field with a red border and shows a tooltip.

    Args:
        widget (QWidget): The specific UI widget that caused the error.
        error_message (str): The validation error message to display.
    """

    widget.setStyleSheet("border: 1px solid red;")

    if error_message:
        widget.setToolTip(error_message)

def clear_error_styles(widget: QLineEdit):
    """
    Removes error highlighting and tooltip from validated UI field.

    Args:
        widget (QLineEdit): Remove error styling effects from widget.
    """
    widget.setStyleSheet("")
    widget.setToolTip("")

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

def dynamic_validation(widget: QLineEdit, validation_rule):
    """
    Applies real-time validation to a QLineEdit widget based on a predefined validation type.

    Args:
        widget (QLineEdit): The input field to validate.
        validation_type (str): The type of validation (must match a key in VALIDATION_RULES).
        error_message (str): The error message to display when validation fails.
    """

    # Create a new validator instance for this widget
    validator = validation_rule(widget)
    widget.setValidator(validator)

    def validate_input():
        text = widget.text()
        state = validator.validate(text, 0)[0]  # Get validation state

        if state == QRegularExpressionValidator.Acceptable:
            clear_error_styles(widget)
        else:
            apply_error_style(widget)

    widget.textChanged.connect(validate_input)  # Real-time validation

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


# ── ViewModel Form Integration ──────────────────────────────────────────────────────────────────────────────
def create_dto_field_mapping(field_configs: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Create DTO field mapping configuration for BaseViewModel._build_dto_data().
    
    Args:
        field_configs: Configuration for each field
            Format: {
                form_field_name: {
                    'dto_field': 'dto_field_name',  # Optional, defaults to form_field_name
                    'required': True/False,         # Optional, defaults to False
                    'default': default_value,       # Optional, defaults to None
                    'transform': callable           # Optional transformation function
                }
            }
    
    Returns:
        Dict[str, Dict[str, Any]]: Processed field mapping for DTO construction
    
    Examples:
        config = {
            'recipe_name': {'required': True, 'max_length': 200},
            'servings': {'transform': lambda x: int(x) if x else 1, 'default': 1},
            'dietary_preference': {'dto_field': 'diet_pref', 'default': None}
        }
        mapping = create_dto_field_mapping(config)
    """
    processed_mapping = {}
    
    for form_field, config in field_configs.items():
        processed_config = {
            'dto_field': config.get('dto_field', form_field),
            'required': config.get('required', False),
            'default': config.get('default', None),
            'transform': config.get('transform', None)
        }
        processed_mapping[form_field] = processed_config
    
    return processed_mapping

def create_validation_rules(field_configs: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Create validation rules configuration from field configs.
    
    Args:
        field_configs: Field configuration dictionary
            Format: {
                field_name: {
                    'required': True/False,
                    'min_length': int,
                    'max_length': int,
                    'numeric': True/False,
                    'min_value': float,
                    'max_value': float
                }
            }
    
    Returns:
        Dict[str, Dict[str, Any]]: Validation rules for batch validation
    
    Examples:
        config = {
            'recipe_name': {'required': True, 'max_length': 200},
            'servings': {'required': True, 'numeric': True, 'min_value': 1}
        }
        rules = create_validation_rules(config)
    """
    validation_rules = {}
    
    for field_name, config in field_configs.items():
        rules = {}
        
        # Copy validation-related keys
        validation_keys = [
            'required', 'min_length', 'max_length', 
            'numeric', 'min_value', 'max_value'
        ]
        
        for key in validation_keys:
            if key in config:
                rules[key] = config[key]
        
        validation_rules[field_name] = rules
    
    return validation_rules

def extract_form_validation_data(form_mapping: Dict[str, QWidget], 
                               field_configs: Dict[str, Dict[str, Any]]) -> List[tuple]:
    """
    Extract validation data tuples for BaseViewModel._batch_validate_fields().
    
    Args:
        form_mapping: Dictionary mapping field names to widgets
        field_configs: Field configuration with validation rules
    
    Returns:
        List[tuple]: List of (field_value, field_name, display_name, validation_rules) tuples
    
    Examples:
        form_data = collect_form_data(form_mapping)
        validation_data = extract_form_validation_data(form_mapping, field_configs)
        result = view_model._batch_validate_fields(validation_data)
    """
    validation_data = []
    form_data = collect_form_data(form_mapping)
    
    for field_name, widget in form_mapping.items():
        if field_name in field_configs:
            field_value = form_data.get(field_name, "")
            display_name = field_configs[field_name].get('display_name', field_name.replace('_', ' ').title())
            validation_rules = create_validation_rules({field_name: field_configs[field_name]})[field_name]
            
            validation_data.append((field_value, field_name, display_name, validation_rules))
    
    return validation_data

def apply_viewmodel_error_styling(field_name: str, error_message: str, form_mapping: Dict[str, QWidget]) -> None:
    """
    Apply error styling to a form field based on ViewModel field validation signals.
    
    Args:
        field_name: Name of the field that failed validation
        error_message: Error message to display
        form_mapping: Dictionary mapping field names to widgets
    
    Examples:
        # Connect to ViewModel signal
        view_model.field_validation_error.connect(
            lambda field, msg: apply_viewmodel_error_styling(field, msg, form_widgets)
        )
    """
    widget = form_mapping.get(field_name)
    if widget:
        apply_error_style(widget, error_message)

def clear_viewmodel_error_styling(field_name: str, form_mapping: Dict[str, QWidget]) -> None:
    """
    Clear error styling from a form field based on ViewModel field validation signals.
    
    Args:
        field_name: Name of the field to clear errors from
        form_mapping: Dictionary mapping field names to widgets
    
    Examples:
        # Connect to ViewModel signal
        view_model.field_validation_cleared.connect(
            lambda field: clear_viewmodel_error_styling(field, form_widgets)
        )
    """
    widget = form_mapping.get(field_name)
    if widget:
        clear_error_styles(widget)

def setup_viewmodel_field_validation_connections(view_model, form_mapping: Dict[str, QWidget]) -> None:
    """
    Set up connections between ViewModel field validation signals and UI error styling.
    
    Args:
        view_model: ViewModel instance with field validation signals
        form_mapping: Dictionary mapping field names to widgets
    
    Examples:
        setup_viewmodel_field_validation_connections(self.recipe_view_model, form_widgets)
    """
    # Connect error and clear signals
    view_model.field_validation_error.connect(
        lambda field, msg: apply_viewmodel_error_styling(field, msg, form_mapping)
    )
    view_model.field_validation_cleared.connect(
        lambda field: clear_viewmodel_error_styling(field, form_mapping)
    )
