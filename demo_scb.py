\
import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QLabel
from PySide6.QtCore import Slot, Qt # Import Qt

# Assuming demo_scb.py is in the root of recipe_app,
# and the script is run from the recipe_app root,
# or recipe_app is in PYTHONPATH.
from ui.components.inputs.smart_combobox import SmartComboBox

class SmartComboBoxDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmartComboBox Demo")
        self.setGeometry(100, 100, 700, 500)  # Adjusted size for better layout

        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        # Label to display selection
        self.selection_label = QLabel("No selection yet.", self)
        self.selection_label.setAlignment(Qt.AlignCenter) # Center align text
        main_layout.addWidget(self.selection_label)

        # Grid for SmartComboBoxes
        grid_layout = QGridLayout()
        main_layout.addLayout(grid_layout)

        self.smart_comboboxes = []
        # Sample items for the comboboxes - ensure this list is not empty
        sample_items = [f"Option {i}" for i in range(1, 21)] 
        if not sample_items:
            sample_items = ["Default Item 1", "Default Item 2"] # Fallback

        for i in range(3):  # 3 rows
            for j in range(3):  # 3 columns
                scb = SmartComboBox(
                    list_items=sample_items,
                    placeholder=f"Select ({i+1},{j+1})"
                )
                # Connect the signal to the handler
                scb.selection_trigger.connect(self.update_selection_label)
                grid_layout.addWidget(scb, i, j)
                self.smart_comboboxes.append(scb)

    @Slot(str)
    def update_selection_label(self, selected_text: str):
        """
        Handles the selection_trigger signal from any SmartComboBox.
        Updates the label to display the selected text.
        """
        self.selection_label.setText(f"Selected: {selected_text}")

def main():
    app = QApplication(sys.argv)

    # Note: For this demo to run correctly, the Python environment
    # must be able to find the 'ui', 'config', 'core' modules
    # as imported by SmartComboBox and its dependencies.
    # This usually means running the script from the project root directory
    # (g:\\My Drive\\Python\\recipe_app) or ensuring this directory is in PYTHONPATH.
    # Also, the icon paths in 'config.py' (SMART_COMBOBOX setting) must be valid.

    demo_window = SmartComboBoxDemo()
    demo_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    # This ensures that the main function is called only when the script is executed directly.
    # Add the project root to sys.path to help with module resolution if needed,
    # though it's better if the execution environment handles this (e.g., running from root).
    # import os
    # project_root = os.path.dirname(os.path.abspath(__file__))
    # if project_root not in sys.path:
    #     sys.path.insert(0, project_root)
    
    main()
