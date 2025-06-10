import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt

from ui.components.inputs.custom_combobox import CustomComboBox # Import CustomComboBox

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test App with CustomComboBox")
        self.setGeometry(100, 100, 400, 150)

        central_widget = QFrame(self)
        self.setCentralWidget(central_widget)
        main_window_layout = QVBoxLayout(central_widget)
        
        # Sample items for the CustomComboBox
        combo_items = [f"Item {i+1}" for i in range(10)] + ["Another Option", "Test Value", "Final Choice"]

        self.custom_combo_box = CustomComboBox(
            list_items=combo_items,
            placeholder="Select an option..."
        )
        # Connect the textChanged signal of the internal QLineEdit to update the label
        self.custom_combo_box.line_edit.textChanged.connect(self.update_label_from_combobox)
        main_window_layout.addWidget(self.custom_combo_box) # Add CustomComboBox instead of QPushButton

        self.selection_label = QLabel("No selection yet.", self)
        self.selection_label.setAlignment(Qt.AlignCenter)
        main_window_layout.addWidget(self.selection_label, alignment=Qt.AlignCenter)
        
    def update_label_from_combobox(self, text):
        if text: # Only update if text is not empty (e.g. when cleared)
            self.selection_label.setText(f"Selected: {text}")
        else:
            self.selection_label.setText("No selection yet.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
