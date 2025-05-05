from components.icon_display_card import IconDisplayCard
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from core.controllers.theme_controller import ThemeController
from ui.iconkit.themed_icon import ThemedIcon

ThemeController().apply_theme()

class IconTestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IconKit Playground")
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        container_layout = QVBoxLayout(container)

        test_icons = [
            ("search.svg", QSize(24, 24), "default"),
            ("search.svg", QSize(24, 24), "nav"),
            ("close.svg", QSize(32, 32), "titlebar"),
            ("settings.svg", QSize(32, 32), "nav"),
            ("add.svg", QSize(20, 20), "default"),
            ("dashboard.svg", QSize(28, 28), "nav"),
            ("warning.svg", QSize(24, 24), "default"),
        ]

        for file_name, size, variant in test_icons:
            container_layout.addWidget(IconDisplayCard(file_name, size, variant))

        scroll.setWidget(container)
        layout.addWidget(scroll)
        container_layout.addStretch()
