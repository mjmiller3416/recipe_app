"""app/ui/components/inputs/smart_line_edit.py

Defines a SmartLineEdit with a proxy-filtered dropdown completer and custom submission.
"""
from typing import Sequence

from PySide6.QtCore import QEvent, QStringListModel, Qt, QTimer, Signal
from PySide6.QtWidgets import QCompleter

from app.ui.components.widgets import DropDown
from app.ui.models import IngredientProxyModel
from dev_tools import DebugLogger

# Fixed height for the line edit
FIXED_HEIGHT = 45


class SmartLineEdit(DropDown):
    """Line edit with proxy-filtered completer and custom text handling."""

    currentTextChanged = Signal(str)
    item_selected = Signal(str)
    custom_text_submitted = Signal(str)

    def __init__(
        self,
        parent=None,
        list_items: Sequence[str] = None,
        placeholder: str = None,
    ):
        # build source and proxy models
        self.source = QStringListModel(list_items or [])
        # create proxy model before base widget init to filter list_items
        self.proxy = IngredientProxyModel()
        self.proxy.setSourceModel(self.source)
        self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)

        # initialize base dropdown with proxy model
        super().__init__(
            parent=parent,
            model=self.proxy,
            placeholder=placeholder,
            read_only=False,
            show_button=False,
            button_icon=None,
            completion_mode=QCompleter.UnfilteredPopupCompletion,
            layout_margins=(0, 0, 0, 0),
            layout_spacing=0,
            show_popup_on_focus=False,
        )
        self.setObjectName("SmartLineEdit")
        # ensure proxy model is parented to this widget for proper cleanup
        self.proxy.setParent(self)
        self.line_edit.setFixedHeight(FIXED_HEIGHT)

        # connect signals
        self.completer.activated.connect(self._on_item_selected)
        self.line_edit.textEdited.connect(self._on_text_changed)
        self.line_edit.textChanged.connect(self._on_text_changed)
        self.line_edit.returnPressed.connect(self._handle_submission)

    def _reset_completer(self):
        """Clear any active filter on the proxy model."""
        self.proxy.setFilterFixedString("")

    def _handle_submission(self):
        """Emit either item_selected or custom_text_submitted on Enter or focus out."""
        if self.completer.popup().isVisible():
            return
        text = self.line_edit.text().strip()
        if not text:
            return

        source_items = [item.lower() for item in self.source.stringList()]
        if text.lower() in source_items:
            self.item_selected.emit(text)
            DebugLogger.log(f"Submitted text '{text}' matched an item in the list.")
        else:
            self.custom_text_submitted.emit(text)
            DebugLogger.log(f"Submitted text '{text}' is a custom entry.")

        self._reset_completer()
        self.line_edit.clear()

    def _on_item_selected(self, text: str):
        """Handle selection from the completer popup."""
        self.line_edit.setText(text)
        self.item_selected.emit(text)
        DebugLogger.log(f"[SIGNAL] Item selected: {text}")
        self._reset_completer()
        QTimer.singleShot(0, self.focusNextChild)

    def _on_text_changed(self, text: str):
        """Update proxy filter and emit currentTextChanged."""
        self.proxy.setFilterFixedString(text)
        self.currentTextChanged.emit(text)
        DebugLogger.log(f"Text changed: {text}", "debug")

    def focusOutEvent(self, event: QEvent):
        """Trigger submission logic when focus is lost."""
        self._handle_submission()
        super().focusOutEvent(event)

    def currentText(self) -> str:
        """Get the current text from the line edit."""
        return self.line_edit.text()
