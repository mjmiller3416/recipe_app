"""app/ui/views/recipe_browser/_filter_bar.py

Filter bar component for recipe browsing with category, sorting, and favorites options.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout

from app.config import RECIPE_CATEGORIES, SORT_OPTIONS

from ...components.widgets import ComboBox, CheckBox

class FilterBar(QWidget):
    category_changed = Signal(str)
    sort_changed = Signal(str)
    favorites_toggled = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        """Build UI components."""
        self._filter_layout = QHBoxLayout()
        self._filter_layout.setSpacing(10)
        self._filter_layout.setContentsMargins(0, 0, 0, 0)

        self._create_filter_controls()

        self.setLayout(self._filter_layout) # Set the layout

    def _create_filter_controls(self):
        # Create filter controls with optimized settings
        self._cb_filter = ComboBox(list_items=RECIPE_CATEGORIES, placeholder="Filter")
        self._cb_filter.setObjectName("CategoryFilter")
        self._cb_filter.setFixedHeight(60)

        self._cb_sort = ComboBox(list_items=SORT_OPTIONS, placeholder="Sort")
        self._cb_sort.setObjectName("SortFilter")
        self._cb_sort.setFixedHeight(60)

        self._chk_favorites = CheckBox("Show Favorites Only")
        self._chk_favorites.setObjectName("FavoritesFilter")

        # Add to layout
        self._filter_layout.addWidget(self._cb_filter)
        self._filter_layout.addWidget(self._cb_sort)
        self._filter_layout.addWidget(self._chk_favorites)
        self._filter_layout.addStretch()

    def _connect_signals(self):
        """Connect widget signals to internal signals."""
        self._cb_filter.currentTextChanged.connect(self.category_changed.emit)
        self._cb_sort.currentTextChanged.connect(self.sort_changed.emit)
        self._chk_favorites.toggled.connect(self.favorites_toggled.emit)

    def get_current_filters(self):
        """Get current filter values."""
        return {
            'category': self._cb_filter.currentText(),
            'sort': self._cb_sort.currentText(),
            'favorites_only': self._chk_favorites.isChecked()
        }

    def reset_filters(self):
        """Reset all filters to default state."""
        self._cb_filter.setCurrentText("")
        self._cb_sort.setCurrentText("")
        self._chk_favorites.setChecked(False)
