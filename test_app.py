import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit
from PySide6.QtCore import qVersion

# 1. Print the exact Qt version this script is using to be certain
print(f"--- Running with Qt version: {qVersion()} ---")

# 2. The Stylesheet (QSS)
# The style is made very obvious (large, red, bold, italic) to be unmissable.
STYLESHEET = """
QLineEdit {
    font-size: 20px;
    padding: 10px;
    border: 2px solid #555;
    border-radius: 5px;
}

QLineEdit::placeholder {
    color: red;
    font-style: italic;
    font-weight: bold;
}
"""

# 3. The Main Application Window
class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Placeholder Style Test")
        self.setGeometry(300, 300, 500, 150) # Set window size

        layout = QVBoxLayout(self)
        line_edit = QLineEdit()
        line_edit.setPlaceholderText("Is this text red and italic?")
        layout.addWidget(line_edit)

# 4. Standard boilerplate to create and run the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Apply the stylesheet to the entire application
    app.setStyleSheet(STYLESHEET)
    
    window = TestWindow()
    window.show()
    
    sys.exit(app.exec())