"""ui/tools/validation.py

This module provides functions to apply error styles, clear error styles, and perform dynamic validation on 
QLineEdit widgets in a PySide6 application. 
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import QLineEdit, QWidget


# ── Public Methods ──────────────────────────────────────────────────────────────
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