from PySide6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QPushButton, QVBoxLayout,
    QLabel, QSizePolicy, QFrame
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap

from core.helpers import svg_loader  # Assuming this is accessible
from core.widgets.svg_button import SVGButton  # Assuming you have this ready to use


class IconComparisonDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QIcon Crisp vs Non-Crisp Comparison")
        self.setMinimumSize(500, 250)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel("🔍 Both buttons use the same SVG file and fixed size:")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        button_row = QHBoxLayout()
        layout.addLayout(button_row)

        icon_path = ":/icons/search.svg"
        color = "#03B79E"
        size = QSize(48, 48)

        # Button using QIcon (crisp = False)
        icon_blurry = svg_loader(icon_path, color=color, size=size, return_type=QIcon, crisp=False)
        btn_blurry = QPushButton("crisp = False")
        btn_blurry.setIcon(icon_blurry)
        btn_blurry.setIconSize(size)
        btn_blurry.setFixedSize(160, 100)
        button_row.addWidget(btn_blurry)

        # Button using QIcon (crisp = True)
        icon_crisp = svg_loader(icon_path, color=color, size=size, return_type=QIcon, crisp=True)
        btn_crisp = QPushButton("crisp = True")
        btn_crisp.setIcon(icon_crisp)
        btn_crisp.setIconSize(size)
        btn_crisp.setFixedSize(160, 100)
        button_row.addWidget(btn_crisp)

        # Button using SVGButton wrapper class
        btn_custom = SVGButton(svg_path=icon_path, color=color, text="SVGButton", icon_size=size)
        btn_custom.setFixedSize(160, 100)
        button_row.addWidget(btn_custom)


if __name__ == "__main__":
    app = QApplication([])
    demo = IconComparisonDemo()
    demo.show()
    app.exec()
