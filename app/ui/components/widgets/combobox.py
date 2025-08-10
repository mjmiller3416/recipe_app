"""app/ui/components/widgets/combobox.py

Defines a custom ComboBox with read-only selection and integrated dropdown button.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from typing import Sequence

from PySide6.QtCore import QEvent, QStringListModel, Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QWidget

from app.style.icon.config import Name
from .dropdown_menu import DropdownMenu
from .button import ToolButton


# ── ComboBox ─────────────────────────────────────────────────────────────────────────────────
class ComboBox(QWidget):
    """Custom combo box widget with a read-only line edit and a dropdown button."""
    selection_validated = Signal(bool)
    currentTextChanged = Signal(str)

    def __init__(
        self,
        parent: QWidget | None = None,
        list_items: Sequence[str] | None = None,
        placeholder: str | None = None,
    ):
        super().__init__(parent)

        # Create model
        self.model = QStringListModel(list_items or [])

        # Create line edit (read-only)
        self.line_edit = QLineEdit(self)
        if placeholder:
            self.line_edit.setPlaceholderText(placeholder)
        self.line_edit.setReadOnly(True)
        self.line_edit.setObjectName("CBLineEdit")

        # Create dropdown button
        from app.style.icon import Type
        self.cb_btn = ToolButton(Type.DEFAULT, Name.ANGLE_DOWN)
        self.cb_btn.setCursor(Qt.PointingHandCursor)
        self.cb_btn.setObjectName("CBButton")

        # Create dropdown menu
        self.dropdown_menu = DropdownMenu(
            parent=self,
            model=self.model
        )
        self.dropdown_menu.set_case_sensitivity(Qt.CaseInsensitive)

        # Set up layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 2, 5)
        layout.setSpacing(0)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.cb_btn)

        # Widget configuration
        self.setObjectName("ComboBox")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFocusPolicy(Qt.StrongFocus)

        # Connect signals
        self.line_edit.textChanged.connect(self._on_text_changed)
        self.dropdown_menu.item_selected.connect(self._on_item_selected)
        self.cb_btn.clicked.connect(self._show_popup)

        # Install event filter for mouse clicks
        self.line_edit.installEventFilter(self)

    @property
    def completer(self):
        """Access to the dropdown menu's completer for backward compatibility."""
        return self.dropdown_menu.completer

    def _on_text_changed(self, text: str):
        """Handle text changes in the line edit."""
        if self.dropdown_menu.completer.popup().isVisible():
            return
        self.currentTextChanged.emit(text)

    def _on_item_selected(self, text: str):
        """Handle item selection from the dropdown menu."""
        self.line_edit.setText(text)
        self.selection_validated.emit(True)
        self.currentTextChanged.emit(text)

        # Move focus to next widget
        if self.window().focusWidget() is self.line_edit:
            self.focusNextChild()

    def _show_popup(self):
        """Show the dropdown popup."""
        self.dropdown_menu.show_popup(self.line_edit)

    def eventFilter(self, obj, event):
        """Handle events for child widgets."""
        if obj is self.line_edit and event.type() == QEvent.MouseButtonPress:
            self._show_popup()
        return super().eventFilter(obj, event)

    def setCurrentText(self, text: str):
        """Set the current text in the line edit."""
        self.line_edit.setText(text)
        self.selection_validated.emit(bool(text))

    def currentText(self) -> str:
        """Get the current text from the line edit."""
        return self.line_edit.text()

    def setCurrentIndex(self, index: int):
        """Set the current selection by index."""
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
