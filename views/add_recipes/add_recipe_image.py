"""views/add_recipes/add_recipe_image.py

This module defines the functionality to upload an image in the Add Recipes view.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
import os
import shutil
from pathlib import Path

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QFileDialog, QVBoxLayout, QLabel, QSizePolicy
from PySide6.QtGui import QPixmap

from ui.iconkit import ToolButtonIcon
from config.config import ADD_RECIPES
from config.paths import AppPaths
from core.helpers import DebugLogger
from ui.components.dialogs import MessageDialog

# ── Class Definition ────────────────────────────────────────────────────────────
class AddRecipeImage(QWidget):
    """Widget for uploading a recipe image."""
    
    # Signal emitted when an image is selected
    image_selected = Signal(str)  # Emits the path to the selected image
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AddRecipeImage")
        
        # Store the selected image path
        self.selected_image_path = None
        
        # Set up the widget layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Create the icon button
        self.btn_add_image = ToolButtonIcon(
            file_path=ADD_RECIPES["ADD_IMAGE"]["FILE_PATH"],
            size=ADD_RECIPES["ADD_IMAGE"]["ICON_SIZE"],
            variant=ADD_RECIPES["ADD_IMAGE"]["DYNAMIC"]
        )
        self.btn_add_image.setToolTip("Click to add recipe image")
        
        # Set size policies for proper layout
        self.btn_add_image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Create label for feedback
        self.lbl_status = QLabel("No image selected")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setObjectName("image_status_label")
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        layout.addWidget(self.btn_add_image, 1)  # Give button more space
        layout.addWidget(self.lbl_status, 0)     # Give label less space
        
        # Set widget size policies
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.setMaximumWidth(200)
        
        # Connect the click signal
        self.btn_add_image.clicked.connect(self.select_image)
    
    def select_image(self):
        """Open file dialog to select an image file."""
        try:
            # Define supported image formats
            image_filters = (
                "Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp);;"
                "PNG Files (*.png);;"
                "JPEG Files (*.jpg *.jpeg);;"
                "All Files (*)"
            )
            
            # Open file dialog
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Recipe Image",
                "",
                image_filters
            )
            
            if file_path:
                self.set_image(file_path)
                
        except Exception as e:
            DebugLogger().log(f"[AddRecipeImage] Error selecting image: {e}", "error")
            MessageDialog("error", "Error", f"Failed to select image: {str(e)}", self).exec()
    
    def set_image(self, file_path: str):
        """Set the selected image and copy it to the recipe images directory."""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Image file not found: {file_path}")
            
            # Ensure the recipe images directory exists
            AppPaths.RECIPE_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
            
            # Generate a unique filename
            original_name = Path(file_path).name
            base_name = Path(file_path).stem
            extension = Path(file_path).suffix
            
            # Create a unique filename to prevent conflicts
            counter = 1
            new_filename = original_name
            destination_path = AppPaths.RECIPE_IMAGES_DIR / new_filename
            
            while destination_path.exists():
                new_filename = f"{base_name}_{counter}{extension}"
                destination_path = AppPaths.RECIPE_IMAGES_DIR / new_filename
                counter += 1
            
            # Copy the file to the recipe images directory
            shutil.copy2(file_path, destination_path)
            
            # Store the relative path (just the filename)
            self.selected_image_path = str(destination_path)
            
            # Update the status label
            self.lbl_status.setText(f"Image: {new_filename}")
            
            # Update button tooltip
            self.btn_add_image.setToolTip(f"Current image: {new_filename}\nClick to change")
            
            # Emit signal with the image path
            self.image_selected.emit(str(destination_path))
            
            DebugLogger().log(f"[AddRecipeImage] Image selected: {destination_path}", "info")
            
        except Exception as e:
            DebugLogger().log(f"[AddRecipeImage] Error setting image: {e}", "error")
            MessageDialog("error", "Error", f"Failed to set image: {str(e)}", self).exec()
    
    def get_image_path(self):
        """Return the selected image path."""
        return self.selected_image_path
    
    def clear_image(self):
        """Clear the selected image."""
        self.selected_image_path = None
        self.lbl_status.setText("No image selected")
        self.btn_add_image.setToolTip("Click to add recipe image")
        self.image_selected.emit("")  # Emit empty string to indicate no image
    
    def mousePressEvent(self, event):
        """Handle mouse press events to make the entire widget clickable."""
        if event.button() == Qt.LeftButton:
            self.select_image()
        super().mousePressEvent(event)

        