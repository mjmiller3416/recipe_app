"""ui/components/inputs/custom_combobox.py

This module defines a CustomComboBox class that extends QComboBox.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from typing import Sequence

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QComboBox, QListView

# ── Class Definition ────────────────────────────────────────────────────────────
class CustomComboBox(QComboBox):
    """
    Custom QComboBox that uses a QListView as the popup view.
    This allows for a more customized appearance and behavior.
    
    Optionally accepts a list of items to populate on creation.
    """

    # ── Signals ─────────────────────────────────────────────────────────────────
    cb_validated = Signal(bool)  # Emits when a valid selection is made

    def __init__(
        self, 
        list: Sequence[str] = None, 
        placeholder: str = None,
        editable: bool = False,
        parent=None, 
    ):
        """
        Initialize the CustomComboBox.

        Args:
            parent (QWidget): The parent widget.
            values (list[str]: optional): A list of values to populate the combobox with.
            editable (bool): 
        """
        super().__init__(parent)

        self.setObjectName("CustomComboBox")
        self.setEditable(editable)

        # ── Create List View ──
        list_view = QListView(self)
        list_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setView(list_view)

        # populate items
        if list: self.populate_combobox(list)

        # set placeholder
        if placeholder:
            self.setPlaceholderText(placeholder)
            self.setCurrentIndex(-1)

        self.currentTextChanged.connect(self.emit_validation) # connect signals

    def emit_validation(self, text):
        """Emit validation signal based on selection text."""
        self.cb_validated.emit(bool(text))

    def populate_combobox(combobox: QComboBox, *values):
        """
        Populates a QComboBox with the provided values.

        Args:
            combobox (QComboBox): The combobox to populate.
            *values (str or list): A list of values or multiple string arguments.
        """
        if len(values) == 1 and isinstance(values[0], list):
            values = values[0]  # Unpack list if a single list argument is passed

        combobox.clear()
        combobox.addItems(values)
