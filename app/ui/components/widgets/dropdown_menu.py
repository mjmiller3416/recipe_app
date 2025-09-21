"""app/ui/components/widgets/dropdown_menu.py

Provides a reusable dropdown menu component for displaying selectable lists.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from typing import Optional, Sequence

from PySide6.QtCore import (QAbstractItemModel, QEvent, QStringListModel, Qt,
                            Signal)
from PySide6.QtWidgets import QCompleter, QWidget

from _dev_tools import DebugLogger
from app.style import Qss, Theme


# ── Dropdown Menu ───────────────────────────────────────────────────────────────────────────────────────────
class DropdownMenu(QWidget):
    """
    Reusable dropdown menu component for displaying filtered selectable lists.

    This component provides just the dropdown functionality without any input field
    or button. It can be used by SmartInput, ComboBox, and future multi-select widgets.

    Args:
        parent (QWidget, optional): Parent widget.
        model (QAbstractItemModel, optional): Model for the completer.
        list_items (Sequence[str], optional): List of strings to populate a QStringListModel.
        completion_mode (QCompleter.CompletionMode, optional): Mode for completer.
        allow_multi_select (bool): If True, supports multiple selections (for future checkbox lists).
    """

    item_selected = Signal(str)
    items_selected = Signal(list)  # For multi-select support
    popup_opened = Signal()
    popup_closed = Signal()
    tab_pressed = Signal(int, str)  # Emits (row_count, highlighted_text or empty string)

    def __init__(
        self,
        parent: QWidget = None,
        model: Optional[QAbstractItemModel] = None,
        list_items: Optional[Sequence[str]] = None,
        completion_mode: Optional[QCompleter.CompletionMode] = None,
        allow_multi_select: bool = False,
    ):
        super().__init__(parent)

        # Set object name for styling
        self.setObjectName("DropdownMenu")

        # set up model
        if model is not None:
            self.model = model
        else:
            self.model = QStringListModel(list_items or [])

        # create completer
        self.completer = QCompleter(self.model, self)
        if completion_mode is not None:
            self.completer.setCompletionMode(completion_mode)

        # configure popup with proper parent isolation
        popup = self.completer.popup()
        popup.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        popup.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        popup.setObjectName("DropdownMenuPopup")

        # Keep popup connected to parent for styling, but set as top-level for proper display
        popup.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)

        # Apply theme styling to the popup
        popup.setAttribute(Qt.WA_StyledBackground, True)

        # multi-select support
        self.allow_multi_select = allow_multi_select
        self.selected_items = set() if allow_multi_select else None

        # install event filter for popup
        self.completer.popup().installEventFilter(self)

        # connect signals
        self.completer.activated.connect(self._on_item_activated)

    def show_popup(self, line_edit: QWidget):
        print(f"\n[DROPDOWN {id(self)}] show_popup called")

        if not self.completer.popup().isVisible():
            self.completer.setWidget(line_edit)

            # Set popup to not interfere with tab navigation
            popup = self.completer.popup()
            popup.setFocusPolicy(Qt.NoFocus)  # Add this line

            self.completer.complete()

            print(f"[DROPDOWN {id(self)}] Emitting popup_opened signal...")
            self.popup_opened.emit()
            print(f"[DROPDOWN {id(self)}] Signal emitted, continuing...")

        print(f"[DROPDOWN {id(self)}] show_popup complete\n")

    def hide_popup(self):
        """Hide the dropdown popup."""
        if self.completer.popup().isVisible():
            self.completer.popup().hide()
            self.popup_closed.emit()
            print("Popup closed.")

    def set_filter(self, filter_text: str):
        """Set filter text for the completer model (if supported)."""
        # Check if the model is a proxy model with filtering capability
        if hasattr(self.model, 'setFilterFixedString'):
            self.model.setFilterFixedString(filter_text)
        elif hasattr(self.model, 'setFilterRegularExpression'):
            self.model.setFilterRegularExpression(filter_text)

    def clear_filter(self):
        """Clear any active filter."""
        self.set_filter("")

    def set_proxy_model(self, proxy_model):
        """Set a proxy model for advanced filtering (used by SmartInput)."""
        self.model = proxy_model
        self.completer.setModel(proxy_model)

    def get_model(self):
        """Get the current model (useful for setting source models)."""
        return self.model

    def _on_item_activated(self, text: str):
        """Handle item activation from the completer."""
        if self.allow_multi_select:
            # toggle selection for multi-select
            if text in self.selected_items:
                self.selected_items.remove(text)
            else:
                self.selected_items.add(text)
            self.items_selected.emit(list(self.selected_items))
            DebugLogger.log(f"Multi-select: {list(self.selected_items)}")
        else:
            # single selection
            self.item_selected.emit(text)
            self.hide_popup()
            DebugLogger.log(f"Item selected: {text}")

    def get_selected_items(self) -> list:
        """Get currently selected items (for multi-select mode)."""
        if self.allow_multi_select:
            return list(self.selected_items)
        return []

    def clear_selection(self):
        """Clear all selections (for multi-select mode)."""
        if self.allow_multi_select:
            self.selected_items.clear()
            self.items_selected.emit([])

    def set_completion_mode(self, mode: QCompleter.CompletionMode):
        """Set the completion mode for the completer."""
        self.completer.setCompletionMode(mode)

    def set_case_sensitivity(self, sensitivity: Qt.CaseSensitivity):
        """Set case sensitivity for the completer."""
        self.completer.setCaseSensitivity(sensitivity)

    def eventFilter(self, obj, event):
        """Handle events for the popup."""
        if obj is self.completer.popup():
            if event.type() == QEvent.KeyPress:
                key = event.key()

                # Track Enter key for keyboard selection
                if key in (Qt.Key_Enter, Qt.Key_Return):
                    # Tell parent ComboBox this is a keyboard selection
                    if self.parent() and hasattr(self.parent(), '_keyboard_selection'):
                        self.parent()._keyboard_selection = True
                    return False  # Let completer handle the actual selection

                # Handle Tab key to select highlighted option and navigate
                elif key == Qt.Key_Tab:
                    # Special handling for SmartInput parent - emit signal instead of handling directly
                    if self.parent() and self.parent().__class__.__name__ == 'SmartInput':
                        popup = self.completer.popup()
                        model = popup.model()
                        row_count = model.rowCount() if model else 0

                        # Get highlighted text if any
                        highlighted_text = ""
                        if popup.currentIndex().isValid():
                            highlighted_text = popup.currentIndex().data(Qt.DisplayRole)

                        # Emit signal with row count and highlighted text
                        self.tab_pressed.emit(row_count, highlighted_text)
                        self.hide_popup()
                        return True

                    # Original ComboBox behavior - unchanged
                    # Get the currently highlighted index
                    popup = self.completer.popup()
                    current_index = popup.currentIndex()

                    if current_index.isValid():
                        # Get the highlighted text
                        selected_text = current_index.data(Qt.DisplayRole)

                        # Tell parent ComboBox this is a keyboard selection
                        if self.parent() and hasattr(self.parent(), '_keyboard_selection'):
                            self.parent()._keyboard_selection = True

                        # Trigger the selection and explicitly hide popup
                        self.item_selected.emit(selected_text)
                        self.hide_popup()  # Explicitly hide popup after selection

                        return True  # We handled the selection
                    else:
                        # No selection, just close popup and navigate
                        self.hide_popup()
                        # Post the event to the parent widget (ComboBox)
                        if self.parent():
                            from PySide6.QtCore import QCoreApplication
                            QCoreApplication.postEvent(self.parent(), event.clone())
                        return True

                # For Backtab, close popup and let parent handle navigation
                elif key == Qt.Key_Backtab:
                    self.hide_popup()
                    # Post the event to the parent widget (ComboBox)
                    if self.parent():
                        from PySide6.QtCore import QCoreApplication
                        QCoreApplication.postEvent(self.parent(), event.clone())
                    return True  # We handled it by closing and reposting

                # Handle Escape key to close popup
                elif key == Qt.Key_Escape:
                    DebugLogger.log("Escape pressed in dropdown menu.", "debug")
                    self.hide_popup()
                    return True

                # Pass printable characters to parent for type-ahead (only for ComboBox)
                elif event.text() and event.text().isprintable():
                    # Check if parent is a ComboBox (has type_ahead_string attribute)
                    if self.parent() and hasattr(self.parent(), 'type_ahead_string'):
                        # Let the parent ComboBox handle type-ahead
                        from PySide6.QtCore import QCoreApplication
                        QCoreApplication.postEvent(self.parent(), event.clone())
                        return True  # Prevent default handling
                    # For SmartInput, let it filter naturally
                    return False

                # Let arrow keys and Enter work normally for selection
                elif key in (Qt.Key_Up, Qt.Key_Down, Qt.Key_Enter, Qt.Key_Return):
                    return False  # Let completer handle these

            elif event.type() == QEvent.Hide:
                self.popup_closed.emit()

        return super().eventFilter(obj, event)
