"""ui/components/inputs/custom_combobox.py

This module defines a CustomComboBox widget that provides a read-only line edit
with a button to display a list of items. It uses a completer for auto-completion
and emits signals when a valid selection is made.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from typing import Sequence

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QLineEdit, QCompleter, QHBoxLayout

from config import CUSTOM_COMBOBOX
from ui.iconkit import ToolButtonIcon
from services.ingredient_service import IngredientService
from style_manager import WidgetLoader
from config import STYLES
from core.helpers import DebugLogger

# ── Class Definition: CustomComboBox ─────────────────────────────────────────────
class CustomComboBox(QWidget):
    """Custom combo box widget with a read-only line edit and a button to show a 
    list of items."""

    # ── Signals ─────────────────────────────────────────────────────────────────
    selection_validated = Signal(bool)  # emits when a valid selection is made

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
            items (Sequence[str], optional): List of items to populate the combo box.
            placeholder (str, optional): Placeholder text for the combo box.
        """
        super().__init__(parent)
        self.setObjectName("CustomComboBox")
        self.setAttribute(Qt.WA_StyledBackground, True)

        # ── Completer ──
        self.completer = QCompleter(list_items, self)  # create a completer for the combo box
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        popup = self.completer.popup()
        popup.setObjectName("CompleterPopup")

        # ── Input Field ──
        self.line_edit = QLineEdit(self) 
        self.line_edit.setObjectName("LineEdit")
        self.line_edit.setPlaceholderText(placeholder)
        self.line_edit.setCompleter(self.completer)
        self.line_edit.setReadOnly(True)

        # ── List Button ──
        self.cb_btn = ToolButtonIcon(
            file_path = CUSTOM_COMBOBOX["ICON_ARROW"]["FILE_PATH"],
            icon_size = CUSTOM_COMBOBOX["ICON_ARROW"]["ICON_SIZE"],
            variant   = CUSTOM_COMBOBOX["ICON_ARROW"]["DYNAMIC"],
        )
        self.cb_btn.setObjectName("Button")
        self.cb_btn.setCursor(Qt.PointingHandCursor)
        self.cb_btn.clicked.connect(self._show_popup) # connect button to show popup

        self._build_ui()  # build the UI components

    def _build_ui(self):
        """
        Build the UI components for the CustomComboBox.
        """
        # Set up the layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 2, 5)
        layout.setSpacing(0)

        # Add the line edit and button to the layout
        layout.addWidget(self.line_edit)
        layout.addWidget(self.cb_btn)

    def _show_popup(self):
        """Show the popup with the list of items."""
        self.completer.complete()

    def emit_validation(self, text: str):
        """
        Emit a signal to indicate whether the current text is valid.

        Args:
            text (str): The current text in the combo box.
        """
        self.selection_validated.emit(bool(text))
