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

        # Track current selection row
        self._current_popup_row = -1

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

        # Create DropdownMenu
        self.dropdown_menu = DropdownMenu(
            parent=self,
            completion_mode=QCompleter.UnfilteredPopupCompletion
        )
        self.dropdown_menu.set_proxy_model(self.proxy)
        self.dropdown_menu.set_case_sensitivity(Qt.CaseInsensitive)

        # IMPORTANT: Don't set the completer on the line edit directly
        # We'll manage the popup manually
        self.dropdown_menu.completer.setWidget(self)

        # Fix minimum rows
        self.dropdown_menu.completer.setMaxVisibleItems(7)

        # Ensure popup resizes to content
        popup = self.dropdown_menu.completer.popup()
        popup.installEventFilter(self)
        from PySide6.QtWidgets import QAbstractScrollArea
        popup.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        # Disconnect the default activated behavior
        # We'll handle selection manually
        try:
            self.dropdown_menu.completer.activated[str].disconnect()
        except:
            pass  # Nothing to disconnect

        # Connect our custom handler
        self.dropdown_menu.completer.activated[str].connect(self._on_completer_activated)

        # connect other signals
        self.textEdited.connect(self._on_text_changed)
        self.textChanged.connect(self._on_text_changed_filter_only)
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

    def _on_item_highlighted(self, text: str):
        """Handle item highlighting without auto-selecting."""
        # Just track that we're navigating, don't auto-fill the text
        self._navigating_with_arrows = True

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
        """Handle user typing - show and filter dropdown."""
        self.dropdown_menu.set_filter(text)
        self.currentTextChanged.emit(text)

        # Show dropdown if there are matches
        if not self.dropdown_menu.completer.popup().isVisible() and text:
            self.dropdown_menu.completer.complete()

        # Resize popup after filtering
        from PySide6.QtCore import QTimer
        QTimer.singleShot(10, self._resize_popup)  # Small delay to let filter apply

        DebugLogger.log(f"Text changed: {text}", "debug")

    def _on_text_changed_filter_only(self, text: str):
        """Update filter without showing popup (for programmatic changes)."""
        if not self.hasFocus():
            return
        self.dropdown_menu.set_filter(text)

    def _on_completer_activated(self, text: str):
        """Handle explicit selection from dropdown."""
        self.setText(text)
        self.item_selected.emit(text)
        self.dropdown_menu.hide_popup()
        QTimer.singleShot(0, self.focusNextChild)

    def _resize_popup(self):
        """Manually resize popup to fit content."""
        popup = self.dropdown_menu.completer.popup()
        if not popup.isVisible():
            return

        # Get the number of visible items
        model = popup.model()
        visible_items = model.rowCount()

        if visible_items == 0:
            self.dropdown_menu.hide_popup()
            return

        # Calculate height based on visible items (with a max)
        item_height = popup.sizeHintForRow(0) if visible_items > 0 else 30
        max_visible = min(visible_items, 7)  # Show max 7 items

        # Calculate total height including some padding
        total_height = (item_height * max_visible) + 10

        # Set the popup size
        popup.setFixedHeight(total_height)

        # Also adjust width to match the input field
        popup.setFixedWidth(self.width())

        # Disable scrollbars for small lists to prevent scrolling
        if visible_items <= 3:
            popup.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            popup.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        else:
            popup.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            popup.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def currentText(self) -> str:
        """Get the current text from the line edit."""
        return self.text()

    # ── Event Handlers ──
    def focusInEvent(self, event):
        """Handle focus in event - show dropdown on tab focus."""
        super().focusInEvent(event)

        # Auto-show dropdown when focused via Tab
        if event.reason() in (Qt.TabFocusReason, Qt.BacktabFocusReason):
            # Show all items when first focused
            self.dropdown_menu.clear_filter()
            if not self.dropdown_menu.completer.popup().isVisible():
                from PySide6.QtCore import QTimer
                QTimer.singleShot(50, lambda: self.dropdown_menu.completer.complete())

    def focusOutEvent(self, event: QEvent):
        """Handle focus out - hide popup but don't clear text."""
        # Hide the dropdown when focus is lost
        self.dropdown_menu.hide_popup()
        # Don't call _handle_submission() which would clear the text
        super().focusOutEvent(event)

    def eventFilter(self, obj, event):
        """Filter events on the popup to prevent cycling."""
        popup = self.dropdown_menu.completer.popup()

        if obj == popup and event.type() == QEvent.KeyPress:
            key = event.key()

            if key in (Qt.Key_Up, Qt.Key_Down):
                model = popup.model()
                current = popup.currentIndex()
                row_count = model.rowCount()

                if row_count == 0:
                    return True

                current_row = current.row() if current.isValid() else -1

                # Store the current scroll position before changing selection
                scrollbar = popup.verticalScrollBar()
                scroll_pos = scrollbar.value() if scrollbar else 0

                if key == Qt.Key_Down:
                    if current_row < row_count - 1:
                        new_index = model.index(current_row + 1, 0)
                        popup.setCurrentIndex(new_index)
                        # Restore scroll position for small lists
                        if row_count <= 3 and scrollbar:
                            scrollbar.setValue(scroll_pos)
                    return True
                elif key == Qt.Key_Up:
                    if current_row > 0:
                        new_index = model.index(current_row - 1, 0)
                        popup.setCurrentIndex(new_index)
                        # Restore scroll position for small lists
                        if row_count <= 3 and scrollbar:
                            scrollbar.setValue(scroll_pos)
                    elif current_row == -1 and row_count > 0:
                        new_index = model.index(row_count - 1, 0)
                        popup.setCurrentIndex(new_index)
                    return True

        return super().eventFilter(obj, event)

    def resizeEvent(self, event):
        """Handle resize events."""
        super().resizeEvent(event)
