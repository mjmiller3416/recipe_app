#!/usr/bin/env python3
"""
Test script for AddRecipeImage widget functionality.

This script creates a minimal test environment to verify the image upload widget
works correctly without needing to run the full application.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import QSize

from views.add_recipes.add_recipe_image import AddRecipeImage
from config.paths import AppPaths


class TestWindow(QWidget):
    """Simple test window for the AddRecipeImage widget."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test AddRecipeImage Widget")
        self.setFixedSize(400, 500)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("AddRecipeImage Widget Test")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Status label
        self.status_label = QLabel("No image selected")
        self.status_label.setStyleSheet("padding: 10px; background-color: #f0f0f0; border: 1px solid #ccc;")
        layout.addWidget(self.status_label)
        
        # The image upload widget
        self.image_widget = AddRecipeImage()
        self.image_widget.image_selected.connect(self.on_image_selected)
        layout.addWidget(self.image_widget)
        
        # Test buttons
        clear_btn = QPushButton("Clear Image")
        clear_btn.clicked.connect(self.clear_image)
        layout.addWidget(clear_btn)
        
        get_path_btn = QPushButton("Get Image Path")
        get_path_btn.clicked.connect(self.show_path)
        layout.addWidget(get_path_btn)
        
        # Create recipe images directory for testing
        AppPaths.RECIPE_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    
    def on_image_selected(self, image_path: str):
        """Handle image selection."""
        if image_path:
            filename = Path(image_path).name
            self.status_label.setText(f"Image selected: {filename}")
            self.status_label.setStyleSheet("padding: 10px; background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724;")
        else:
            self.status_label.setText("No image selected")
            self.status_label.setStyleSheet("padding: 10px; background-color: #f0f0f0; border: 1px solid #ccc;")
    
    def clear_image(self):
        """Clear the selected image."""
        self.image_widget.clear_image()
    
    def show_path(self):
        """Show the current image path."""
        path = self.image_widget.get_image_path()
        if path:
            print(f"Current image path: {path}")
            self.status_label.setText(f"Path: {Path(path).name}")
        else:
            print("No image selected")
            self.status_label.setText("No image path available")


def main():
    """Run the test application."""
    app = QApplication(sys.argv)
    
    # Set a basic style for testing
    app.setStyleSheet("""
        QWidget {
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 12px;
        }
        QPushButton {
            padding: 8px 16px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            margin: 2px;
        }
        QPushButton:hover {
            background-color: #0056b3;
        }
        QPushButton:pressed {
            background-color: #004085;
        }
    """)
    
    window = TestWindow()
    window.show()
    
    print("Test window opened. You can:")
    print("1. Click the image widget to select an image")
    print("2. Use 'Clear Image' button to clear selection")
    print("3. Use 'Get Image Path' button to see current path")
    print("4. Check the console for debug output")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
