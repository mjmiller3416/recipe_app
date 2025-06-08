import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QLabel
from PySide6.QtGui import QFocusEvent

class FocusLineEdit(QLineEdit):
    """
    A custom QLineEdit that emits signals and prints messages on focus changes.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

    def focusInEvent(self, event: QFocusEvent):
        """
        This method is called automatically when the widget gains keyboard focus.
        """
        print(f"'{self.objectName()}' gained focus!")
        # Do something custom here, like changing the background color
        self.setStyleSheet("background-color: #e6f7ff;")
        # IMPORTANT: Call the base class implementation to allow normal event processing
        super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent):
        """
        This method is called automatically when the widget loses keyboard focus.
        """
        print(f"'{self.objectName()}' lost focus!")
        # Revert the custom change
        self.setStyleSheet("") # Reverts to the default stylesheet
        # IMPORTANT: Call the base class implementation
        super().focusOutEvent(event)


class FocusDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Focus In/Out Event Demo")

        # Create two instances of our custom QLineEdit to demonstrate focus changes
        line_edit_1 = FocusLineEdit()
        line_edit_1.setObjectName("LineEdit1")
        line_edit_1.setPlaceholderText("Click here first")

        line_edit_2 = FocusLineEdit()
        line_edit_2.setObjectName("LineEdit2")
        line_edit_2.setPlaceholderText("Then click here")
        
        info_label = QLabel("Click between the two text fields to see focus events in the console.")

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(info_label)
        layout.addWidget(line_edit_1)
        layout.addWidget(line_edit_2)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FocusDemo()
    window.show()
    sys.exit(app.exec())