"""app/ui/components/handlers/image_upload_handler.py

ImageUploadHandler for managing recipe image upload and crop workflows.
Extracted from UploadRecipeImage to separate upload logic from display.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
import uuid
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFileDialog, QWidget

from app.config.paths import AppPaths
from dev_tools import DebugLogger

# ── Constants ────────────────────────────────────────────────────────────────────────────────
IMAGE_SAVE_DIR = Path(AppPaths.RECIPE_IMAGES_DIR)

# ── ImageUploadHandler ───────────────────────────────────────────────────────────────────────
class ImageUploadHandler(QObject):
    """Handles recipe image upload and crop workflows.
    
    Separated from display logic to enable reusable upload functionality.
    Works with ImageCard for display or any other display component.
    
    Signals:
        image_uploaded(str): Emitted when image is successfully processed and saved
        upload_failed(str): Emitted when upload/crop process fails
    """
    
    image_uploaded = Signal(str)  # emits path to saved cropped image
    upload_failed = Signal(str)   # emits error message
    
    def __init__(self, parent_widget: QWidget):
        """Initialize the upload handler.
        
        Args:
            parent_widget: Parent widget for dialogs (file dialog, crop dialog)
        """
        super().__init__()
        self.parent_widget = parent_widget
        self.original_selected_file_path: Optional[str] = None
        self.saved_image_path: Optional[str] = None
    
    def start_upload_workflow(self):
        """Start the image upload workflow by opening file dialog."""
        self.open_file_dialog()
    
    def open_file_dialog(self):
        """Open file dialog to select an image."""
        file_filter = "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent_widget,
            "Select Recipe Image",
            "",  # start directory
            file_filter
        )
        
        if file_path:
            self.original_selected_file_path = file_path
            self._launch_crop_dialog(file_path)
    
    def _launch_crop_dialog(self, image_path: str):
        """Launch the RecipeImageCropDialog with the selected image."""
        from app.ui.components.dialogs.crop_dialog import CropDialog
        
        crop_dialog = CropDialog(image_path, self.parent_widget)
        crop_dialog.crop_finalized.connect(self._handle_crop_saved)
        crop_dialog.select_new_image_requested.connect(self._handle_select_new_from_crop_dialog)
        crop_dialog.exec()
    
    @Slot(QPixmap)
    def _handle_crop_saved(self, cropped_pixmap: QPixmap):
        """Save the cropped pixmap and emit success signal."""
        if cropped_pixmap.isNull():
            error_msg = "Cropped pixmap is null, not saving."
            DebugLogger().log(error_msg, "warning")
            self.upload_failed.emit(error_msg)
            return
        
        # Ensure the destination directory exists
        IMAGE_SAVE_DIR.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        unique_filename = f"recipe_{uuid.uuid4().hex}.png"
        save_path = IMAGE_SAVE_DIR / unique_filename
        
        try:
            if cropped_pixmap.save(str(save_path), "PNG"):
                self.saved_image_path = str(save_path)
                DebugLogger().log(f"Cropped image saved to: {save_path}", "info")
                self.image_uploaded.emit(str(save_path))
            else:
                error_msg = f"Failed to save cropped image to: {save_path}"
                DebugLogger().log(error_msg, "error")
                self.upload_failed.emit(error_msg)
        except Exception as e:
            error_msg = f"Exception saving cropped image: {e}"
            DebugLogger().log(error_msg, "error")
            self.upload_failed.emit(error_msg)
    
    @Slot()
    def _handle_select_new_from_crop_dialog(self):
        """Handle request to select a new image from the crop dialog."""
        # The crop dialog would have closed. Now open the file dialog again.
        self.open_file_dialog()
    
    def get_saved_image_path(self) -> Optional[str]:
        """Get the path to the most recently saved image.
        
        Returns:
            Path to saved image or None if no image has been saved
        """
        return self.saved_image_path
    
    def clear_saved_path(self):
        """Clear the saved image path (doesn't delete the file)."""
        self.saved_image_path = None
        self.original_selected_file_path = None