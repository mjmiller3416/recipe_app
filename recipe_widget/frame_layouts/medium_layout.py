from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QGridLayout, QHBoxLayout, QLabel, QSizePolicy,
                               QSpacerItem, QWidget)


class MediumLayout(QWidget):
    """
    Recipe Card Medium Layout

    Displays:
        - Recipe image
        - Recipe name
        - Servings icon + value
        - Time value + suffix
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MediumLayout")
        self.setFixedSize(280, 420)
        self._build_ui()

    def build_medium_layout(self):
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 🔹 Recipe Image
        self.lbl_image = QLabel() # Recipe.image
        self.lbl_image.setObjectName("CardImage")
        self.lbl_image.setFixedSize(280, 280)
        self.lbl_image.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_image, 0, 0, 1, 4)

        # 🔹 Recipe Name
        self.lbl_name = QLabel() # Recipe.name
        self.lbl_name.setObjectName("RecipeName")
        self.lbl_name.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_name, 1, 2, 1, 2)

        # 🔹 Headings: Servings | Time
        headings_layout = QHBoxLayout()
        headings_layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_servings_heading = QLabel("Servings")
        self.lbl_time_heading = QLabel("Time")
        self.lbl_time_heading.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        headings_layout.addWidget(self.lbl_servings_heading)
        headings_layout.addWidget(self.lbl_time_heading)
        layout.addLayout(headings_layout, 2, 0, 1, 4)

        # 🔹 Servings Value
        servings_layout = QHBoxLayout()
        self.lbl_icon = QLabel()  # Placeholder for icon
        self.lbl_servings = QLabel() # Recipe.servings
        servings_layout.addWidget(self.lbl_icon)
        servings_layout.addWidget(self.lbl_servings, alignment=Qt.AlignBottom)
        layout.addLayout(servings_layout, 3, 1, 2, 1)

        # 🔹 Spacer
        spacer = QSpacerItem(129, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addItem(spacer, 4, 2, 1, 1)

        # 🔹 Time Display
        time_layout = QHBoxLayout()
        self.lbl_time = QLabel() # Recipe.time
        self.lbl_time_suffix = QLabel("min.")
        time_layout.addWidget(self.lbl_time)
        time_layout.addWidget(self.lbl_time_suffix)
        layout.addLayout(time_layout, 4, 3, 1, 1)
