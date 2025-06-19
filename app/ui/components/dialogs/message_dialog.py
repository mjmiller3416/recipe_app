"""ui/components/dialogs/message_dialog.py

Custom dialog for displaying messages with dynamic button visibility.
"""


# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QDialog, QDialogButtonBox,
                               QGraphicsDropShadowEffect, QGridLayout, QLabel,
                               QSizePolicy, QSpacerItem, QVBoxLayout)

from app.config import MESSAGE_DIALOG
from app.core.utils import DebugLogger
from app.ui.widgets import CTIcon


# ── Class Definition ────────────────────────────────────────────────────────────
class MessageDialog(QDialog):
    """Custom dialog for displaying messages with dynamic button visibility."""

    def __init__(self, message_type="info", message="", description="", parent=None):
        super().__init__(parent)
        self.setObjectName("MessageDialog")
        self.setFixedSize(400, 220)
        self.setWindowFlags(Qt.FramelessWindowHint)

        DebugLogger.log("DialogWidget initialized", "info")

        self.message_type = message_type

        self._setup_ui()
        self._configure_buttons()
        self._set_messages(message, description)
        #self._apply_shadow()

    def _setup_ui(self):
        self.grid_layout = QGridLayout(self)
        self.grid_layout.setContentsMargins(9, 9, 9, 18)
        self.grid_layout.setVerticalSpacing(6)

        self.lyt_message = QVBoxLayout()
        self.lyt_message.setContentsMargins(9, 9, 10, 9)
        self.lyt_message.setSpacing(0)

        icon_config = MESSAGE_DIALOG.get(f"ICON_{self.message_type.upper()}", MESSAGE_DIALOG["ICON_INFO"])
        self.status_icon = CTIcon(
            file_path=icon_config["ICON_PATH"],
            size=MESSAGE_DIALOG["ICON_SIZE"],
            variant=icon_config["ICON_COLOR"]
        )
        self.lyt_message.addWidget(self.status_icon, 0, Qt.AlignmentFlag.AlignHCenter)
        self.lyt_message.addItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

        self.lbl_message = QLabel("Message", self)
        self.lyt_message.addWidget(self.lbl_message, 0, Qt.AlignmentFlag.AlignHCenter)

        self.lbl_description = QLabel("Descriptive Message", self)
        self.lbl_description.setWordWrap(True)
        self.lyt_message.addWidget(self.lbl_description, 0, Qt.AlignmentFlag.AlignHCenter)

        self.grid_layout.addLayout(self.lyt_message, 1, 0)

        self.buttonBox = QDialogButtonBox(self)
        self.grid_layout.addWidget(self.buttonBox, 2, 0, 1, 1, Qt.AlignmentFlag.AlignHCenter)

    def _apply_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 165))
        self.setGraphicsEffect(shadow)

    def showEvent(self, event):
        super().showEvent(event)
        self._center_dialog()

    def _center_dialog(self):
        if self.parent():
            parent_rect = self.parent().geometry()
            dialog_rect = self.geometry()

            center_x = parent_rect.x() + (parent_rect.width() - dialog_rect.width()) // 2 - 20
            center_y = parent_rect.y() + (parent_rect.height() // 3 - dialog_rect.height() // 2)
            self.move(center_x, center_y)

    def _configure_buttons(self):
        self.buttonBox.clear()
        t = self.message_type

        if t in ("info", "error"):
            self.buttonBox.addButton("OK", QDialogButtonBox.AcceptRole).clicked.connect(self.accept)

        elif t == "warning":
            self.buttonBox.addButton("OK", QDialogButtonBox.AcceptRole).clicked.connect(self.accept)
            self.buttonBox.addButton("Cancel", QDialogButtonBox.RejectRole).clicked.connect(self.reject)

        elif t == "confirmation":
            self.buttonBox.addButton("Save", QDialogButtonBox.AcceptRole).clicked.connect(self.accept)
            discard_btn = self.buttonBox.addButton("Discard", QDialogButtonBox.DestructiveRole)
            discard_btn.clicked.connect(self.discard_changes)
            self.buttonBox.addButton("Cancel", QDialogButtonBox.RejectRole).clicked.connect(self.reject)

    def discard_changes(self):
        DebugLogger.log("Changes discarded!", "warning")
        self.accept()

    def _set_messages(self, title, description):
        self.lbl_message.setText(title or "")
        self.lbl_description.setText(description or "")

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.accept()
        elif event.key() == Qt.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)
