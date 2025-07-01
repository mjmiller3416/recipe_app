"""app/ui/components/smart_line_edit.py

This module defines a SmartLineEdit widget that provides an enhanced
input field with auto-completion using a proxy model for advanced filtering.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QEvent, QStringListModel, Qt, QTimer, Signal
from PySide6.QtWidgets import QCompleter, QHBoxLayout, QLineEdit, QWidget

from dev_tools import DebugLogger
from app.ui.models import IngredientProxyModel

# ── Constants ───────────────────────────────────────────────────────────────────
FIXED_HEIGHT = 45

# ── Class Definition ────────────────────────────────────────────────────────────
class SmartLineEdit(QWidget):
    """
    A custom line edit widget that provides auto-completion functionality
    using a list of items. It emits signals when an item is selected or when
    a custom text is submitted.
    """


    # ── Signals ──
    currentTextChanged = Signal(str)
    item_selected = Signal(str)
    custom_text_submitted = Signal(str)

    def __init__(
        self, 
        parent: QWidget = None,
        list_items: list = None,
        placeholder: str = None,
        ):
        """
        Initializes the SmartLineEdit widget with a list of items for auto-completion.

        Args:
            parent (QWidget): The parent widget for this SmartLineEdit.
            list_items (list): A list of strings to populate the completer.
            placeholder (str): Placeholder text for the line edit.
            editable (bool): If True, the line edit is editable; otherwise, it is read-only.
        """
        super().__init__(parent)
        self.setObjectName("SmartLineEdit")

        # ── Source Model ──
        self.source = QStringListModel(list_items)

        # ── Proxy Model ──
        self.proxy = IngredientProxyModel(self)
        self.proxy.setSourceModel(self.source)
        self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        
        # ── Completer ──
        self.completer = QCompleter(self.proxy, self)
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)

        # ── Input Field ──
        self.line_edit = QLineEdit(self) 
        self.line_edit.setPlaceholderText(placeholder)
        self.line_edit.setCompleter(self.completer)
        self.line_edit.setFixedHeight(FIXED_HEIGHT)

        # ── Event Filters ──
        self.line_edit.installEventFilter(self)
        self.completer.popup().installEventFilter(self)

        self._connect_signals()
        self._build_ui()

    # ── Private Methods ────────────────────────────────────────────────────────
    def _build_ui(self):
        """Builds the UI layout for the SmartLineEdit widget."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.line_edit)

    def _connect_signals(self):
        """
        Connects component signals to their respective slots.
        
        Signals:
            - completer.activated: Triggered when an item is selected from the completer.
            - line_edit.textEdited: Triggered when the text in the line edit changes.
            - line_edit.returnPressed: Triggered when the Enter key is pressed.
            - line_edit.textChanged: Triggered when the text in the line edit changes.
        """
        self.completer.activated.connect(self._on_item_selected)
        self.line_edit.textEdited.connect(self._on_text_changed)
        self.line_edit.textChanged.connect(self._on_text_changed)
        self.line_edit.returnPressed.connect(self._handle_submission)
        

    def _reset_completer(self):
        """Resets the completer and proxy filter to a neutral state."""
        self.proxy.setFilterFixedString("")

    def _handle_submission(self):
        """
        Checks the current text upon submission (Enter/focus out) and emits the
        appropriate signal if it's a known item or a custom entry.
        """
        if self.completer.popup().isVisible():
            return # do not submit if the completer popup is visible
        
        text = self.line_edit.text().strip()

        if not text:
            return # no text to submit

        # create a lowercase version of the source list for case-insensitive matching
        source_items = [item.lower() for item in self.source.stringList()]

        if text.lower() in source_items:
            # valid item selected 
            self.item_selected.emit(text)
            DebugLogger.log(f"Submitted text '{text}' matched an item in the list.")
        else:
            # custom entry
            self.custom_text_submitted.emit(text)
            DebugLogger.log(f"Submitted text '{text}' is a custom entry.")

        # reset the completer and clear the line edit after any submission
        self._reset_completer()
        self.line_edit.clear()

    # ── Slots & Events ──────────────────────────────────────────────────────────
    def _on_item_selected(self, text: str):
        """
        Handles final item selection from the completer's popup list.
        
        Args:
            text (str): The text of the selected item.
        """
        self.line_edit.setText(text)
        self.item_selected.emit(text)
        DebugLogger.log(f"[SIGNAL] Item selected: {text}")
        self._reset_completer()
        QTimer.singleShot(0, self.focusNextChild) # keep for smooth focus change
        
    def _on_text_changed(self, text: str):
        """
        Updates the proxy model's filter based on user input.
        
        Args:
            text (str): The text entered in the line edit.
        """
        self.proxy.setFilterFixedString(text)
        self.currentTextChanged.emit(text)
        DebugLogger.log(f"Text changed: {text}", "debug")

    def eventFilter(self, obj: QWidget, event: QEvent) -> bool:
        """
        Filters events for the line edit and completer popup.
        
        Args:
            obj (QWidget): The object that received the event.
            event (QEvent): The event to filter.
        """
        
        # handle the Escape key when the line edit has focus.
        if obj == self.line_edit and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Escape:
                DebugLogger.log("Esc. pressed.", "debug")
                self.completer.popup().hide()
                return True # Event handled

        # handle the Tab key when the completer popup has focus
        if obj == self.completer.popup() and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Tab:
                DebugLogger.log("Tab pressed.", "debug")
                current_index = self.completer.popup().currentIndex()

                # if a valid item is highlighted, select it.
                if current_index.isValid():
                    selected_text = current_index.data()
                    
                    # emit item selection signal,
                    self.completer.activated.emit(selected_text)
                    
                    self.completer.popup().hide()
                    return True # event handled

        # pass on all other events to the default handlers.
        return super().eventFilter(obj, event)
    
    def focusOutEvent(self, event: QEvent):
        """Triggers submission logic when the widget loses focus."""
        self._handle_submission()
        super().focusOutEvent(event)

    def currentText(self) -> str:
        return self.line_edit.text()