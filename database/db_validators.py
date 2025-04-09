# Description: Database validators for recipe and ingredient data.

#🔸Local Imports
from debug_logger import DebugLogger
from qt_imports import (
    QLineEdit, QComboBox, QTextEdit)
from app.helpers.ui_helpers import apply_error_style

#🔹VALIDATE DATA

def validate_data_fields(data): # ✅
    """
    Validates user input widgets before formatting and database insertion.
    - Only checks if fields were completely skipped.
    - Does not trim whitespace (handled elsewhere).

    Args:
        data (dict): Dictionary containing field names as keys and corresponding widget objects.

    Returns:
        bool: True if all fields are valid, False otherwise.
    """
    is_valid = True
    error_messages = {}

    for field_name, widget in data.items():
        
        # 🔹 Validate QLineEdit (Ensure it was at least touched)
        if isinstance(widget, QLineEdit):
            if not widget.text():  # Only fails if it's completely empty
                apply_error_style(widget)
                is_valid = False

        # 🔹 Validate QComboBox (Ensure selection is made)
        elif isinstance(widget, QComboBox):
            if not widget.currentText():
                apply_error_style(widget)
                is_valid = False

        # 🔹 Validate QTextEdit (Ensure it was at least touched)
        elif isinstance(widget, QTextEdit):
            if not widget.toPlainText():  # Only fails if it's completely empty
                apply_error_style(widget)
                is_valid = False

    if error_messages:
        for field, message in error_messages.items():
            DebugLogger.log("Validation Error: {message}")  # Replace with UI feedback

    return is_valid

#🔸END