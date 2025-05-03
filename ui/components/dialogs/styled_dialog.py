"""helpers/ui_helpers/base_dialog.py

Defines the BaseDialog class, a frameless QDialog with a custom title bar and standardized content layout.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QWidget

from ui.components.layouts.title_bar import TitleBar


# ── Class Definition ────────────────────────────────────────────────────────────
class StyledDialog(QDialog):
    """
    A frameless QDialog that swaps out the native title bar
    for your custom TitleBar widget.

    Attributes:
        title_bar (TitleBar): The draggable header with close/min/max.
        body (QWidget): Container for your dialog’s main content.
        content_layout (QVBoxLayout): Layout you add your widgets into.
    """

    def __init__(self, parent=None):
        """A frameless QDialog with a custom TitleBar widget.

        Attributes:
            title_bar (TitleBar): Draggable custom header with close, minimize, maximize buttons.
            body (QWidget): Container widget for main dialog content.
            content_layout (QVBoxLayout): Vertical layout inside the body for adding content.
        """
        super().__init__(parent)
        # ── Instiate TileBar ──
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog) # remove native title bar
        self.title_bar = TitleBar(self)

        # ── Connect Signals ──
        self.title_bar.close_clicked.connect(self.close)
        self.title_bar.minimize_clicked.connect(self.showMinimized)
        self.title_bar.maximize_clicked.connect(self._toggle_maximize)

        self._is_maximized = False # track maximized state

        # ── Create Body Container ──
        self.body = QWidget(self)
        self.body.setObjectName("dialog_body")
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
        """Switch between maximized and normal, updating the icon."""
        if not self._is_maximized:
            self.showMaximized() # maximize the window
        else:
            self.showNormal()

        # ── Toggle Maximize State ──
        self._is_maximized = not self._is_maximized
        self.title_bar.updateMaximizeIcon(self._is_maximized)
