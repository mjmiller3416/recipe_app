from PySide6.QtWidgets import QCheckBox
from PySide6.QtCore import Qt, Property
from PySide6.QtGui import QPainter, QColor, QBrush


class ToggleSwitch(QCheckBox):
    def __init__(self, label="", parent=None):
        super().__init__(label, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(50, 28)
        self.setStyleSheet("QCheckBox { padding-left: 60px; }")

    def paintEvent(self, event):
        radius = 12
        width = self.width()
        height = self.height()

        center_y = height // 2
        knob_x = width - 28 if self.isChecked() else 4

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Draw track
        track_color = QColor("#4CAF50") if self.isChecked() else QColor("#ccc")
        p.setBrush(QBrush(track_color))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(2, center_y - 10, 46, 20, radius, radius)

        # Draw knob
        p.setBrush(QColor("white"))
        p.drawEllipse(knob_x, center_y - 9, 18, 18)
