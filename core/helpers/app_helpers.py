# Package: app.helpers

# Description: This file contains helper functions for the application, including functions to show message boxes, populate combo boxes,
# and handle key events. These functions are commonly used throughout the application to provide a consistent user experience.

#🔸Standard Imports
from typing import Literal
import os

#🔸Third-Party Imports
from core.helpers.qt_imports import (QMessageBox, Qt, QWidget, QComboBox)

#🔸Local Imports
from core.helpers.debug_logger import DebugLogger
def exit_fullscreen(self, event):
        """
        Handle key press events, such as ESC to exit fullscreen mode.
        """
        if event.key() == Qt.Key_Escape:
            self.main_window.showNormal()

def show_message_box(
    box_type: Literal["info", "save", "confirm"],
    message: str,
    informative_text: str = None,
    parent: QWidget = None
) -> QMessageBox.StandardButton:
    """
    Displays a standardized custom dialog with predefined styles.

    Args:
        box_type (Literal["info", "save", "confirm"]): The type of message box.
        message (str): The main message to display.
        informative_text (str, optional): Additional informative text. Defaults to None.
        parent (QWidget, optional): The parent widget of the dialog. Defaults to None.

    Returns:
        QMessageBox.StandardButton: The button clicked by the user.
    """
    
    from widgets import DialogWidget #🔸Lazy import to avoid circular dependancy 

    dialog = DialogWidget(box_type, message, informative_text, parent)

    # Execute the dialog modally
    dialog.exec()

    # Return the button the user actually clicked
    return dialog.result_button()

def populate_combobox(combobox: QComboBox, *values):
    """
    Populates a QComboBox with the provided values.

    Args:
        combobox (QComboBox): The combobox to populate.
        *values (str or list): A list of values or multiple string arguments.

    Example usage:
        populate_combobox(self.ui.my_combobox, "Option1", "Option2", "Option3")
        OR
        options = ["Option1", "Option2", "Option3"]
        populate_combobox(self.ui.my_combobox, *options)
    """
    if len(values) == 1 and isinstance(values[0], list):
        values = values[0]  # Unpack list if a single list argument is passed
    
    combobox.clear()
    combobox.addItems(values)

def get_user_friendly_name(field_name):
    # Remove known prefixes like "le_", "cb_", "te_"
    for prefix in ["le_", "cb_", "te_"]:
        if field_name.startswith(prefix):
            field_name = field_name[len(prefix):]
            break
    # Replace underscores with spaces and title-case the result.
    return field_name.replace("_", " ").title()

def load_stylesheet(parent, path: str) -> str:
    """
    Loads and applies a stylesheet from the given path, relative to the parent's base directory.
    Args:
        parent: The widget to apply the stylesheet to.
        path (str): The relative or absolute path to the stylesheet file.
    """
    import os
    # Try to resolve path relative to parent's base directory if possible
    base_dir = os.path.dirname(
        os.path.abspath(parent.__module__.replace('.', os.sep) + '.py')
    ) if hasattr(parent, '__module__') else os.getcwd()
    stylesheet_path = os.path.join(base_dir, path) if not os.path.isabs(path) else path
    try:
        with open(stylesheet_path, "r") as file:
            parent.setStyleSheet(file.read())
    except FileNotFoundError:
        DebugLogger.log(f"Stylesheet not found: {stylesheet_path}", "warning")
    except Exception as e:
        DebugLogger.log_and_raise(f"Error loading stylesheet: {e}")

#🔸END