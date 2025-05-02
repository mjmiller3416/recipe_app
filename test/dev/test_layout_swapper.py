import sys

from PySide6.QtCore import QTimer, Slot
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout,
                               QLabel, QMainWindow, QPushButton, QVBoxLayout,
                               QWidget)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Layout Switcher (Recreate Container)")
        self.resize(450, 350)

        # --- Main Structure ---
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        # This layout holds controls AND the switch_container area
        self.main_container_layout = QVBoxLayout(main_widget)

        # --- Control Buttons ---
        control_widget = QWidget()
        control_layout = QHBoxLayout(control_widget)
        btn_layout1 = QPushButton("Show Vertical Layout")
        btn_layout2 = QPushButton("Show Horizontal Layout")
        btn_layout3 = QPushButton("Show Grid Layout")
        control_layout.addWidget(btn_layout1)
        control_layout.addWidget(btn_layout2)
        control_layout.addWidget(btn_layout3)
        # Add controls to the main layout (will be at index 0)
        self.main_container_layout.addWidget(control_widget)

        # --- Placeholder for the switch container ---
        self.switch_container_widget = None # Reference to the current container

        # --- Connect Signals to Slots ---
        btn_layout1.clicked.connect(self.display_vertical_layout)
        btn_layout2.clicked.connect(self.display_horizontal_layout)
        btn_layout3.clicked.connect(self.display_grid_layout)

        # --- Initial Layout ---
        QTimer.singleShot(0, self.display_vertical_layout)


    def _replace_container_widget(self, new_layout):
        """Removes the old container, creates a new one, applies layout, adds it back."""
        print(f"Replacing container. New layout type: {type(new_layout).__name__}")

        # 1. Remove and delete the OLD container widget (if it exists)
        if self.switch_container_widget is not None:
            print(f"  Removing old container: {self.switch_container_widget}")
            # Remove from its parent layout first
            self.main_container_layout.removeWidget(self.switch_container_widget)
            # Schedule the widget (and its children/layout) for deletion
            self.switch_container_widget.deleteLater()
            self.switch_container_widget = None
            print("  Old container removed and scheduled for deletion.")
        # else:
            # print("  No old container to remo
        # 2. Create a NEW container widget
        self.switch_container_widget = QFrame()
        self.switch_container_widget.setStyleSheet("background-color: #f0f0f0; border: 1px solid grey;")
        self.switch_container_widget.setMinimumHeight(100)
        print(f"  Created new container: {self.switch_container_widget}")

        # 3. Apply the new layout to the NEW container
        self.switch_container_widget.setLayout(new_layout)
        print(f"  Applied new layout ({type(new_layout).__name__}) to new container.")

        # 4. Add the NEW container to the main layout
        # Add it below the controls (index 1), with stretch factor 1
        self.main_container_layout.insertWidget(1, self.switch_container_widget, 1)
        print(f"  Added new container back to main layout.")
        # You might need to explicitly show it, although addWidget usually does
        # self.switch_container_widget.show()


    @Slot()
    def display_vertical_layout(self):
        """Creates a new container with a QVBoxLayout."""
        print("--- Request Vertical Layout ---")
        new_layout = QVBoxLayout()
        # Create widgets WITHOUT specifying a parent initially
        lbl = QLabel("--- Vertical Layout ---")
        btn1 = QPushButton("Button V1")
        lbl2 = QLabel("Another Label")
        btn2 = QPushButton("Button V2")
        # Add widgets to the layout (layout manages parenting later)
        new_layout.addWidget(lbl)
        new_layout.addWidget(btn1)
        new_layout.addWidget(lbl2)
        new_layout.addWidget(btn2)
        print("  New vertical layout object and widgets created.")
        # Replace the whole container widget
        self._replace_container_widget(new_layout)


    @Slot()
    def display_horizontal_layout(self):
        """Creates a new container with an QHBoxLayout."""
        print("--- Request Horizontal Layout ---")
        new_layout = QHBoxLayout()
        new_layout.addWidget(QLabel("--- Horizontal ---"))
        new_layout.addWidget(QPushButton("Button H1"))
        new_layout.addWidget(QPushButton("Button H2"))
        new_layout.addWidget(QLabel("End"))
        print("  New horizontal layout object and widgets created.")
        self._replace_container_widget(new_layout)


    @Slot()
    def display_grid_layout(self):
        """Creates a new container with a QGridLayout."""
        print("--- Request Grid Layout ---")
        new_layout = QGridLayout()
        new_layout.addWidget(QLabel("--- Grid Layout ---"), 0, 0, 1, 2)
        new_layout.addWidget(QPushButton("Grid (1,0)"), 1, 0)
        new_layout.addWidget(QPushButton("Grid (1,1)"), 1, 1)
        new_layout.addWidget(QLabel("Cell (2,0)"), 2, 0)
        new_layout.addWidget(QPushButton("Grid (2,1)"), 2, 1)
        print("  New grid layout object and widgets created.")
        self._replace_container_widget(new_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
