"""app/ui/components/inputs/smart_line_edit.py

Defines a SmartInput with a proxy-filtered dropdown completer and custom submission.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from typing import Sequence

from PySide6.QtCore import QEvent, QStringListModel, Qt, QTimer, Signal
from PySide6.QtWidgets import QCompleter, QLineEdit

from _dev_tools import DebugLogger
from app.ui.components.widgets.dropdown_menu import DropdownMenu
from app.ui.utils import IngredientProxyModel

# fixed height for the line edit
FIXED_HEIGHT = 45


# ── Smart Input ─────────────────────────────────────────────────────────────────────────────────────────
class SmartInput(QLineEdit):
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
        self.setObjectName("SmartInput")

        # Create DropdownMenu with proxy model for filtering
        self.dropdown_menu = DropdownMenu(
            parent=self,
            completion_mode=QCompleter.UnfilteredPopupCompletion
        )
        self.dropdown_menu.set_proxy_model(self.proxy)
        self.dropdown_menu.set_case_sensitivity(Qt.CaseInsensitive)

        # Set the completer for this line edit
        self.setCompleter(self.dropdown_menu.completer)

        # connect signals
        self.dropdown_menu.item_selected.connect(self._on_item_selected)
        self.textEdited.connect(self._on_text_changed)
        self.textChanged.connect(self._on_text_changed)
        self.returnPressed.connect(self._handle_submission)

    def _reset_completer(self):
        """Clear any active filter on the proxy model."""
        self.dropdown_menu.clear_filter()

    def _handle_submission(self):
        """Emit either item_selected or custom_text_submitted on Enter press only."""
        if self.dropdown_menu.completer.popup().isVisible():
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
        # Don't clear the text - keep the selection visible!

    def _on_item_selected(self, text: str):
        """Handle selection from the dropdown menu."""
        self.setText(text)
        self.item_selected.emit(text)
        DebugLogger.log(f"[SIGNAL] Item selected: {text}")
        self._reset_completer()
        # Hide the dropdown after selection
        self.dropdown_menu.hide_popup()
        # Move focus to next widget
        QTimer.singleShot(0, self.focusNextChild)

    def _on_text_changed(self, text: str):
        """Update proxy filter and emit currentTextChanged."""
        self.dropdown_menu.set_filter(text)
        self.currentTextChanged.emit(text)
        DebugLogger.log(f"Text changed: {text}", "debug")

    def focusOutEvent(self, event: QEvent):
        """Handle focus out - hide popup but don't clear text."""
        # Hide the dropdown when focus is lost
        self.dropdown_menu.hide_popup()
        # Don't call _handle_submission() which would clear the text
        super().focusOutEvent(event)

    def currentText(self) -> str:
        """Get the current text from the line edit."""
        return self.text()

    def resizeEvent(self, event):
        """Handle resize events."""
        super().resizeEvent(event)
