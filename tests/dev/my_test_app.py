import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout,
                               QHBoxLayout, QStackedWidget, QPushButton, QLabel)
from PySide6.QtCore import Qt

class CarouselWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Carousel Example")
        self.setGeometry(100, 100, 400, 300)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # QStackedWidget to hold the different "pages" of the carousel
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # Create some example pages (QWidgets with labels)
        for i in range(1, 4):
            page = QWidget()
            page_layout = QVBoxLayout(page)
            label = QLabel(f"Page {i}")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font-size: 24px; background-color: lightblue;")
            page_layout.addWidget(label)
            self.stacked_widget.addWidget(page)

        # Navigation buttons
        nav_layout = QHBoxLayout()
        main_layout.addLayout(nav_layout)

        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.show_previous_page)
        nav_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.show_next_page)
        nav_layout.addWidget(self.next_button)

        self.update_button_states()

    def show_previous_page(self):
        current_index = self.stacked_widget.currentIndex()
        if current_index > 0:
            self.stacked_widget.setCurrentIndex(current_index - 1)
        self.update_button_states()

    def show_next_page(self):
        current_index = self.stacked_widget.currentIndex()
        if current_index < self.stacked_widget.count() - 1:
            self.stacked_widget.setCurrentIndex(current_index + 1)
        self.update_button_states()

    def update_button_states(self):
        current_index = self.stacked_widget.currentIndex()
        self.prev_button.setEnabled(current_index > 0)
        self.next_button.setEnabled(current_index < self.stacked_widget.count() - 1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    carousel = CarouselWidget()
    carousel.show()
    sys.exit(app.exec())