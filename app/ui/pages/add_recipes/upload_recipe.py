"""app/ui/pages/add_recipes/upload_recipe.py

UploadRecipeImage widget for uploading and cropping recipe images.
"""


import tempfile
import uuid
from pathlib import Path

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QFileDialog, QLabel, QStackedLayout,
                               QVBoxLayout, QWidget)

from app.config import STYLES, UPLOAD_RECIPE_IMAGE
from app.config.paths import AppPaths
from app.core.utils import DebugLogger
from app.ui.components.dialogs.crop_dialog import CropDialog
from app.ui.helpers.ui_helpers import make_overlay
from app.ui.widgets import CTToolButton, RoundedImage


# Function to ensure a directory exists
def ensure_directory_exists(dir_path: Path):
    dir_path.mkdir(parents=True, exist_ok=True)

# Try to get a dedicated temp dir from AppPaths, otherwise use system temp
try:
    # Assuming AppPaths.TEMP_CROP_DIR or similar might be defined
    # If AppPaths has a general TEMP_DIR:
    # TEMP_IMAGE_DIR = AppPaths.TEMP_DIR / "cropped_recipe_images"
    # For this example, let's assume a specific one or create one.
    if hasattr(AppPaths, 'TEMP_CROP_DIR'):
        TEMP_IMAGE_DIR = Path(AppPaths.TEMP_CROP_DIR)
    elif hasattr(AppPaths, 'TEMP_DIR'):
        TEMP_IMAGE_DIR = Path(AppPaths.TEMP_DIR) / "cropped_recipe_images"
    else: # Fallback if AppPaths has no temp dir defined
        TEMP_IMAGE_DIR = Path(tempfile.gettempdir()) / "recipe_app_crops"
except (ImportError, AttributeError): # Fallback if AppPaths or specific attrs don't exist
    TEMP_IMAGE_DIR = Path(tempfile.gettempdir()) / "recipe_app_crops"

ensure_directory_exists(TEMP_IMAGE_DIR)


