"""ui/components/inputs/smart_combobox.py

This module defines a Smart ComboBox class that extends QComboBox.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from typing import Sequence

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtWidgets import QComboBox, QListView, QWidget 

from ui.iconkit import ToolButtonIcon
from config import SMART_COMBOBOX 

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

        # ── Initialize & Setup UI ──
        self.setObjectName("SmartComboBox")
        self.setEditable(editable)
        self.setStyleSheet("QComboBox::drop-down { border: none; width: 0px; }") 


        # ── Create Custom Button ──
        self.cb_btn = ToolButtonIcon(
            file_path = SMART_COMBOBOX["ICON_ARROW"]["FILE_PATH"],
            size      = SMART_COMBOBOX["ICON_ARROW"]["ICON_SIZE"],
            variant   = SMART_COMBOBOX["ICON_ARROW"]["DYNAMIC"],
        )

        # assign button properties
        self.cb_btn.setParent(self)
        self.cb_btn.setCursor(Qt.PointingHandCursor)

        self.cb_btn.clicked.connect(self.showPopup) # connect button to show popup

        # ── Create List ──
        list_view = QListView(self)
        list_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # use full enum path
        list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # use full enum path
        self.setView(list_view)

        # ── Populate List ──
        if list is not None: 
            self.populate_items(list)

        # ── Set Placeholder ──
        if placeholder: 
            self.set_placeholder(placeholder)

        self.currentTextChanged.connect(self.emit_validation) # connect signal to emit validation

    def emit_validation(self, text: str):
        """
        Emit a signal to indicate whether the current text is valid.

        Args:
            text (str): The current text in the combo box.
        """
        self.selection_validated.emit(bool(text))

    def populate_items(self, items_to_add: Sequence[str]):
        """
        Populate the combo box with a list of items.

        Args:
            items_to_add (Sequence[str]): List of items to add to the combo box.
        """
        self.clear()
        self.addItems(list(items_to_add))

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