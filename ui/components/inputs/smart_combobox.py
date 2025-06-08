"""ui/components/inputs/search_bar.py

This module defines a SmartComboBox widget that provides an enhanced
input field with auto-completion, a dropdown list, and a clear entry button.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QLineEdit, QHBoxLayout, QCompleter

from config import SMART_COMBOBOX
from ui.iconkit import ToolButtonIcon
from core.helpers import DebugLogger


# ── Class Definition ────────────────────────────────────────────────────────────
class SmartComboBox(QWidget):
    """SmartComboBox is a custom widget that combines a QLineEdit with a QCompleter
    and additional buttons for dropdown and clear functionality.

    It allows users to type and select items from a list, with features like
    auto-completion and a clear button to reset the input field.
    """
    # ── Signals ─────────────────────────────────────────────────────────────────────
    selection_trigger = Signal(str)  # event for item selection

    def __init__(
            self, 
            parent = None,
            list_items: list = None,
            placeholder: str = None,
            editable: bool = True
        ):
        """
        Initializes the SmartComboBox widget.

        Args:
            parent (QWidget): The parent widget.
            list_items (list): List of items for the completer.
            placeholder (str): Placeholder text for the input field.
            editable (bool): Whether the input field is editable.
        """
        super().__init__(parent)
        DebugLogger.log("Initializing SmartComboBox", log_type = "info")
        self.setObjectName("SmartComboBox")

        # ── Input Field ──
        self.line_edit = QLineEdit(self)
        self.line_edit.setObjectName("SCBInput")
        self.line_edit.setPlaceholderText(placeholder)
        if not editable:
            self.line_edit.setReadOnly(True)
    
        # ── Completer ──
        self.completer = QCompleter(list_items, self)
        DebugLogger.log(f"Setting completer model with {len(list_items)} items", log_type = "debug")
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.line_edit.setCompleter(self.completer)

        # ── Dropdown Button ──
        self.btn_dropdown = ToolButtonIcon(
            file_path = SMART_COMBOBOX["ICON_ARROW"]["FILE_PATH"],
            icon_size = SMART_COMBOBOX["ICON_ARROW"]["ICON_SIZE"],
            variant   = SMART_COMBOBOX["ICON_ARROW"]["DYNAMIC"],
        )
        self.btn_dropdown.setVisible(True) # default visibility

        # ── Clear Button ──
        self.btn_clear = ToolButtonIcon(
            file_path = SMART_COMBOBOX["ICON_CLEAR"]["FILE_PATH"],
            icon_size = SMART_COMBOBOX["ICON_CLEAR"]["ICON_SIZE"],
            variant   = SMART_COMBOBOX["ICON_CLEAR"]["DYNAMIC"],
        )
        self.btn_clear.setVisible(False) # toggle visibility based on text input

        # ── Layout ──
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(12, 0, 8, 0)  # left/right padding for breathing room
        self._layout.setSpacing(5)
        self._layout.addWidget(self.line_edit)
        self._layout.addWidget(self.btn_dropdown)
        self._layout.addWidget(self.btn_clear)

        # ── Signal Connections ──
        self.line_edit.textChanged.connect(self._on_text_changed)
        self.line_edit.returnPressed.connect(self._on_return_pressed)
        self.btn_clear.clicked.connect(self._on_clear_input)
        self.btn_dropdown.clicked.connect(self._on_completion)

    def _on_text_changed(self, text):
        """
        Handles text changes in the input field.
        
        Args:
            text (str): The current text in the input field.
        """
        if text:
            self.btn_dropdown.setVisible(False)
            self.btn_clear.setVisible(True)
            DebugLogger.log(f"Search text changed: {text}", log_type = "debug")
        else:
            self.btn_dropdown.setVisible(True)
            self.btn_clear.setVisible(False)
            self._on_clear_input()

    def _on_return_pressed(self):
        """Handles the return key press event."""
        self.selection_trigger.emit(self.line_edit.text())
        DebugLogger.log(f"{self.line_edit.text()} selected.", log_type = "info")

    def _on_clear_input(self):
        """Clears the input field and resets the completer."""
        self.line_edit.clear()
        self.completer.setCompletionPrefix("")
        DebugLogger.log("Search input cleared", log_type = "info")
    
    def _on_completion(self):
        """Triggers the completer to display the list items."""
        DebugLogger.log("Displaying list items...", log_type = "info")
        self.completer.complete()