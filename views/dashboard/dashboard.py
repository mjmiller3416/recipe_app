from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget, QLabel
from ui.iconkit import StandardIcon


class Dashboard(QWidget):
    """Placeholder class for the Dashboard screen."""

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize & Setup UI
        self.setObjectName("Dashboard")
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setObjectName("Dashboard")
        self.setMinimumSize(984, 818)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel("Dashboard", self)

        self.layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)