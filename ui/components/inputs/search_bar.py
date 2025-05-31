"""ui/components/inputs/search_bar.py

This module defines a custom search widget that includes a search icon, a text input field,
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import QFrame, QGridLayout, QLineEdit, QSizePolicy

from config import SEARCH
from ui.iconkit import Icon, ToolButtonIcon


# ── Class Definition ────────────────────────────────────────────────────────────
class SearchBar(QFrame):
    """
    A custom search bar widget with a search icon, text input, and clear button.

    Emits:
        - search_triggered(str): when text is entered or Enter is pressed.
        - recipe_selected(str): placeholder for future recipe selection support.
    """
    
    # ── Signals ─────────────────────────────────────────────────────────────────────
    recipe_selected = Signal(str)
    search_triggered = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SearchBar")
        self.setMinimumHeight(40)
        self.setMaximumHeight(60)

        self._setup_ui()
        self._setup_events()

    def _setup_ui(self):
        """Creates and lays out the internal UI elements."""
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(12, 0, 8, 0)  # Left/right padding for breathing room
        self.layout.setSpacing(5)

        # ── Search Icon ──
        self.ico_search = Icon(
            file_path=SEARCH["ICON_SEARCH"]["FILE_PATH"],
            size=SEARCH["ICON_SEARCH"]["ICON_SIZE"],
            variant=SEARCH["ICON_SEARCH"]["STATIC"],
        )
        self.layout.addWidget(self.ico_search, 0, 0)

        # ── Input Field ──
        self.le_search = QLineEdit(self)
        self.le_search.setObjectName("le_search")
        self.le_search.setPlaceholderText("Search...")
        self.le_search.setFixedHeight(24)
        self.le_search.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.le_search.setAlignment(Qt.AlignVCenter)
        self.layout.addWidget(self.le_search, 0, 1)

        # ── Clear Button ──
        self.btn_ico_clear = ToolButtonIcon(
            file_path = SEARCH["ICON_CLEAR"]["FILE_PATH"],
            icon_size = SEARCH["ICON_CLEAR"]["ICON_SIZE"],
            variant   = SEARCH["ICON_CLEAR"]["DYNAMIC"],
        )
        self.btn_ico_clear.setVisible(False) # visibility based on text input
        self.layout.addWidget(self.btn_ico_clear, 0, 2)

    def _setup_events(self):
        """Connects signals to slots."""
        self.le_search.textChanged.connect(self._on_text_changed)
        self.le_search.returnPressed.connect(self._on_return_pressed)
        self.btn_ico_clear.clicked.connect(self.clear_input)

    def _on_text_changed(self, text):
        self.btn_ico_clear.setVisible(bool(text))

    def _on_return_pressed(self):
        self.search_triggered.emit(self.le_search.text())

    def clear_input(self):
        self.le_search.clear()

    def text(self):
        return self.le_search.text()

    def setText(self, text: str):
        self.le_search.setText(text)


