from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QApplication, QVBoxLayout
from PySide6.QtCore import Qt, QEvent, QTimer
from PySide6.QtGui import QPixmap, QIcon

import sys

from PySide6.QtCore import QObject, QEvent
from app.ui.helpers.ui_helpers import CornerAnchor


class AvatarEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(300, 300)

        # Create layouts and widgets
        self.setStyleSheet("background-color: #f0f0f0;")
        self.setWindowTitle("Avatar Editor")

        # ── Layout ──
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(10)

        # ── Avatar Widget ──
        self.avatar = QLabel(self)
        self.avatar.setPixmap(QPixmap("path/to/avatar.png").scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.avatar.setFixedSize(128, 128)
        self.avatar.setStyleSheet("border-radius: 64px; background-color: #ccc;")  # Placeholder look
        self.layout.addWidget(self.avatar, alignment=Qt.AlignCenter)

        self.edit_btn = QPushButton(self)
        self.edit_btn.setFixedSize(32, 32)
        self.edit_btn.setIcon(QIcon("edit.svg"))
        self.edit_btn.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 16px;
                background-color: white;
                box-shadow: 0px 2px 4px rgba(0,0,0,0.3);
            }
        """)

        # 🎯 Create the anchor
        self.anchor = CornerAnchor(
            anchor_widget=self.avatar,
            target_widget=self.edit_btn,
            corner="bottom-left",
            x_offset=-6,
            y_offset=-6,
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AvatarEditor()
    window.show()
    sys.exit(app.exec())
