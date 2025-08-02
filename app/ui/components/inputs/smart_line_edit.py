"""app/ui/components/inputs/smart_line_edit.py

Defines a SmartLineEdit with a proxy-filtered dropdown completer and custom submission.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from typing import Sequence

from PySide6.QtCore import QEvent, QStringListModel, Qt, QTimer, Signal
from PySide6.QtWidgets import QCompleter, QLineEdit

from app.ui.models import IngredientProxyModel
from dev_tools import DebugLogger

# fixed height for the line edit
FIXED_HEIGHT = 45


# ── SmartLineEdit ────────────────────────────────────────────────────────────────────────────
class SmartLineEdit(QLineEdit):
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
        super().__init__(parent)

        # build source and proxy models
        self.source = QStringListModel(list_items or [])
        self.proxy = IngredientProxyModel()
        self.proxy.setSourceModel(self.source)
        self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy.setParent(self)

        # Set up this line edit directly
        if placeholder:
            self.setPlaceholderText(placeholder)
        self.setFixedHeight(FIXED_HEIGHT)
        self.setObjectName("SmartLineEdit")

        # Create and configure completer directly (simpler approach)
        self.completer = QCompleter(self.proxy, self)
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        
        self.completer.popup().setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.completer.popup().setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.completer.popup().setObjectName("SmartLineEditPopup")
        
        # Set the completer for this line edit
        self.setCompleter(self.completer)

        # connect signals
        self.completer.activated.connect(self._on_item_selected)
        self.textEdited.connect(self._on_text_changed)
        self.textChanged.connect(self._on_text_changed)
        self.returnPressed.connect(self._handle_submission)

    def _reset_completer(self):
        """Clear any active filter on the proxy model."""
        self.proxy.setFilterFixedString("")

    def _handle_submission(self):
        """Emit either item_selected or custom_text_submitted on Enter or focus out."""
        if self.completer.popup().isVisible():
            return
        text = self.text().strip()
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
        self.clear()

    def _on_item_selected(self, text: str):
        """Handle selection from the dropdown menu."""
        self.setText(text)
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
        return self.text()

    def resizeEvent(self, event):
        """Handle resize events."""
        super().resizeEvent(event)
