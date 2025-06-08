"""ui/components/inputs/search_bar.py

This module defines a SmartComboBox widget that provides an enhanced
input field with auto-completion, a dropdown list, and a clear entry button.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QLineEdit, QHBoxLayout, QCompleter
from PySide6.QtGui import QFocusEvent, QKeyEvent

from config import SMART_COMBOBOX
from ui.iconkit import ToolButtonIcon
from core.helpers import DebugLogger

# ── Class Definition ────────────────────────────────────────────────────────────
class FocusLineEdit(QLineEdit):
    """A QLineEdit that emits a signal when it gains focus."""
    focusIn = Signal()

    def focusInEvent(self, event: QFocusEvent):
        """Overrides the focus-in event to emit a signal."""
        DebugLogger.log(f"Focus In.", "debug")
        self.focusIn.emit()
        super().focusInEvent(event)

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
        self.line_edit = FocusLineEdit(self) 
        self.line_edit.setObjectName("SCBInput")
        self.line_edit.setPlaceholderText(placeholder)
        if not editable:
            self.line_edit.setReadOnly(True)
    
        # ── Completer ──
        self.completer = QCompleter(list_items, self)
        DebugLogger.log(f"Setting completer model with {len(list_items)} items", log_type = "info")
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
        self.completer.activated.connect(
            self._on_item_selected) # when an item is selected from the completer's popup
        self.completer.setCompletionMode(
            QCompleter.PopupCompletion)  # show popup completion
        self.line_edit.textChanged.connect(
            self._on_text_changed) # when text changes in the input field
        self.line_edit.returnPressed.connect(
            self._on_return_pressed) # when the return key is pressed in the input field
        self.btn_clear.clicked.connect(
            self._on_clear_input) # when the clear button is clicked
        self.btn_dropdown.clicked.connect(
            self._on_completion) # when the dropdown button is clicked to show the completer's popup
        self.line_edit.focusIn.connect(
            self._on_completion) # when the input field gains focus, show the completer's popup

    def _update_button_visibility(self, has_text: bool):
        """
        Updates the visibility of the dropdown and clear buttons based on
        whether the line edit has text.

        Args:
            has_text (bool): True if the line edit is not empty.
        """
        self.btn_clear.setVisible(has_text) # show clear button when there is text
        self.btn_dropdown.setVisible(not has_text) # show dropdown button when there is no text

    def _on_text_changed(self, text):
        """
        Handles text changes in the input field.
        
        Args:
            text (str): The current text in the input field.
        """
        has_text = bool(text) # check if the input field has text
        self._update_button_visibility(has_text) # update button visibility based on text presence

        if text:
            DebugLogger.log(f"Search text changed: {text}", log_type = "debug")
        else:
            self.completer.setCompletionPrefix("")

    def _on_item_selected(self, text: str):
        """Handles item selection from the completer's popup list."""
        self.selection_trigger.emit(text)
        self.line_edit.setText(text)
        self.completer.setCompletionPrefix("")
        self._update_button_visibility(False)
        DebugLogger.log(f"Item '{text}' selected from completer.", log_type="info")

    def _on_return_pressed(self):
        """Handles the return key press event to submit the current text."""
        current_text = self.line_edit.text()
        self.selection_trigger.emit(current_text)
        DebugLogger.log(f"Text '{current_text}' submitted.", log_type="info")
        #self.line_edit.clearFocus()

    def _on_clear_input(self):
        """Clears the input field and resets the completer."""
        self.line_edit.clear()
        DebugLogger.log("Search input cleared", log_type = "info")
    
    def _on_completion(self):
        """Triggers the completer to display the list items."""
        DebugLogger.log("Displaying list items...", log_type = "info")
        self.completer.complete()
        self._update_button_visibility(True)  # show clear button when completer is activated

    def keyPressEvent(self, event: QKeyEvent):
        """
        This method is called automatically whenever a key is pressed
        while this widget has focus.
        """
        if event.key() == Qt.Key.Key_Escape:
            
            DebugLogger.log(f"Focus Out.", "debug")
            self.line_edit.clearFocus()
            self._update_button_visibility(False)  # hide clear button on escape

            event.accept() # accept the event to prevent further processing
            super().keyPressEvent(event) 
    