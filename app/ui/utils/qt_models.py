"""app/ui/utils/qt_models.py

Contains custom proxy models for filtering and sorting data in views.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSortFilterProxyModel


# ── Ingredient Proxy Model ──────────────────────────────────────────────────────────────────────────────────
class IngredientProxyModel(QSortFilterProxyModel):
    """IngredientProxyModel is a custom proxy model that filters
    ingredient items based on a plain text filter.

    It checks if any word
    in the ingredient name starts with the filter text.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._filter_text = ""

    def setFilterFixedString(self, pattern: str):
        """Overrides default behavior to store plain text pattern."""
        self._filter_text = pattern.strip().lower()
        self.invalidateFilter()

    def filterAcceptsRow(self, row, parent):
        """Determines if a row should be included in the filtered results."""
        if not self._filter_text:
            return True

        index = self.sourceModel().index(row, 0, parent)
        text = self.sourceModel().data(index).lower()

        # check if *any word* starts with the filter text
        return any(word.startswith(self._filter_text) for word in text.split())
