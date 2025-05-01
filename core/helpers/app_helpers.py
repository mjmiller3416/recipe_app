# Package: app.helpers

# Description: This file contains helper functions for the application, including functions to show message boxes, populate combo boxes,
# and handle key events. These functions are commonly used throughout the application to provide a consistent user experience.

import inspect
import sys
#🔸Standard Imports
from typing import Literal

from PySide6.QtCore import QFile, QIODevice, QTextStream

#🔸Local Imports
from helpers.app_helpers.debug_logger import DebugLogger
#🔸Third-Party Imports
from core.helpers.qt_imports import (QApplication, QComboBox, QFile,
                                     QMessageBox, Qt, QTextStream, QWidget)


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

    from widgets import \
        DialogWidget  # 🔸Lazy import to avoid circular dependancy

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

def load_and_apply_stylesheet(app: QApplication, file_path: str) -> bool:
    """
    Loads a QSS stylesheet from a file and applies it to the QApplication.

    Args:
        app: The QApplication instance to apply the stylesheet to.
        file_path: The path to the .qss stylesheet file.

    Returns:
        True if the stylesheet was successfully loaded and applied, False otherwise.
    """
    style_file = QFile(file_path)

    # Use QIODevice constants for file opening modes
    # (QFile.ReadOnly and QFile.Text are older Qt4 style,
    # use QIODevice equivalents in Qt5/Qt6)
    if not style_file.open(QIODevice.ReadOnly | QIODevice.Text):
        print(f"Error: Could not open stylesheet file: {file_path}")
        print(f"Reason: {style_file.errorString()}")
        return False

    # Ensure the file is closed even if errors occur during reading
    try:
        in_stream = QTextStream(style_file)
        stylesheet_content = in_stream.readAll()
    except Exception as e:
        print(f"Error reading stylesheet content from {file_path}: {e}")
        style_file.close()
        return False
    finally:
        # Important: Close the file handle
        style_file.close()

    if stylesheet_content:
        try:
            app.setStyleSheet(stylesheet_content)
            DebugLogger.log(f"Successfully loaded and applied stylesheet: {file_path}", "info")
            return True
        except Exception as e:
            # Catch potential errors during setStyleSheet if content is invalid
            # (though Qt usually just prints warnings for invalid QSS)
            print(f"Error applying stylesheet content from {file_path}: {e}")
            return False
    else:
        # File was opened but empty or read failed silently
        print(f"Warning: Stylesheet file '{file_path}' is empty or could not be read.")
        # Optionally apply an empty stylesheet to clear any existing one
        # app.setStyleSheet("")
        return False # Consider empty file a failure or non-action

# In core/helpers/app_helpers.py

# 🔸Third-party Imports (Ensure these are at the top of the file)
from PySide6.QtCore import QFile, QIODevice, QTextStream
from PySide6.QtWidgets import (  # QApplication might still be needed for type hint if used elsewhere
    QApplication, QWidget)

# 🔸Local Imports (Ensure these are at the top of the file)
from helpers.app_helpers.debug_logger import DebugLogger

# --- Existing load_and_apply_stylesheet function ---
# def load_and_apply_stylesheet(app: QApplication, file_path: str) -> bool:
#    ... (your existing global function) ...


# --- New helper for widget-specific styles ---
def load_stylesheet_for_widget(widget: QWidget, file_path: str) -> bool:
    """
    Loads a QSS stylesheet from a file and applies it directly to a specific widget.

    Args:
        widget: The QWidget instance to apply the stylesheet to.
        file_path: The path to the .qss stylesheet file.

    Returns:
        True if the stylesheet was successfully loaded and applied, False otherwise.
    """
    if not isinstance(widget, QWidget):
        DebugLogger.log(f"Error: Invalid 'widget' argument provided. Expected QWidget, got {type(widget)}", "error")
        return False

    style_file = QFile(file_path)

    # Use QIODevice constants for file opening modes
    if not style_file.open(QIODevice.ReadOnly | QIODevice.Text):
        DebugLogger.log(f"Error: Could not open stylesheet file: {file_path}", "error")
        DebugLogger.log(f"Reason: {style_file.errorString()}", "debug")
        return False

    stylesheet_content = ""
    try:
        in_stream = QTextStream(style_file)
        stylesheet_content = in_stream.readAll()
    except Exception as e:
        DebugLogger.log(f"Error reading stylesheet content from {file_path}: {e}", "error")
        return False # Ensure file is closed in finally block even on read error
    finally:
        # Important: Close the file handle
        style_file.close()

    if stylesheet_content:
        try:
            widget.setStyleSheet(stylesheet_content) # Apply directly to the widget
            DebugLogger.log(f"Successfully applied stylesheet '{file_path}' to widget '{widget.objectName() or type(widget).__name__}'", "info")
            return True
        except Exception as e:
            # Catch potential errors during setStyleSheet (though less common for widgets)
            DebugLogger.log(f"Error applying stylesheet content from {file_path} to widget: {e}", "error")
            return False
    else:
        DebugLogger.log(f"Warning: Stylesheet file '{file_path}' is empty or could not be read.", "warning")
        # Optionally clear the widget's specific stylesheet if the file is empty
        # widget.setStyleSheet("")
        return False # Consider empty file a failure or non-action

#🔸END
