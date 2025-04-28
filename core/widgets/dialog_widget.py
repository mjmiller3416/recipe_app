import sys

from core.application.config import (ERROR_COLOR, INFO_COLOR, SUCCESS_COLOR,
                                     WARNING_COLOR, icon_path)
from helpers.debug_logger import DebugLogger
from core.helpers.qt_imports import (QApplication, QColor, QDialog,
                                     QDialogButtonBox,
                                     QGraphicsDropShadowEffect, QGridLayout,
                                     QLabel, QPixmap, QSizePolicy, QSpacerItem,
                                     Qt, QVBoxLayout)


class DialogWidget(QDialog):
    """Custom dialog for displaying messages with dynamic button visibility."""

    def __init__(self, message_type="info", message="", description="", parent=None):
        super().__init__(parent)
        self.setObjectName("DialogWidget")
        self.setFixedSize(400, 220)
        self.setWindowFlags(Qt.FramelessWindowHint)

        DebugLogger.log("DialogWidget initialized", "info")

        self.message_type = message_type
        self._setup_ui()
        self._apply_shadow()
        self._configure_buttons(message_type)
        self._set_messages(message, description)

    def _setup_ui(self):
        """Manually creates the UI layout without .ui dependency."""
        self.grid_layout = QGridLayout(self)
        self.grid_layout.setContentsMargins(9, 9, 9, 18)
        self.grid_layout.setVerticalSpacing(6)

        self.lyt_message = QVBoxLayout()
        self.lyt_message.setContentsMargins(9, 9, 10, 9)
        self.lyt_message.setSpacing(0)

        self.lbl_icon = QLabel(self)
        self.lbl_icon.setFixedSize(50, 50)
        self.lbl_icon.setScaledContents(True)
        self.lyt_message.addWidget(self.lbl_icon, 0, Qt.AlignmentFlag.AlignHCenter)

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

    def _configure_buttons(self, message_type):
        self.buttonBox.clear()

        if message_type == "info":
            self.buttonBox.addButton("OK", QDialogButtonBox.AcceptRole).clicked.connect(self.accept)

        elif message_type == "warning":
            self.buttonBox.addButton("OK", QDialogButtonBox.AcceptRole).clicked.connect(self.accept)
            self.buttonBox.addButton("Cancel", QDialogButtonBox.RejectRole).clicked.connect(self.reject)

        elif message_type == "confirmation":
            self.buttonBox.addButton("Save", QDialogButtonBox.AcceptRole).clicked.connect(self.accept)
            discard_btn = self.buttonBox.addButton("Discard", QDialogButtonBox.DestructiveRole)
            discard_btn.clicked.connect(self.discard_changes)
            self.buttonBox.addButton("Cancel", QDialogButtonBox.RejectRole).clicked.connect(self.reject)

        elif message_type == "error":
            self.buttonBox.addButton("OK", QDialogButtonBox.AcceptRole).clicked.connect(self.accept)

    def _set_messages(self, message, description):
        from core.helpers.ui_helpers import svg_loader # Local import for button icons⚠️⚠️⚠️
        self.lbl_message.setText(message)
        self.lbl_description.setText(description)

        color = INFO_COLOR
        if self.message_type == "success":
            color = SUCCESS_COLOR
        elif self.message_type == "warning":
            color = WARNING_COLOR
        elif self.message_type == "error":
            color = ERROR_COLOR

        pixmap = svg_loader(icon_path("success"), color, size=self.lbl_icon.size(), return_type=QPixmap, source_color="#000")
        self.lbl_icon.setPixmap(pixmap)

    def discard_changes(self):
        DebugLogger.log("Changes discarded!", "warning")
        self.accept()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.accept()
        elif event.key() == Qt.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dlg = DialogWidget(
        message_type="success",
        message="Operation Complete",
        description="All changes have been saved successfully."
    )
    result = dlg.exec()
    print("Accepted" if result else "Rejected")
