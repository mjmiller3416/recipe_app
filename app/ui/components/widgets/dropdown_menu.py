"""app/ui/components/widgets/dropdown_menu.py

Provides a reusable dropdown menu component for displaying selectable lists.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from typing import Sequence, Optional

from PySide6.QtCore import QAbstractItemModel, QEvent, QStringListModel, Qt, Signal
from PySide6.QtWidgets import QApplication, QCompleter, QWidget

from app.style import Qss, Theme
from dev_tools import DebugLogger


# ── DropdownMenu ─────────────────────────────────────────────────────────────────────────────
class DropdownMenu(QWidget):
    """
    Reusable dropdown menu component for displaying filtered selectable lists.

    This component provides just the dropdown functionality without any input field
    or button. It can be used by SmartLineEdit, ComboBox, and future multi-select widgets.

    Args:
        parent (QWidget, optional): Parent widget.
        model (QAbstractItemModel, optional): Model for the completer.
        list_items (Sequence[str], optional): List of strings to populate a QStringListModel.
        completion_mode (QCompleter.CompletionMode, optional): Mode for completer.
        allow_multi_select (bool): If True, supports multiple selections (for future checkbox lists).
    """

    item_selected = Signal(str)
    items_selected = Signal(list)  # For multi-select support
    popup_closed = Signal()

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

        # register for component-specific styling
        Theme.register_widget(self, Qss.DROPDOWN_MENU)

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
        Theme.register_widget(popup, Qss.DROPDOWN_MENU)

        # multi-select support
        self.allow_multi_select = allow_multi_select
        self.selected_items = set() if allow_multi_select else None

        # install event filter for popup
        self.completer.popup().installEventFilter(self)

        # connect signals
        self.completer.activated.connect(self._on_item_activated)

    def show_popup(self, line_edit: QWidget):
        """Show the dropdown popup attached to the given line edit."""
        if not self.completer.popup().isVisible():
            # set the completer's widget to the line edit for proper positioning
            self.completer.setWidget(line_edit)
            line_edit.setFocus()
            self.completer.complete()

    def hide_popup(self):
        """Hide the dropdown popup."""
        if self.completer.popup().isVisible():
            self.completer.popup().hide()
            self.popup_closed.emit()

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
        """Set a proxy model for advanced filtering (used by SmartLineEdit)."""
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

    def eventFilter(self, obj, event):
        """Handle events for the popup."""
        if obj is self.completer.popup():
            if event.type() == QEvent.KeyPress:
                key = event.key()

                # handle Tab key for selection
                if key == Qt.Key_Tab:
                    DebugLogger.log("Tab pressed in dropdown menu.", "debug")
                    current_index = self.completer.popup().currentIndex()
                    if current_index.isValid():
                        selected_text = current_index.data()
                        self.completer.activated.emit(selected_text)
                        return True

                # handle Escape key to close popup
                elif key == Qt.Key_Escape:
                    DebugLogger.log("Escape pressed in dropdown menu.", "debug")
                    self.hide_popup()
                    return True

                # let arrow keys and Enter/Return through
                elif key in (Qt.Key_Up, Qt.Key_Down, Qt.Key_Enter, Qt.Key_Return):
                    return False

            elif event.type() == QEvent.Hide:
                self.popup_closed.emit()

        return super().eventFilter(obj, event)

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
