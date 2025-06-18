"""ui/components/inputs/custom_combobox.py

This module defines a CustomComboBox widget that provides a read-only line edit
with a button to display a list of items. It uses a completer for auto-completion
and emits signals when a valid selection is made.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from typing import Sequence

from PySide6.QtCore import QStringListModel, Qt, Signal
from PySide6.QtWidgets import QCompleter, QHBoxLayout, QLineEdit, QWidget

from config import CUSTOM_COMBOBOX, STYLES
from core.utils import DebugLogger
from ui.widgets import CTButton


# ── Class Definition: CustomComboBox ─────────────────────────────────────────────
class CustomComboBox(QWidget):
    """Custom combo box widget with a read-only line edit and a button to show a 
    list of items."""

    # ── Signals ─────────────────────────────────────────────────────────────────
    selection_validated = Signal(bool)
    currentTextChanged = Signal(str)

    def __init__(
        self,
        parent: QWidget | None = None, 
        list_items: Sequence[str] | None = None, 
        placeholder: str | None = None,     
    ):
        """
        Initialize CustomComboBox.

        Args:
            parent (QWidget, optional): Parent widget.
            list_items (Sequence[str], optional): Initial list of items.
            placeholder (str, optional): Placeholder text for the combo box.
        """
        super().__init__(parent)
        self.setObjectName("CustomComboBox")
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.model = QStringListModel(list_items or [])  # 🔹 Store the list model

        # ── Completer ──
        self.completer = QCompleter(self.model, self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.popup().setObjectName("CompleterPopup")

        # ── Input Field ──
        self.line_edit = QLineEdit(self) 
        self.line_edit.setObjectName("LineEdit")
        self.line_edit.setPlaceholderText(placeholder)
        self.line_edit.setCompleter(self.completer)
        self.line_edit.setReadOnly(True)

        # ── List Button ──
        self.cb_btn = CTButton(
            file_path = CUSTOM_COMBOBOX["ICON_ARROW"]["FILE_PATH"],
            icon_size = CUSTOM_COMBOBOX["ICON_ARROW"]["ICON_SIZE"],
            variant   = CUSTOM_COMBOBOX["ICON_ARROW"]["DYNAMIC"],
        )
        self.cb_btn.setObjectName("Button")
        self.cb_btn.setCursor(Qt.PointingHandCursor)

        # ── Signals ──
        self.line_edit.textChanged.connect(self._on_text_changed)
        self.cb_btn.clicked.connect(self._show_popup)

        self._build_ui()

    def _build_ui(self):
        """Builds the layout and adds components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 2, 5)
        layout.setSpacing(0)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.cb_btn)

    def _on_text_changed(self, text: str):
        self.currentTextChanged.emit(text)

    def _show_popup(self):
        """Display the completer popup."""
        self.completer.complete()

    def currentText(self) -> str:
        return self.line_edit.text()

    def setCurrentText(self, text: str):
        self.line_edit.setText(text)
        self.selection_validated.emit(bool(text))

    def setCurrentIndex(self, index: int):
        """
        Sets the current text based on index in the model.

        Args:
            index (int): Index to select.
        """
        if 0 <= index < self.model.rowCount():
            text = self.model.data(self.model.index(index, 0), Qt.DisplayRole)
            self.line_edit.setText(text)
            self.selection_validated.emit(True)
        else:
            self.line_edit.clear()
            self.selection_validated.emit(False)

    def findText(self, text: str, flags: Qt.MatchFlags = Qt.MatchExactly) -> int:
        """
        Searches for a string in the model.

        Args:
            text (str): String to find.
            flags (Qt.MatchFlags): Match mode flags.

        Returns:
            int: Index of found string or -1.
        """
        for row in range(self.model.rowCount()):
            item_text = self.model.data(self.model.index(row, 0), Qt.DisplayRole)
            if flags & Qt.MatchExactly and item_text.lower() == text.lower():
                return row
            if flags & Qt.MatchFixedString and item_text == text:
                return row
            if flags & Qt.MatchContains and text.lower() in item_text.lower():
                return row
        return -1

    def addItem(self, text: str):
        """
        Adds a new item if it doesn't already exist.

        Args:
            text (str): The text to add.
        """
        items = self.model.stringList()
        if text not in items:
            items.append(text)
            self.model.setStringList(items)
