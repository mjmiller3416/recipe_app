"""ui/components/inputs/smart_combobox.py

This module defines a Smart ComboBox class that extends QComboBox.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from typing import Sequence

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QComboBox, QListView, QWidget

from config import SMART_COMBOBOX
from ui.iconkit import ToolButtonIcon
# Removed unused import IngredientService

# ── Class Definition: SmartComboBox ─────────────────────────────────────────────
class SmartComboBox(QComboBox):
    """
    Custom QComboBox that uses a QListView as the popup view and a themed dropdown arrow.
    Optionally accepts a list of items to populate on creation.
    """

    # ── Signals ─────────────────────────────────────────────────────────────────
    selection_validated = Signal(bool)  # emits when a valid selection is made

    def __init__(
        self,
        parent: QWidget | None = None, 
        list: Sequence[str] | None = None, 
        placeholder: str | None = None,     
        editable: bool = False,
    ):
        """
        Initialize SmartComboBox.
        
        Args:
            parent (QWidget, optional): Parent widget.
            items (Sequence[str], optional): List of items to populate the combo box.
            placeholder (str, optional): Placeholder text for the combo box.
            editable (bool): If True, allows editing of the combo box text.
        """
        super().__init__(parent)
        # ── Initialize Widget ──
        self.setObjectName("SmartComboBox")
        self.setEditable(editable)
        
        # ── Setup UI ──
        self.cb_btn = ToolButtonIcon(
            file_path = SMART_COMBOBOX["ICON_ARROW"]["FILE_PATH"],
            icon_size = SMART_COMBOBOX["ICON_ARROW"]["ICON_SIZE"],
            variant   = SMART_COMBOBOX["ICON_ARROW"]["DYNAMIC"],
        )

        # assign button properties
        self.cb_btn.setParent(self)
        self.cb_btn.setCursor(Qt.PointingHandCursor)
        self.cb_btn.clicked.connect(self.showPopup) # connect button to show popup

        # ── Create List ──
        list_view = QListView(self)
        list_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) 
        list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) 
        self.setView(list_view)

        # ── Populate List ──
        if list is not None: 
            self.populate_items(list)

        # ── Set Placeholder ──
        if placeholder: 
            self.set_placeholder(placeholder)

        self.currentTextChanged.connect(self.emit_validation) # connect signal to emit validation

        # Connect textChanged signal to _filter_items for live filtering
        if self.isEditable():
            self.lineEdit().textChanged.connect(self._filter_items)

    def emit_validation(self, text: str):
        """
        Emit a signal to indicate whether the current text is valid.

        Args:
            text (str): The current text in the combo box.
        """
        self.selection_validated.emit(bool(text))

    def _filter_items(self, text: str):
        """
        Filter the items in the combo box based on the input text.
        
        Args:
            text (str): The text to filter items by.
        """
        if hasattr(self, "_all_items"):
            self.blockSignals(True)
            self.clear()
            self.addItems([item for item in self._all_items if text.lower() in item.lower()])
            self.showPopup()
            self.blockSignals(False)

    def populate_items(self, items_to_add: Sequence[str]):
        """
        Populate the combo box with a list of items.

        Args:
            items_to_add (Sequence[str]): List of items to add to the combo box.
        """
        self._all_items = list(items_to_add)
        self.clear()
        self.addItems(self._all_items)

    def set_placeholder(self, placeholder: str):
        """
        Set the placeholder text for the combo box.

        Args:
            placeholder (str): The placeholder text to set.
        """

        if not self.isEditable():
            self.setPlaceholderText(placeholder)
            self.setCurrentIndex(-1)
        else:
            self.lineEdit().setPlaceholderText(placeholder)
            self.setCurrentIndex(-1)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        # align it right inside the combo box frame
        x = self.width() - self.cb_btn.width()  # adjust for margins
        y = (self.height() - self.cb_btn.height()) // 2
        self.cb_btn.move(x, y)
        self.cb_btn.raise_()