"""ui/components/inputs/search_bar.py

This module defines a CustomComboBox widget that provides an enhanced
input field with auto-completion, a dropdown list, and a clear entry button.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt, Signal, QStringListModel, QSortFilterProxyModel, QTimer, QEvent 
from PySide6.QtGui import QFocusEvent, QKeyEvent
from PySide6.QtWidgets import QCompleter, QHBoxLayout, QLineEdit, QWidget, QFrame

from config import CUSTOM_COMBOBOX
from core.helpers import DebugLogger
from ui.iconkit import ToolButtonIcon, ButtonIcon
from ui.tools import IngredientProxyModel
from ui.components.widget_frame import WidgetFrame

# ── Class Definition ────────────────────────────────────────────────────────────
class SCBButton(ToolButtonIcon):
    """Overrides the ToolButtonIcon to handle Enter key presses."""
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key_Tab, Qt.Key_Tab):
            self.click()
            event.accept() # accept the event to prevent further processing
        else:
            super().keyPressEvent(event)
    # TODO: Possibly implment directly into ToolButtonIcon

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
class SmartLineEdit(QWidget):
    """CustomComboBox is a custom widget that combines a QLineEdit with a QCompleter
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
            editable: bool = True,
            custom_selection = False,
        ):
        """
        Initializes the CustomComboBox widget.

        Args:
            parent (QWidget): The parent widget.
            list_items (list): List of items for the completer.
            placeholder (str): Placeholder text for the input field.
            editable (bool): Whether the input field is editable.
        """
        super().__init__(parent)
        DebugLogger.log("Initializing CustomComboBox", log_type = "info")
        self.setObjectName("CustomComboBox")

        """ # ── Source Model ──
        self.source = QStringListModel(list_items)

        # ── Proxy Model ──
        self.proxy = IngredientProxyModel(self)
        self.proxy.setSourceModel(self.source)
        self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive) 
        
        ⚠️ The proxy model disabled. 
        TODO: Re-enable it when the filtering logic is fixed
        Subsequent comments marked with ⚠️ indicate the proxy model usage.
        """

        # ── Completer ──
        """ ⚠️ self.completer = QCompleter(self.proxy) """
        self.completer = QCompleter(list_items)
        DebugLogger.log(f"Setting completer model with {len(list_items)} items", log_type = "info")
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        """ ⚠️ self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive) """
        
        # ── Input Field ──
        self.line_edit = FocusLineEdit(self) 
        self.line_edit.setObjectName("SCBInput")
        self.line_edit.setPlaceholderText(placeholder)
        if not editable:
            self.line_edit.setReadOnly(True)

        self.line_edit.setCompleter(self.completer)  # set the completer for the input field
        self.line_edit.installEventFilter(self) # install event filter to handle focus events

        # ── Dropdown Button ──
        self.btn_dropdown = SCBButton(
            file_path = CUSTOM_COMBOBOX["ICON_ARROW"]["FILE_PATH"],
            icon_size = CUSTOM_COMBOBOX["ICON_ARROW"]["ICON_SIZE"],
            variant   = CUSTOM_COMBOBOX["ICON_ARROW"]["DYNAMIC"],
        )
        self.btn_dropdown.setVisible(True) # default visibility
        self.btn_dropdown.setFocusPolicy(Qt.NoFocus) # prevent from tabbing into the button

        # ── Clear Button ──
        self.btn_clear = SCBButton(
            file_path = CUSTOM_COMBOBOX["ICON_CLEAR"]["FILE_PATH"],
            icon_size = CUSTOM_COMBOBOX["ICON_CLEAR"]["ICON_SIZE"],
            variant   = CUSTOM_COMBOBOX["ICON_CLEAR"]["DYNAMIC"],
        )
        self.btn_clear.setVisible(False) # toggle visibility based on text input

        self._connect_signals()  # connect signals to slots
        self._build_ui()  # build the UI layout
    
    def _build_ui(self):
        """
        Builds the UI layout for the CustomComboBox widget.
        
        This method sets up the horizontal layout containing the input field,
        dropdown button, and clear button.
        """
        # ── Outer Layout for CustomComboBox ──
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # ── QFrame Wrapper ──
        self.frame = QFrame(self)
        self.frame.setObjectName("CustomComboBox")  # optional for styling
        self.frame.setFrameShape(QFrame.NoFrame)
        self.frame.setFrameShadow(QFrame.Plain)

        # ── Frame Layout ──
        self.frame_layout = QHBoxLayout(self.frame)
        self.frame_layout.setContentsMargins(0,0,0,0)
        self.frame_layout.setSpacing(5)

        # ── Add Widgets ──
        self.frame_layout.addWidget(self.line_edit)
        self.frame_layout.addWidget(self.btn_dropdown)
        self.frame_layout.addWidget(self.btn_clear)

        # ── Add Frame to Main Layout ──
        self.main_layout.addWidget(self.frame)

        # ── Note ──────────────────────────────────────────────────────────────────────── 
        # Remove initial focus from the input field. This is to prevent the input field 
        # from  stealing focus when the widget is created. May not be necessary in 
        # production, but useful for testing
        # ────────────────────────────────────────────────────────────────────────────────
        QTimer.singleShot(0, lambda: self.parentWidget().setFocus())  

    def _connect_signals(self):
        """
        Connects signals to their respective slots.
        
        Signals:
            - completer.activated: Triggered when an item is selected from the completer.
            - line_edit.textChanged: Triggered when the text in the input field changes.
            - line_edit.returnPressed: Triggered when the return key is pressed.
            - btn_clear.clicked: Triggered when the clear button is clicked.
            - btn_dropdown.clicked: Triggered when the dropdown button is clicked.
            - line_edit.focusIn: Triggered when the input field gains focus.
        """
        self.completer.activated.connect(self._on_item_selected)
        self.line_edit.textChanged.connect(self._on_text_changed)
        """ ⚠️ self.line_edit.returnPressed.connect(self._on_return_pressed) """
        self.btn_clear.clicked.connect(self._on_clear_input)
        self.btn_dropdown.clicked.connect(self._on_completion)
        self.line_edit.focusIn.connect(self._on_completion)

    def _update_button_visibility(self, has_text: bool):
        """
        Updates the visibility of the dropdown and clear buttons based on
        whether the line edit has text.

        Args:
            has_text (bool): True if the line edit is not empty.
        """
        self.btn_clear.setVisible(has_text) # show clear button when there is text
        self.btn_dropdown.setVisible(not has_text) # show dropdown button when there is no text

    def _reset_completer(self):
        """ Resets the completer by clearing the completion prefix and proxy filter."""
        self.completer.setCompletionPrefix("")
        """ ⚠️ self.proxy.setFilterFixedString("") """
        DebugLogger.log("Filtered results have been reset.", log_type="info")


    # ── Events ──────────────────────────────────────────────────────────────────────
    def _on_item_selected(self, text: str):
        """
        Handles item selection from the completer's popup list.
        
        Args:
            text (str): The selected item text.
        """
        DebugLogger.log("[_on_item_selected] event was triggered.", log_type = "debug")
        self.selection_trigger.emit(text) # emit the selected item for external handling
        DebugLogger.log("[SIGNAL] Item '{text}' selected from completer.", log_type="info")

        self._reset_completer()  # reset the completer after selection
        self._update_button_visibility(False)
        
    def _on_text_changed(self, text):
        """
        Handles text changes in the input field and updates button visibility.
        
        Args:
            text (str): The current text in the input field.
        """
        DebugLogger.log("[_on_text_changed] event was triggered.", log_type = "debug")
        has_text = bool(text) # check if the input field has text
        self._update_button_visibility(has_text) # update button visibility based on text presence

        """ ⚠️ self.completer.model().setFilterFixedString(text) """
        """ ⚠️ self.completer.complete() """

        if text:
            DebugLogger.log("Search text changed: {text}", log_type = "debug")
        else:
            self._reset_completer()  # reset completer if text is empty

    def _on_return_pressed(self):
        """Handles the return key press event to submit the current text."""
        DebugLogger.log("[_on_return_pressed] event was triggered.", log_type = "debug")
        current_text = self.line_edit.text()
        self.selection_trigger.emit(current_text)
        DebugLogger.log(f"Text '{current_text}' submitted.", log_type="info")

    def _on_clear_input(self):
        """Clears the input field and resets the completer."""
        DebugLogger.log("[_on_clear_input] event was triggered.", log_type = "debug")
        self.line_edit.setFocus() # keep focus on the input field
        self.line_edit.clear() # clear the input field
        self._reset_completer() # reset the completer
        
        DebugLogger.log("Search input cleared", log_type = "info")
    
    def _on_completion(self):
        """Triggers the completer to display the list items."""
        DebugLogger.log("[_on_completion] event was triggered.", log_type = "debug")
        DebugLogger.log("Displaying list items...", log_type = "info")
        self.completer.complete()
        self._update_button_visibility(True) # show clear button when completer is activated

    def keyPressEvent(self, event: QKeyEvent):
        """
        This method is called automatically whenever a key is pressed
        while this widget has focus.
        """
        if event.key() == Qt.Key.Key_Escape:
            
            DebugLogger.log(f"Focus Out.", "debug")
            self.line_edit.clearFocus()
            self._update_button_visibility(False) # hide clear button on escape

            event.accept() # accept the event to prevent further processing
            super().keyPressEvent(event) 
    