class UploadRecipeImage(QWidget):
    image_uploaded = Signal(str)  # emits the path to the CROPPED image

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("UploadRecipeImage")
        self.selected_image_path: Path | None = None # Will store path to the final cropped image
        self.original_selected_file_path: str | None = None # Path from QFileDialog

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        # Use QStackedLayout to switch between upload button and image display
        self.stacked_layout = QStackedLayout(self)
        self.stacked_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.stacked_layout)

        # --- Upload Button (Page 0) ---
        self.upload_button_widget = QWidget() # Container for overlay
        self.upload_button_layout = QVBoxLayout(self.upload_button_widget)
        self.upload_button_layout.setContentsMargins(0,0,0,0)
        self.upload_button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.upload_button = CTToolButton(
            file_path   = UPLOAD_RECIPE_IMAGE["ICON_UPLOAD"]["FILE_PATH"],
            icon_size   = UPLOAD_RECIPE_IMAGE["ICON_UPLOAD"]["ICON_SIZE"],
            button_size = UPLOAD_RECIPE_IMAGE["ICON_UPLOAD"]["BUTTON_SIZE"],
            variant     = UPLOAD_RECIPE_IMAGE["ICON_UPLOAD"]["DYNAMIC"],
        )
        btn_lbl = QLabel("Upload Image")

        self.overlay_widget = make_overlay(
            base_widget=self.upload_button,
            overlay_widget=btn_lbl,
            margins=(0, 0, 0, 10),
            align=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter
        )
        self.upload_button_layout.addWidget(self.overlay_widget)
        self.stacked_layout.addWidget(self.upload_button_widget)

        # --- Image Display (Page 1) ---
        # RoundedImage will be created/updated when an image is processed
        self.image_display: RoundedImage | None = None 
        
        # Ensure the widget has a fixed size based on the button, important for layout stability
        button_qsize = self.upload_button.button_size # This is QSize
        self.setFixedSize(button_qsize)


    def _connect_signals(self):
        self.upload_button.clicked.connect(self.open_file_dialog_for_upload)

    @Slot()
    def open_file_dialog_for_upload(self):
        """Open file dialog to select an image."""
        # TODO: Define image file types (e.g., "Images (*.png *.jpg *.jpeg *.bmp)")
        file_filter = "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Recipe Image",
            "",  # Start directory (e.g., QDir.homePath())
            file_filter
        )
        if file_path:
            self.original_selected_file_path = file_path
            self._launch_crop_dialog(file_path)

    def _launch_crop_dialog(self, image_path: str):
        """Lauches the RecipeImageCropDialog with the selected image."""
        crop_dialog = CropDialog(image_path, self)
        crop_dialog.crop_finalized.connect(self._handle_crop_saved)
        crop_dialog.select_new_image_requested.connect(self._handle_select_new_from_crop_dialog)
        
        # If you used custom result codes in dialog:
        # result = crop_dialog.exec()
        # if result == QDialog.DialogCode.Accepted:
        #     # crop_finalized signal already handled this
        #     pass
        # elif result == RecipeImageCropDialog.SelectNewImageCode:
        #     # select_new_image_requested signal already handled this
        #     pass
        crop_dialog.exec()


    @Slot(QPixmap)
    def _handle_crop_saved(self, cropped_pixmap: QPixmap):
        """Saves the cropped pixmap and updates the UI."""
        if cropped_pixmap.isNull():
            DebugLogger().log("Cropped pixmap is null, not saving.", "warning")
            return

        # Save the cropped QPixmap to a temporary file
        unique_filename = f"cropped_{uuid.uuid4().hex}.png" # Save as PNG for transparency
        temp_image_path = TEMP_IMAGE_DIR / unique_filename
        
        try:
            ensure_directory_exists(TEMP_IMAGE_DIR) # Ensure again just in case
            if cropped_pixmap.save(str(temp_image_path), "PNG"):
                self.selected_image_path = temp_image_path
                DebugLogger().log(f"Cropped image saved to: {temp_image_path}", "info")
                self._update_display_with_image(str(temp_image_path))
                self.image_uploaded.emit(str(temp_image_path))
            else:
                DebugLogger().log(f"Failed to save cropped image to: {temp_image_path}", "error")
                # TODO: Show error to user?
        except Exception as e:
            DebugLogger().log(f"Exception saving cropped image: {e}", "error")

    @Slot()
    def _handle_select_new_from_crop_dialog(self):
        """Handles the request to select a new image from the crop dialog."""
        # The crop dialog would have closed. Now open the file dialog again.
        self.open_file_dialog_for_upload()


    def _update_display_with_image(self, image_path: str):
        """Updates the UI to show the RoundedImage."""
        if self.image_display is None:
            # Create RoundedImage with the same size as the upload button
            button_qsize = self.upload_button.button_size # This is QSize from app.config
            # Determine radii (e.g., fixed, or from style)
            radii = 15 # Example radius
            
            self.image_display = RoundedImage(image_path=image_path, size=button_qsize, radii=radii)
            self.stacked_layout.addWidget(self.image_display) # Add to page 1 (index 1)
        else:
            self.image_display.set_image_path(image_path)
        
        self.stacked_layout.setCurrentWidget(self.image_display)

    def clear_image(self):
        """Resets the widget to show the upload button, clearing any displayed image."""
        if self.selected_image_path:
            # Optionally, delete the temporary cropped image file
            try:
                if self.selected_image_path.exists():
                    self.selected_image_path.unlink()
                    DebugLogger().log(f"Deleted temp cropped image: {self.selected_image_path}", "info")
            except Exception as e:
                DebugLogger().log(f"Error deleting temp image {self.selected_image_path}: {e}", "error")
        
        self.selected_image_path = None
        self.original_selected_file_path = None
        
        # Switch back to the upload button widget
        self.stacked_layout.setCurrentWidget(self.upload_button_widget)
        
        # If RoundedImage was created, you might want to clear its path or hide it
        # If it's on a different page of QStackedLayout, switching pages is enough.
        # If you want to free resources, you could delete and None it:
        # if self.image_display:
        #     self.image_display.deleteLater()
        #     self.image_display = None 
        # However, for QStackedLayout, just switching is fine, it can be reused.
        # Let's clear its path for tidiness if it exists:
        if self.image_display:
            self.image_display.clear_image()