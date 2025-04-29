import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QListView, QSplitter, QTextEdit,
                               QVBoxLayout, QWidget)


class SplitterExample(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        splitter = QSplitter(Qt.Horizontal)  # Split left and right

        text_edit = QTextEdit()
        text_edit.setPlainText("This is a QTextEdit.")

        list_view = QListView()

        splitter.addWidget(text_edit)
        splitter.addWidget(list_view)

        layout.addWidget(splitter)

        self.setWindowTitle('QSplitter Example')
        self.resize(600, 400)
        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SplitterExample()
    sys.exit(app.exec_())
