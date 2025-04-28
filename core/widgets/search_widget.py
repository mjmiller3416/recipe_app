from core.application.config import ICON_COLOR, icon_path
# 🔹 Local Import
from core.helpers.qt_imports import (QFrame, QGridLayout, QIcon, QLabel,
                                     QLineEdit, QPixmap, QSize, QSizePolicy,
                                     Qt, QToolButton, Signal)
from core.managers.style_manager import StyleManager


class SearchWidget(QFrame):
    """
    A custom search bar widget with a search icon, text input, and clear button.

    Emits:
        - search_triggered(str): when text is entered or Enter is pressed.
        - recipe_selected(str): placeholder for future recipe selection support.
    """

    # 🔹 Constants
    ICON_SIZE = QSize(16, 16)

    # 🔹 Signals
    recipe_selected = Signal(str)
    search_triggered = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SearchWidget")
        self.setMinimumHeight(40)
        self.setMaximumHeight(60)

        self._setup_ui()
        self._setup_events()

        self.style_manager = StyleManager(self)

    def _setup_ui(self):
        """Creates and lays out the internal UI elements."""

        from core.helpers.ui_helpers import svg_loader # Import to avoid circular dependency ⚠️⚠️⚠️

        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(12, 0, 8, 0)  # Left/right padding for breathing room
        self.layout.setSpacing(5)

        # 🔹 Load Label Icons
        self.icon_search = svg_loader(icon_path("search"), ICON_COLOR, self.ICON_SIZE, return_type=QPixmap, source_color="#000")
        self.icon_clear = svg_loader(icon_path("x"), ICON_COLOR, self.ICON_SIZE, return_type=QIcon, source_color="#000")

        # 🔹 Search Icon
        self.lbl_search = QLabel(self)
        self.lbl_search.setObjectName("lbl_search")
        self.lbl_search.setFixedSize(self.ICON_SIZE)
        self.lbl_search.setPixmap(self.icon_search)
        self.lbl_search.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.lbl_search, 0, 0)

        # 🔹 Input Field
        self.le_search = QLineEdit(self)
        self.le_search.setObjectName("le_search")
        self.le_search.setPlaceholderText("Search...")
        self.le_search.setFixedHeight(24)
        self.le_search.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.le_search.setAlignment(Qt.AlignVCenter)
        self.layout.addWidget(self.le_search, 0, 1)

        # 🔹 Clear Button
        self.btn_clear = QToolButton(self)
        self.btn_clear.setObjectName("btn_clear")
        self.btn_clear.setIcon(self.icon_clear)
        self.btn_clear.setVisible(False) # Testing visibility based on text input
        self.btn_clear.setFixedSize(24, 24)
        self.btn_clear.setIconSize(QSize(20, 20))  # Set icon size for the button
        self.btn_clear.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.layout.addWidget(self.btn_clear, 0, 2)

    def _setup_events(self):
        """Connects signals to slots."""
        self.le_search.textChanged.connect(self._on_text_changed)
        self.le_search.returnPressed.connect(self._on_return_pressed)
        self.btn_clear.clicked.connect(self.clear_input)

    def _on_text_changed(self, text):
        self.btn_clear.setVisible(bool(text))

    def _on_return_pressed(self):
        self.search_triggered.emit(self.le_search.text())

    def clear_input(self):
        self.le_search.clear()

    def text(self):
        return self.le_search.text()

    def setText(self, text: str):
        self.le_search.setText(text)


