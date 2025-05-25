#!/usr/bin/env python3
"""
Simple test script to verify the AddRecipeImage widget functionality.
This script opens just the image widget in isolation for testing.
"""

import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PySide6.QtCore import Qt

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import our widget
from views.add_recipes.add_recipe_image import AddRecipeImage

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AddRecipeImage Widget Test")
        self.setGeometry(100, 100, 400, 300)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Add title
        title = QLabel("Testing AddRecipeImage Widget")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Create and add our image widget
        self.image_widget = AddRecipeImage()
        layout.addWidget(self.image_widget)
        
        # Connect signal to see when images are selected
        self.image_widget.image_selected.connect(self.on_image_selected)
        
        # Add status label
        self.status_label = QLabel("No image selected")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
          # Add clear button for testing
        clear_button = QPushButton("Clear Image")
        clear_button.clicked.connect(self.image_widget.clear_image)
        layout.addWidget(clear_button)
        
        # Add get path button for testing
        get_path_button = QPushButton("Get Current Path")
        get_path_button.clicked.connect(self.show_current_path)
        layout.addWidget(get_path_button)
        
    def on_image_selected(self, file_path):
        """Handle image selection signal."""
        self.status_label.setText(f"Image selected: {os.path.basename(file_path)}")
        print(f"Signal received: image_selected('{file_path}')")
        
    def show_current_path(self):
        """Show the current image path."""
        current_path = self.image_widget.get_image_path()
        if current_path:
            self.status_label.setText(f"Current path: {os.path.basename(current_path)}")
            print(f"Current image path: {current_path}")
        else:
            self.status_label.setText("No image path set")
            print("No image path set")

def main():
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("AddRecipeImage Test")
    app.setApplicationVersion("1.0")
    
    # Create and show the test window
    window = TestWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
