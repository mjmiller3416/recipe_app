from core.helpers.qt_imports import QWidget, Qt, QVBoxLayout, QLabel


class ShoppingList(QWidget):
    """Placeholder class for the ShoppingList screen."""

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize & Setup UI
        self.setObjectName("ShoppingList")
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setObjectName("ShoppingList")
        self.setMinimumSize(984, 818)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel("Shopping List", self)

        self.layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)