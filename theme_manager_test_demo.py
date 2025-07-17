from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QFrame,
    QLabel, QPushButton, QComboBox
)
from app.theme_manager.theme import Theme
from app.theme_manager.config import Color, Mode, Qss
import sys
import os


class ThemeTestApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Theme Test App")
        self.resize(400, 300)

        self.layout = QVBoxLayout(self)

        # ── Frame Widget ──
        frame = QFrame()
        frame.setProperty("type", "card")

        frame_layout = QVBoxLayout(frame)

        title = QLabel("Primary Surface Card")
        title.setProperty("type", "title")

        subtitle = QLabel("Styled using your ThemeManager + QSS injection system")
        subtitle.setProperty("type", "subtitle")

        frame_layout.addWidget(title)
        frame_layout.addWidget(subtitle)

        # ── Theme Controls ──
        self.toggle_button = QPushButton("Toggle Theme (Light/Dark)")
        self.toggle_button.clicked.connect(self.toggle_theme)

        self.color_dropdown = QComboBox()
        self.color_dropdown.addItems([color.name for color in Color])
        self.color_dropdown.currentTextChanged.connect(self.change_color)

        # ── Add to layout ──
        self.layout.addWidget(self.toggle_button)
        self.layout.addWidget(self.color_dropdown)
        self.layout.addWidget(frame)

    def toggle_theme(self):
        Theme().toggle_theme_mode()

    def change_color(self, color_name: str):
        color_enum = Color[color_name]
        Theme().set_theme_color(color_enum)


if __name__ == "__main__":


    app = QApplication(sys.argv)
    Theme()  # Initialize theme singleton
    window = ThemeTestApp()
    window.show()
    sys.exit(app.exec())
