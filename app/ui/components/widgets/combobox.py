"""app/ui/components/custom_combobox.py

This module defines a ComboBox widget that provides a read-only line edit
with a button to display a list of items. It uses a completer for auto-completion
and emits signals when a valid selection is made.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────
from typing import Sequence

from PySide6.QtCore import QEvent, QStringListModel, Qt, Signal
from PySide6.QtWidgets import (QApplication, QCompleter, QHBoxLayout,
                               QLineEdit, QWidget)

from app.config import CUSTOM_COMBOBOX
from app.ui.components.widgets.ct_tool_button import CTToolButton
from dev_tools import DebugLogger

# ── Constants ───────────────────────────────────────────────────────────────────────────
ICONS = CUSTOM_COMBOBOX["ICONS"]

# ── Class Definition: ComboBox ──────────────────────────────────────────────────────────
class ComboBox(QWidget):
    """Custom combo box widget with a read-only line edit and a button to show a
    list of items."""

    # ── Signals ─────────────────────────────────────────────────────────────────────────
    selection_validated = Signal(bool)
    currentTextChanged = Signal(str)

    def __init__(
        self,
        parent: QWidget | None = None,
        list_items: Sequence[str] | None = None,
        placeholder: str | None = None,
    ):
        """
        Initialize ComboBox.

        Args:
            parent (QWidget, optional): Parent widget.
            list_items (Sequence[str], optional): Initial list of items.
            placeholder (str, optional): Placeholder text for the combo box.
        """
        super().__init__(parent)
        self.setObjectName("ComboBox")
        self.setProperty("focused", True)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFocusPolicy(Qt.StrongFocus)

        self.model = QStringListModel(list_items or [])  # stored items in a model

        # ── Completer ──
        self.completer = QCompleter(self.model, self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.popup().setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.completer.popup().setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.completer.popup().setObjectName("CompleterPopup")

        # ── Input Field ──
        self.line_edit = QLineEdit(self)
        self.line_edit.setObjectName("CBLineEdit")
        self.line_edit.setPlaceholderText(placeholder)
        self.line_edit.setCompleter(self.completer)
        self.line_edit.setReadOnly(True)
        self.line_edit.installEventFilter(self)
        self.installEventFilter(self)

        # ── List Button ──
        self.cb_btn = CTToolButton(
            file_path = ICONS["ARROW"]["PATH"],
            icon_size = ICONS["ARROW"]["SIZE"],
            variant   = ICONS["ARROW"]["DYNAMIC"],
        )
        self.cb_btn.setObjectName("CBButton")
        self.cb_btn.setCursor(Qt.PointingHandCursor)

        # ── Signals ──
        self.line_edit.textChanged.connect(self._on_text_changed)
        self.cb_btn.clicked.connect(self._show_popup)
        self.completer.activated.connect(self._on_completer_activated)

        self._build_ui()

    def _build_ui(self):
        """Builds the layout and adds components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 2, 5)
        layout.setSpacing(0)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.cb_btn)

    def _on_text_changed(self, text: str):
        """Handles text changes in the line edit.

        Args:
            text (str): The new text in the line edit.
        """
        if self.completer.popup().isVisible():
            return  # prevent triggering while navigating the popup
        self.currentTextChanged.emit(text)

    def _on_completer_activated(self, text: str):
        """Handles activation of a completer item.

        Args:
            text (str): The text of the activated item.
        """
        self.line_edit.setText(text)
        self.selection_validated.emit(True)

        # only auto-tab if the event was triggered by keyboard
        focus_widget = self.window().focusWidget()
        if focus_widget == self.line_edit:
            self.focusNextChild()  # move to next widget in tab order

    def _show_popup(self):
        """Show the completer popup."""
        if not self.completer.popup().isVisible():
            self.line_edit.setFocus()
            self.completer.complete()
            self.setProperty("focused", True)
            self.update()  # refresh style

    def currentText(self) -> str:
        """Get the current text from the line edit.

        Returns:
            str: Current text in the line edit.
        """
        return self.line_edit.text()

    def setCurrentText(self, text: str):
        """Sets the current text in the line edit.

        Args:
            text (str): Text to set in the line edit.
        """
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
        """
        Adds a new item if it doesn't already exist.

        Args:
            text (str): The text to add.
        """
        items = self.model.stringList()
        if text not in items:
            items.append(text)
            self.model.setStringList(items)

    # ── Events ──────────────────────────────────────────────────────────────────────────
    def eventFilter(
            self,
            obj: QWidget,
            event: QEvent
        ) -> bool:
        """Expand the popup when the widget or line edit is clicked.

        Args:
            obj (QWidget): The object being filtered.
            event (QEvent): The event being processed.

        Returns:
            bool: True if the event was handled, False to allow normal processing.
        """
        if event.type() == QEvent.MouseButtonPress:
            if obj in (self, self.line_edit):
                self._show_popup()
                return False

        elif event.type() == QEvent.KeyPress:
            if obj is self.line_edit and self.completer.popup().isVisible():
                key = event.key()
                if key in (Qt.Key_Up, Qt.Key_Down, Qt.Key_Enter, Qt.Key_Return):
                    # forward the key event to the popup
                    QApplication.sendEvent(self.completer.popup(), event)
                    return True

        return super().eventFilter(obj, event)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.setProperty("focused", True)
        self.update()  # refresh style
        if not self.completer.popup().isVisible():
            self._show_popup()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.setProperty("focused", False)
        self.update()
