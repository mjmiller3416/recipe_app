# helpers/base_dialog.py

# 🔸 Third-party
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QWidget

# 🔸 Local Imports
from core.application.title_bar import TitleBar

# ────────────────────────────────────────────────────────────────────────────────


class BaseDialog(QDialog):
    """
    A frameless QDialog that swaps out the native title bar
    for your custom TitleBar widget.
    
    Attributes:
        title_bar (TitleBar): The draggable header with close/min/max.
        body (QWidget): Container for your dialog’s main content.
        content_layout (QVBoxLayout): Layout you add your widgets into.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        # remove native window chrome
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # ── title bar ──
        self.title_bar = TitleBar(self)

        # wire up TitleBar signals
        self.title_bar.close_clicked.connect(self.close)
        self.title_bar.minimize_clicked.connect(self.showMinimized)
        self.title_bar.maximize_clicked.connect(self._toggle_maximize)

        # track maximized state
        self._is_maximized = False

        # ── body container ──
        self.body = QWidget(self)
        self.body.setObjectName("dialog_body")
        self.content_layout = QVBoxLayout(self.body)
        self.content_layout.setContentsMargins(12, 12, 12, 12)
        self.content_layout.setSpacing(8)

        # ── main layout ──
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.title_bar)   # at the top
        main_layout.addWidget(self.body)        # your content below

    def _toggle_maximize(self):
        """Switch between maximized and normal, updating the icon."""
        if not self._is_maximized:
            self.showMaximized()
        else:
            self.showNormal()
        self._is_maximized = not self._is_maximized
        self.title_bar.updateMaximizeIcon(self._is_maximized)