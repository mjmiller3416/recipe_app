"""app/ui/views/recipe_browser/_filter_bar.py

A filter bar for filtering recipes by category, cuisine, and preparation time.
"""

# ── Imports ──
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QCheckBox

from app.config import RECIPE_CATEGORIES, SORT_OPTIONS
from app.ui.components.widgets import ComboBox


class FilterBar(QWidget):
    """A filter bar for filtering recipes by category, cuisine, and preparation time."""

    filters_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._set_defaults()
        self._connect_signals()

    def _build_ui(self):
        # filter and sort controls
        self.lyt_main = QHBoxLayout()
        self.lyt_main.setSpacing(10)

        self.cb_filter = ComboBox(list_items=RECIPE_CATEGORIES, placeholder="Filter")
        self.cb_sort = ComboBox(list_items=SORT_OPTIONS, placeholder="Sort")
        self.chk_favorites = QCheckBox("Show Favorites Only")

        self.lyt_main.addWidget(self.cb_filter)
        self.lyt_main.addWidget(self.cb_sort)
        self.lyt_main.addWidget(self.chk_favorites)

        self.setLayout(self.lyt_main)

    def _connect_signals(self):
        # connect signals
        self.cb_filter.currentTextChanged.connect(lambda: self.filters_changed.emit())
        self.cb_sort.currentTextChanged.connect(lambda: self.filters_changed.emit())
        self.chk_favorites.stateChanged.connect(lambda: self.filters_changed.emit())

    def _set_defaults(self):
        """Set default filter values."""
        self.cb_sort.setCurrentText("A-Z")
        self.cb_filter.setCurrentText("All")

    def getFilterState(self):
        """Return current filter state as a dictionary."""
        return {
            'category': self.cb_filter.currentText(),
            'sort': self.cb_sort.currentText(),
            'favorites_only': self.chk_favorites.isChecked()
        }
