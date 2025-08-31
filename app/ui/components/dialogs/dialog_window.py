"""app/ui/components/dialogs/dialog_window.py

Custom Dialog Window with Title Bar
A base QDialog with a frameless window and a custom title bar.
Provides close button and dragging functionality.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QWidget

from app.config import APPLICATION_WINDOW
from app.ui.components.navigation import TitleBar
from app.ui.helpers.ui_helpers import center_on_screen

# ── Constants ───────────────────────────────────────────────────────────────────────────
SETTINGS = APPLICATION_WINDOW["SETTINGS"]

# ── Application Window ──────────────────────────────────────────────────────────────────
class DialogWindow(QDialog):
    """Base dialog class with frameless window and custom title bar.

    Provides a close button and dragging support. Content widgets
    should be added to the content_area layout.

    Attributes:
        title_bar: The custom title bar widget.
        window_body: The main dialog body widget.
        content_area: The widget holding main content.
        content_layout: Layout for adding content widgets.
        central_layout: Main layout for the dialog.
        start_geometry: Initial geometry of the dialog.
    """

    def __init__(self, width: int = 1330, height: int = 800, window_title: str = "", parent=None):
        """Initializes the DialogWindow.

        Args:
            width (int, optional): Initial width of the dialog. Defaults to 1330.
            height (int, optional): Initial height of the dialog. Defaults to 800.
            parent (QWidget, optional): Parent widget that owns the dialog.
        """
        super().__init__(parent)
        # ── Properties ──
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        # self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(400, 300)
        self.setObjectName("Dialog")
        self.start_geometry = self.geometry()
        self.central_layout = QVBoxLayout(self)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setSpacing(0)

        # ── Title Bar ──
        self.title_bar = TitleBar(self)
        self.central_layout.addWidget(self.title_bar)
        # Connect title bar signals for dialog behavior
        self.title_bar.close_clicked.connect(self.close)

        # ── Window Body ──
        self.window_body = QWidget(self)
        self.window_body.setObjectName("DialogWindow")
        self.body_layout = QHBoxLayout(self.window_body)
        self.body_layout.setContentsMargins(1, 0, 1, 1)
        self.body_layout.setSpacing(0)

        # ── Content Area ──
        self.content_area = QWidget()
        self.content_area.setObjectName("DialogLayout")
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(8)
        self.body_layout.addWidget(self.content_area)
        self.central_layout.addWidget(self.window_body)

        self.resize(int(width), int(height))
        center_on_screen(self)


