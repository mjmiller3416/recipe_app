from qt_imports import ( # Imports
    QWidget, Qt)
from app.dashboard import Ui_Dashboard # Import generated UI

class Dashboard(QWidget):
    """Subclass of the generated UI for the Dashboard screen."""

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize & Setup UI
        self.ui = Ui_Dashboard()  # Create an instance of the UI class
        self.ui.setupUi(self)  # Load the UI
        self.setObjectName("Dashboard")
        self.setAttribute(Qt.WA_StyledBackground, True)