"""app/ui/components/widgets/combobox.py

Defines a custom ComboBox with read-only selection and integrated dropdown button.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from typing import Sequence

from PySide6.QtCore import QEvent, QStringListModel, Qt, Signal
from PySide6.QtWidgets import QCompleter, QHBoxLayout, QLineEdit, QWidget

from _dev_tools import DebugLogger
from app.style import Qss, Theme
from app.style.icon.config import Name

from .button import ToolButton
from .dropdown_menu import DropdownMenu


# ── ComboBox ────────────────────────────────────────────────────────────────────────────────────────────────
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
        self.setObjectName("ComboBox")
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setFocusPolicy(Qt.TabFocus) # Allow focus by Tab key only
        # Type-ahead navigation
        self.type_ahead_string = ""
        self.type_ahead_timer = None

        self._keyboard_selection = False # Track if selection was made via keyboard

        # Create model
        self.model = QStringListModel(list_items or [])

        # Create line edit (read-only)
        self.line_edit = QLineEdit(self)
        if placeholder:
            self.line_edit.setPlaceholderText(placeholder)
        self.line_edit.setReadOnly(True)
        self.line_edit.setObjectName("CBLineEdit")

        self.line_edit.setFocusPolicy(Qt.NoFocus)

        # Create dropdown button
        from app.style.icon import Type
        self.cb_btn = ToolButton(Type.PRIMARY, Name.ANGLE_DOWN)
        self.cb_btn.setIconSize(26, 26)
        self.cb_btn.setCursor(Qt.PointingHandCursor)
        self.cb_btn.setObjectName("CBButton")
        self.cb_btn.setProperty("tag", "Dropdown-Button")

        # Create dropdown menu
        self.dropdown_menu = DropdownMenu(
            parent=self,
            model=self.model
        )
        # Always show the full option list (no prefix filtering) when opened
        self.dropdown_menu.set_completion_mode(QCompleter.UnfilteredPopupCompletion)
        self.dropdown_menu.set_case_sensitivity(Qt.CaseInsensitive)

        # Set up layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 10, 5)
        layout.setSpacing(0)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.cb_btn)

        # Set unique scope property for CSS isolation testing
        unique_id = f"ComboBox_{id(self)}"
        self.setProperty("test_scope", unique_id)

        # Connect signals
        self.line_edit.textChanged.connect(self._on_text_changed)
        self.dropdown_menu.item_selected.connect(self._on_item_selected)
        self.dropdown_menu.popup_opened.connect(self._on_popup_opened)
        self.dropdown_menu.popup_closed.connect(self._on_popup_closed)
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

        # Only auto-advance for keyboard selection (Enter key)
        if self._keyboard_selection:
            self.focusNextChild()
            self._keyboard_selection = False  # Reset flag
        # For mouse selection, keep focus on this combobox

    def _show_popup(self):
        """Show the dropdown popup."""
        # Reset prefix so the popup isn't filtered by the current text
        self.dropdown_menu.completer.setCompletionPrefix("")
        self.dropdown_menu.show_popup(self.line_edit)

    def _on_popup_opened(self):
        print(f"[COMBOBOX {id(self)}] Popup opened")
        self.setProperty("dropdown", "true")
        self.style().unpolish(self)
        self.style().polish(self)

    def _on_popup_closed(self):
        print(f"[COMBOBOX {id(self)}] Popup closed")
        self.setProperty("dropdown", "false")
        self.style().unpolish(self)
        self.style().polish(self)

        # Force parent widget to repaint if it exists
        if self.parent():
            self.parent().update()

    def _handle_type_ahead(self, char: str):
        """Handle type-ahead navigation in the dropdown."""
        from PySide6.QtCore import QTimer

        # Add character to type-ahead string
        self.type_ahead_string += char.lower()

        # Reset timer
        if self.type_ahead_timer:
            self.type_ahead_timer.stop()

        # Clear type-ahead string after 1 second
        self.type_ahead_timer = QTimer()
        self.type_ahead_timer.timeout.connect(self._clear_type_ahead)
        self.type_ahead_timer.setSingleShot(True)
        self.type_ahead_timer.start(1000)  # 1 second timeout

        # Find and select matching item
        self._jump_to_matching_item()

    def _clear_type_ahead(self):
        """Clear the type-ahead string."""
        self.type_ahead_string = ""
        print(f"Type-ahead cleared")

    def _jump_to_matching_item(self):
        """Jump to the first item that starts with the type-ahead string."""
        popup = self.dropdown_menu.completer.popup()
        model = popup.model()

        # Search through all items
        for row in range(model.rowCount()):
            index = model.index(row, 0)
            item_text = model.data(index, Qt.DisplayRole)

            # Case-insensitive comparison
            if item_text.lower().startswith(self.type_ahead_string):
                # Set this as the current index
                popup.setCurrentIndex(index)
                # Ensure it's visible
                popup.scrollTo(index)
                print(f"Jumped to: {item_text} (type-ahead: '{self.type_ahead_string}')")
                return

        print(f"No match for: '{self.type_ahead_string}'")

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

    def clearSelection(self):
        """Clear the current selection and text."""
        self.line_edit.clear()
        self.selection_validated.emit(False)

    # ── Event Handling ──
    def eventFilter(self, obj, event):
        """Handle events for child widgets."""
        if obj is self.line_edit and event.type() == QEvent.MouseButtonPress:
            self._show_popup()
        return super().eventFilter(obj, event)

    def focusInEvent(self, event):
        """Handle focus in event."""
        super().focusInEvent(event)

        # Give visual feedback
        self.setProperty("has_focus", "true")
        self.style().unpolish(self)
        self.style().polish(self)

        # Log for debugging
        DebugLogger.log(f"ComboBox {self.objectName()} gained focus", "debug")

        # Auto-open dropdown when focused via keyboard (Tab)
        if event.reason() in (Qt.TabFocusReason, Qt.BacktabFocusReason):
            if not self.dropdown_menu.completer.popup().isVisible():
                from PySide6.QtCore import QTimer
                QTimer.singleShot(50, self._show_popup)

    def focusOutEvent(self, event):
        """Handle focus out event."""
        super().focusOutEvent(event)
        self.setProperty("has_focus", "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def keyPressEvent(self, event):
        """Handle key press events."""
        key = event.key()

        # Track if Enter/Return or Tab is pressed (keyboard selection)
        if key in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Tab):
            self._keyboard_selection = True

        # Handle Tab/Backtab whether popup is visible or not
        if key == Qt.Key_Tab:
            if self.dropdown_menu.completer.popup().isVisible():
                # Let dropdown_menu handle Tab selection, don't hide popup here
                # The dropdown_menu will handle selection and close the popup
                pass
            else:
                event.ignore()
                return
        elif key == Qt.Key_Backtab:
            if self.dropdown_menu.completer.popup().isVisible():
                self.dropdown_menu.hide_popup()
            event.ignore()
            return

        # Open dropdown on Space, Enter, or Down arrow
        if key in (Qt.Key_Space, Qt.Key_Return, Qt.Key_Enter, Qt.Key_Down):
            if not self.dropdown_menu.completer.popup().isVisible():
                self._show_popup()
            else:
                # Dropdown is visible and Enter was pressed - this will trigger selection
                if key in (Qt.Key_Return, Qt.Key_Enter):
                    self._keyboard_selection = True
            event.accept()
        # Handle type-ahead when dropdown is visible
        elif self.dropdown_menu.completer.popup().isVisible() and event.text():
            # Only process printable characters
            if event.text().isprintable():
                self._handle_type_ahead(event.text())
                event.accept()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        """Handle mouse press events on the ComboBox widget itself."""
        super().mousePressEvent(event)
        # Ensure this widget takes focus when clicked
        self.setFocus()
        DebugLogger.log(f"ComboBox clicked, setting focus", "debug")
