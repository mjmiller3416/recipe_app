"""app/ui/components/widgets/combobox.py

Defines a custom ComboBox using DropDown for read-only selection with a button.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from typing import Sequence

from PySide6.QtCore import Qt, QStringListModel, Signal
from PySide6.QtWidgets import QWidget

from app.config import AppIcon
from .dropdown_widget import DropDown


# ── ComboBox ─────────────────────────────────────────────────────────────────────────────────
class ComboBox(DropDown):
    """Custom combo box widget with a read-only line edit and a dropdown button."""
    selection_validated = Signal(bool)
    currentTextChanged = Signal(str)

    def __init__(
        self,
        parent: QWidget | None = None,
        list_items: Sequence[str] | None = None,
        placeholder: str | None = None,
    ):
        model = QStringListModel(list_items or [])
        super().__init__(
            parent=parent,
            model=model,
            placeholder=placeholder,
            read_only=True,
            show_button=True,
            button_icon=AppIcon.COMBOBOX_ARROW,
            completion_mode=None,
            layout_margins=(5, 5, 2, 5),
            layout_spacing=0,
            show_popup_on_focus=True,
        )
        self.setObjectName("ComboBox")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)

        # Style and object names
        self.line_edit.setObjectName("CBLineEdit")
        self.cb_btn.setObjectName("CBButton")

        # Signals
        self.line_edit.textChanged.connect(self._on_text_changed)
        self.completer.activated.connect(self._on_completer_activated)

    def _on_text_changed(self, text: str):
        if self.completer.popup().isVisible():
            return
        self.currentTextChanged.emit(text)

    def _on_completer_activated(self, text: str):
        # update text and emit selection; ensure currentTextChanged fires for filters
        self.line_edit.setText(text)
        self.selection_validated.emit(True)
        # explicitly emit currentTextChanged so connected filters update
        self.currentTextChanged.emit(text)
        # hide completer popup to allow textChanged signal processing
        try:
            self.completer.popup().hide()
        except Exception:
            pass
        if self.window().focusWidget() is self.line_edit:
            self.focusNextChild()

    def setCurrentText(self, text: str):
        super().setCurrentText(text)
        self.selection_validated.emit(bool(text))

    def setCurrentIndex(self, index: int):
        if 0 <= index < self.model.rowCount():
            text = self.model.data(self.model.index(index, 0), Qt.DisplayRole)
            self.line_edit.setText(text)
            self.selection_validated.emit(True)
        else:
            self.line_edit.clear()
            self.selection_validated.emit(False)

    def findText(self, text: str, flags: Qt.MatchFlags = Qt.MatchExactly) -> int:
        for row in range(self.model.rowCount()):
            item_text = self.model.data(self.model.index(row, 0), Qt.DisplayRole)
            if flags == Qt.MatchExactly:
                if item_text.lower() == text.lower():
                    return row
            elif flags & Qt.MatchFixedString:
                if item_text == text:
                    return row
            elif flags & Qt.MatchContains:
                if text.lower() in item_text.lower():
                    return row
        return -1

    def addItem(self, text: str):
        items = self.model.stringList()
        if text not in items:
            items.append(text)
            self.model.setStringList(items)
