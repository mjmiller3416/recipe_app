"""app/ui/components/widgets/filtered_dropdown_menu.py

Provides a dropdown menu that supports proxy model filtering for SmartLineEdit.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QAbstractProxyModel
from PySide6.QtWidgets import QCompleter

from .dropdown_menu import DropdownMenu


# ── FilteredDropdownMenu ─────────────────────────────────────────────────────────────────────
class FilteredDropdownMenu(DropdownMenu):
    """
    Dropdown menu that supports filtering through proxy models.

    This is specifically designed for SmartLineEdit which uses proxy models
    to filter the dropdown list based on user input.
    """

    def __init__(self, parent=None, proxy_model=None, completion_mode=None):
        # initialize with the proxy model
        super().__init__(
            parent=parent,
            model=proxy_model,
            completion_mode=completion_mode or QCompleter.UnfilteredPopupCompletion,
        )

        self.proxy_model = proxy_model

    def set_filter(self, filter_text: str):
        """Set filter text on the proxy model."""
        if self.proxy_model and hasattr(self.proxy_model, 'setFilterFixedString'):
            self.proxy_model.setFilterFixedString(filter_text)

    def clear_filter(self):
        """Clear the proxy model filter."""
        if self.proxy_model and hasattr(self.proxy_model, 'setFilterFixedString'):
            self.proxy_model.setFilterFixedString("")
