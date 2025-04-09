from qt_imports import (
    QWidget, Qt)
from app.shopping_list import Ui_ShoppingList # Import generated UI

class ShoppingList(QWidget):
    """Subclass of the generated UI for the Shopping List screen."""

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize & Setup UI
        self.ui = Ui_ShoppingList()
        self.ui.setupUi(self)   
        self.setObjectName("ShoppingList")

