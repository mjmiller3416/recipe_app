"""ui/components/dialogs/dialog_window.py

Defines the BaseDialog class, a frameless QDialog with a custom title bar and standardized content layout.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QDialog, QVBoxLayout, QWidget

from config import STYLES, TITLE_BAR
from ui.components.title_bar import TitleBar


# ── Class Definition ────────────────────────────────────────────────────────────
class DialogWindow(QDialog):
    """A frameless QDialog with a custom TitleBar widget.
    
    Args:
        width (int, optional): Initial width of the dialog. Defaults to 600.
        height (int, optional): Initial height of the dialog. Defaults to 400.
        title (str, optional): Title displayed in the title bar. Defaults to TITLE_BAR["APP_NAME"].
        parent (QWidget, optional): The parent widget. Defaults to None.
    """

    def __init__(
            self, 
            width: int = 600, 
            height: int = 400,
            title: str = TITLE_BAR["APP_NAME"],
            parent: QWidget | None = None,
        ):
        """A frameless QDialog with a custom TitleBar widget.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
            width (int, optional): Initial width of the dialog. Defaults to 600.
            height (int, optional): Initial height of the dialog. Defaults to 400.
        """
        super().__init__(parent)
        self.setObjectName("DialogWindow")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog) # remove native title bar
        self.resize(int(width), int(height))  # set initial size

        # ── Instiate TileBar ──
        self.title_bar = TitleBar(self)
        self.title_bar.lbl_title.setText(title)
        self.title_bar.close_clicked.connect(self.close)
        self.title_bar.minimize_clicked.connect(self.showMinimized)
        self.title_bar.maximize_clicked.connect(self._toggle_maximize)
        self._is_maximized = False

        # ── Create Body Container ──
        self.body = QWidget(self)
        self.body.setObjectName("Dialog")
        self.content_layout = QVBoxLayout(self.body)
        self.content_layout.setContentsMargins(12, 12, 12, 12)
        self.content_layout.setSpacing(8)

        # ── Create Layout ──
        lyt = QVBoxLayout(self)
        lyt.setContentsMargins(0, 0, 0, 0)
        lyt.setSpacing(0)
        lyt.addWidget(self.title_bar)   # at the top
        lyt.addWidget(self.body)        # your content below

    def _toggle_maximize(self):
        if not self._is_maximized:
            # save current size and pos
            self._normal_geometry = self.geometry()
            screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
            self.setGeometry(screen_geometry)
        else:
            # restore previous size and pos
            if hasattr(self, '_normal_geometry'):
                self.setGeometry(self._normal_geometry)

        self._is_maximized = not self._is_maximized
        self.title_bar.update_maximize_icon(self._is_maximized)

