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

                # Don't handle Tab/Backtab here - let the parent ComboBox handle it
                if key in (Qt.Key_Tab, Qt.Key_Backtab):
                    # Ignore tab events in the popup
                    event.ignore()
                    return True  # Block the event from the popup

                # Handle Escape key to close popup
                elif key == Qt.Key_Escape:
                    DebugLogger.log("Escape pressed in dropdown menu.", "debug")
                    self.hide_popup()
                    return True

            elif event.type() == QEvent.Hide:
                self.popup_closed.emit()

        return super().eventFilter(obj, event)
