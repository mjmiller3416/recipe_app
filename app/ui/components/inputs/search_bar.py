"""app/ui/components/search_bar.py

This module defines a custom search widget that includes a search icon, a text input field,
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QGridLayout, QLineEdit, QSizePolicy

from app.config import SEARCH
from app.ui.components.widgets import CTIcon, CTToolButton

# ── Constants ───────────────────────────────────────────────────────────────────
ICONS = SEARCH["ICONS"]

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
        self.setMinimumHeight(60)
        self.setMaximumHeight(80)
        self.setFixedWidth(400)

        self._setup_ui()
        self._setup_events()

    def _setup_ui(self):
        """Creates and lays out the internal UI elements."""
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(12, 0, 8, 0)  # Left/right padding for breathing room
        self.layout.setSpacing(5)

        # ── Search Icon ──
        self.ico_search = CTIcon(
            file_path =ICONS["SEARCH"]["PATH"],
            icon_size =ICONS["SEARCH"]["SIZE"],
            variant   =ICONS["SEARCH"]["STATIC"],
        )
        self.layout.addWidget(self.ico_search, 0, 0)

        # ── Input Field ──
        self.le_search = QLineEdit(self)
        self.le_search.setObjectName("le_search")
        self.le_search.setPlaceholderText("Search...")
        self.le_search.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.le_search.setAlignment(Qt.AlignVCenter)
        self.layout.addWidget(self.le_search, 0, 1)

        # ── Clear Button ──
        self.btn_ico_clear = CTToolButton(
            file_path = ICONS["CLEAR"]["PATH"],
            icon_size = ICONS["CLEAR"]["SIZE"],
            variant   = ICONS["CLEAR"]["DYNAMIC"],
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


