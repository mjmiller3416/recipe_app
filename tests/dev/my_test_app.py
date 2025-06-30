
from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtGui import QIcon
from qframelesswindow import FramelessWindow

class Window(FramelessWindow):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("ApplicationWindow")

        self.label = QLabel("MealGenie")
        self.label.setScaledContents(True)

        self.setWindowIcon(QIcon("app/assets/icons/logo.svg"))
        self.setWindowTitle("Test Window")

        self.titleBar.raise_()

    def resizeEvent(self, e):
        # don't forget to call the resizeEvent() of super class
        super().resizeEvent(e)
        length = min(self.width(), self.height())
        self.label.resize(length, length)
        self.label.move(
            self.width() // 2 - length // 2,
            self.height() // 2 - length // 2
        )


def run_test(app=None):
    """
    Entry point for test mode when called from main.py --test
    
    Args:
        app: QApplication instance (optional, will create if not provided)
    
    Returns:
        Window instance for the test application
    """
    if app is None:
        app = QApplication([])
        app.setApplicationName("Test App")
    
    # Create and show the test window
    test_window = Window()
    test_window.show()
    
    return test_window