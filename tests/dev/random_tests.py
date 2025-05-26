import sys
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QComboBox,
    QPushButton,
    QVBoxLayout,
    QMessageBox
)


class FormExample(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QFormLayout Test Example")
        self.setMinimumWidth(300)

        # Create the form layout
        form_layout = QFormLayout()

        # Add fields
        self.name_input = QLineEdit()
        form_layout.addRow("Name:", self.name_input)

        self.age_input = QSpinBox()
        self.age_input.setRange(0, 120)
        form_layout.addRow("Age:", self.age_input)

        self.gender_input = QComboBox()
        self.gender_input.addItems(["Select...", "Male", "Female", "Other"])
        form_layout.addRow("Gender:", self.gender_input)

        # Add a submit button below the form
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.handle_submit)

        # Combine form + button in a vertical layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(submit_button)

        self.setLayout(main_layout)

    def handle_submit(self):
        name = self.name_input.text()
        age = self.age_input.value()
        gender = self.gender_input.currentText()

        QMessageBox.information(
            self,
            "Form Submitted",
            f"Name: {name}\nAge: {age}\nGender: {gender}"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FormExample()
    window.show()
    sys.exit(app.exec())
