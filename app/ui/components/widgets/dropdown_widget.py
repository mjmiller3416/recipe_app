"""app/ui/components/widgets/dropdown_widget.py

Provides a base widget combining a QLineEdit, a QCompleter, and an optional
dropdown arrow button, with shared event handling for popup navigation.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from typing import Sequence

from PySide6.QtCore import QEvent, QStringListModel, Qt, Signal
from PySide6.QtWidgets import (QApplication, QCompleter, QHBoxLayout,
                               QLineEdit, QWidget)

from dev_tools import DebugLogger

from .tool_button import ToolButton


# ── Dropdown Widget ──────────────────────────────────────────────────────────────────────────
class DropDown(QWidget):
    """
    Base widget for a line edit with a dropdown completer and optional button.

    Args:
        parent (QWidget, optional): Parent widget.
        model (QAbstractItemModel, optional): Model for the completer.
        list_items (Sequence[str], optional): List of strings to populate a QStringListModel.
        placeholder (str, optional): Placeholder text for the line edit.
        read_only (bool): If True, makes the line edit read-only.
        show_button (bool): If True, displays a dropdown arrow button.
        button_icon (QIcon, optional): Icon for the dropdown button.
        completion_mode (QCompleter.CompletionMode, optional): Mode for completer.
        layout_margins (tuple[int, int, int, int]): Contents margins for layout.
        layout_spacing (int): Spacing between layout items.
        show_popup_on_focus (bool): Automatically open popup on focus.
    """
    currentTextChanged = Signal(str)
    selectionActivated = Signal(str)

    def __init__(
        self,
        parent: QWidget = None,
        model=None,
        list_items: Sequence[str] = None,
        placeholder: str = None,
        read_only: bool = False,
        show_button: bool = False,
        button_icon=None,
        completion_mode=None,
        layout_margins=(0, 0, 0, 0),
        layout_spacing=0,
        show_popup_on_focus: bool = False,
    ):
        super().__init__(parent)
        if model is not None:
            self.model = model
        else:
            self.model = QStringListModel(list_items or [])
        self.completer = QCompleter(self.model, self)
        if completion_mode is not None:
            self.completer.setCompletionMode(completion_mode)
        self.completer.popup().setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.completer.popup().setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.completer.popup().setObjectName("CompleterPopup")

        self.line_edit = QLineEdit(self)
        if placeholder:
            self.line_edit.setPlaceholderText(placeholder)
        self.line_edit.setCompleter(self.completer)
        self.line_edit.setReadOnly(read_only)

        self.show_button = show_button
        if show_button and button_icon is not None:
            from app.appearance.icon import Type
            self.cb_btn = ToolButton(Type.DEFAULT)
            self.cb_btn.setIcon(button_icon)
            self.cb_btn.setCursor(Qt.PointingHandCursor)
            self.cb_btn.clicked.connect(self._show_popup)

        self.installEventFilter(self)
        self.line_edit.installEventFilter(self)
        self.completer.popup().installEventFilter(self)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(*layout_margins)
        layout.setSpacing(layout_spacing)
        layout.addWidget(self.line_edit)
        if show_button and hasattr(self, "cb_btn"):
            layout.addWidget(self.cb_btn)

        self.show_popup_on_focus = show_popup_on_focus

    def _show_popup(self):
        if not self.completer.popup().isVisible():
            self.line_edit.setFocus()
            self.completer.complete()
            self.update()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if obj in (self, self.line_edit) or getattr(self, "cb_btn", None) is obj:
                self._show_popup()
                return False
        if event.type() == QEvent.KeyPress:
            key = event.key()
            if obj is self.line_edit:
                if self.completer.popup().isVisible() and key in (
                    Qt.Key_Up,
                    Qt.Key_Down,
                    Qt.Key_Enter,
                    Qt.Key_Return,
                ):
                    QApplication.sendEvent(self.completer.popup(), event)
                    return True
                if key == Qt.Key_Escape:
                    DebugLogger.log("Esc pressed.", "debug")
                    self.completer.popup().hide()
                    return True
            if obj is self.completer.popup() and key == Qt.Key_Tab:
                DebugLogger.log("Tab pressed.", "debug")
                current_index = self.completer.popup().currentIndex()
                if current_index.isValid():
                    selected_text = current_index.data()
                    self.completer.activated.emit(selected_text)
                    self.completer.popup().hide()
                    return True
        return super().eventFilter(obj, event)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.setProperty("focused", True)
        self.update()
        if self.show_popup_on_focus:
            self._show_popup()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.setProperty("focused", False)
        self.update()

    def currentText(self) -> str:
        return self.line_edit.text()

    def setCurrentText(self, text: str):
        self.line_edit.setText(text)
