# Package: app.widgets.combobox

# Description: This module defines a custom QComboBox that uses a QListView as the popup view.
# It allows for a more customized appearance and behavior, such as hiding scrollbars.

#🔸Third-Party Imports
from core.helpers.qt_imports import (
    Signal, QComboBox, QListView, Qt)

#🔸Local Imports
from core.helpers.config import INGREDIENT_CATEGORIES, MEASUREMENT_UNITS 
from core.helpers.debug_logger import DebugLogger

class CustomComboBox(QComboBox):
    """
    Custom QComboBox that uses a QListView as the popup view.
    This allows for a more customized appearance and behavior.
    """

    #🔹SIGNALS
    cb_validated = Signal(bool)  # Emits when a valid selection is made

    def __init__(self, parent=None):
        super().__init__(parent)

        # Use a QListView as the popup view
        list_view = QListView(self)
        list_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Hide scrollbar
        list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Optional: Hide horizontal scrollbar
        self.setView(list_view)

        # Corrected signal connection
        self.currentTextChanged.connect(self.emit_validation)  

    def emit_validation(self, text):
        """
        Emits a signal when a valid selection is made.
        """
        self.cb_validated.emit(bool(text))  # Emits True if text is not empty
        # DebugLogger.log("🟢 ComboBox text changed: {text}", "debug")  # ⚠️ Debugging line 

