"""views/add_recipes/upload_recipe.py

UploadRecipeImage widget for uploading and cropping recipe images.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
import shutil
import time
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QDialog, QFileDialog, QLabel, QVBoxLayout,
                               QWidget)

from config import STYLES, UPLOAD_RECIPE_IMAGE
from config.paths import AppPaths
from core.helpers import DebugLogger
from core.helpers.ui_helpers import make_overlay
from style_manager import WidgetLoader
from ui.components.dialogs import ImageCropDialog, MessageDialog
from ui.components.dialogs.image_crop_dialog import CROP_SIZE
from ui.components.images import RoundedImage
from ui.iconkit import ToolButtonIcon

# ── Class Definition ────────────────────────────────────────────────────────────
class UploadRecipeImage(QWidget):
    """Widget for uploading and cropping a recipe image"""
    
    image_uploaded = Signal(str)  # emits the path to the cropped image

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("UploadRecipeImage")
        WidgetLoader.apply_widget_style(self, STYLES["UPLOAD_IMAGE"]) # apply the upload image style
        
        self.selected_image_path = None
        
        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        """Builds the UI components for uploading a recipe image."""        
        self.layout = QVBoxLayout(self) # main layout for the widget
        self.upload_button = ToolButtonIcon(
            file_path   = UPLOAD_RECIPE_IMAGE["ICON_UPLOAD"]["FILE_PATH"],
            icon_size   = UPLOAD_RECIPE_IMAGE["ICON_UPLOAD"]["ICON_SIZE"],
            button_size = UPLOAD_RECIPE_IMAGE["ICON_UPLOAD"]["BUTTON_SIZE"],
            variant     = UPLOAD_RECIPE_IMAGE["ICON_UPLOAD"]["DYNAMIC"],
        )
        btn_lbl = QLabel("Upload Image")

        # ── overlay label ──
        self.overlay_widget = make_overlay(
            base_widget=self.upload_button,
            overlay_widget=btn_lbl,
            margins=(0, 0, 0, 10),  # left, top, right, bottom
            align=Qt.AlignBottom | Qt.AlignCenter
        )

        self.layout.addWidget(self.overlay_widget) # add the upload button with label overlay

        self.image_display = None # will hold the displayed image after upload
        
    def _connect_signals(self):
        """Connect button signals."""
        self.upload_button.clicked.connect(self.upload_image)
    
    def _on_image_clicked(self, event):
        """
        Handle click on the displayed image to re-upload.
        
        Args:
            event (QMouseEvent): The mouse event containing button information.
        """
        if event.button() == Qt.LeftButton:
            self.upload_image()
    
    def upload_image(self):
        """Open file dialog to select an image, then crop it."""
        try:
            # define supported image formats
            image_filters = (
                "Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp);;"
                "PNG Files (*.png);;"
                "JPEG Files (*.jpg *.jpeg);;"
                "All Files (*)"
            )
            
            # ── open file dialog ──
            file_name, _ = QFileDialog.getOpenFileName(
                self, 
                "Select Recipe Image", 
                "", 
                image_filters
            )
            
            if not file_name:
                return
            
            # ── validate image ──
            pixmap = QPixmap(file_name)
            if pixmap.isNull():
                MessageDialog("error", "Invalid Image", "The selected file is not a valid image.", self).exec()
                return
            
            # ── check minimize size ──
            if pixmap.width() < CROP_SIZE or pixmap.height() < CROP_SIZE:
                MessageDialog(
                    "error", 
                    "Image Too Small", 
                    f"Image must be at least {CROP_SIZE}×{CROP_SIZE} pixels.\n"
                    f"Selected image is {pixmap.width()}×{pixmap.height()} pixels.",
                    self
                ).exec()
                return
            
            # ── open crop dialog ──
            crop_dialog = ImageCropDialog(file_name, self)
            if crop_dialog.exec() == QDialog.Accepted:
                cropped_path = crop_dialog.get_cropped_image_path()
                if cropped_path:
                    # copy cropped image to recipe images directory
                    self._save_cropped_image(cropped_path)
            
        except Exception as e:
            DebugLogger.log(f"Error in upload_image: {e}", "error")
            MessageDialog("error", "Error", f"Failed to upload image: {str(e)}", self).exec()
    
    def _save_cropped_image(self, temp_cropped_path: str):
        try:
            # generate a unique filename with timestamp
            timestamp = int(time.time())
            temp_filename = Path(temp_cropped_path).stem
            
            # remove "recipe_cropped_" prefix if it already exists to avoid duplication
            if temp_filename.startswith("recipe_cropped_"):
                base_name = temp_filename[15:]  # remove "recipe_cropped_" (15 characters)
            else:
                base_name = temp_filename
                
            final_filename = f"recipe_cropped_{base_name}_{timestamp}.png"
            destination_path = AppPaths.RECIPE_IMAGES_DIR / final_filename
            
            # copy the cropped file to the recipe images directory
            shutil.copy2(temp_cropped_path, destination_path) # store the path and update UI
            self.selected_image_path = str(destination_path)
            
            # ── diaply cropped image ──
            if self.image_display:
                # remove existing image display
                self.layout.removeWidget(self.image_display)
                self.image_display.deleteLater()
            
            # ── create RoundedImage display ──
            button_size = UPLOAD_RECIPE_IMAGE["ICON_UPLOAD"]["BUTTON_SIZE"]
            self.image_display = RoundedImage(
                image_path=str(destination_path),
                size=button_size,
                radii=(16, 16, 16, 16)
            )
            
            # make the image clickable for re-uploading
            self.image_display.mousePressEvent = self._on_image_clicked
            
            # add to layout and show/hide appropriate widgets
            self.layout.addWidget(self.image_display) #
            self.overlay_widget.hide() #
            self.image_uploaded.emit(str(destination_path)) #
            DebugLogger.log(f"Cropped image saved: {destination_path}", "info") #

            # ---- DIAGNOSTIC: DELAYED STYLE REFRESH ----
            from PySide6.QtCore import QTimer

            def refresh_image_style():
                if self.image_display:
                    DebugLogger.log(f"Attempting to refresh style for image_display. Current size: {self.image_display.size()}", "debug") # Add .size()
                    self.image_display.style().unpolish(self.image_display)
                    self.image_display.style().polish(self.image_display)
                    self.image_display.update()
                    DebugLogger.log(f"Style refreshed. Is image visible: {self.image_display.isVisible()}, New size: {self.image_display.size()}", "debug") # Add .size()

            # Schedule the refresh to happen after a short moment (e.g., 100-250 milliseconds)
            # This gives the file system and Qt's event loop a moment to settle.
            QTimer.singleShot(250, refresh_image_style)
            # ---- END DIAGNOSTIC ----

            # clean up temporary file
            try:
                Path(temp_cropped_path).unlink() #
            except Exception as e: # Be more specific with exception if possible
                DebugLogger.log(f"Error deleting temp file {temp_cropped_path}: {e}", "warning")
                pass  # don't fail if temp cleanup fails
                
                # ── Emit Signal ──
                self.image_uploaded.emit(str(destination_path))
                DebugLogger.log(f"Cropped image saved: {destination_path}", "info")
                
                # clean up temporary file
                try:
                    Path(temp_cropped_path).unlink()
                except:
                    pass  # don't fail if temp cleanup fails
                
        except Exception as e:
            DebugLogger.log(f"Error saving cropped image: {e}", "error")            
            MessageDialog("error", "Error", f"Failed to save cropped image: {str(e)}", self).exec()
    
    def get_image_path(self) -> str:
        """Get the path to the selected and cropped image."""
        return self.selected_image_path or ""
    
    def clear_image(self):
        """Clear the selected image."""
        self.selected_image_path = None
        
        # remove the image display if it exists
        if self.image_display:
            self.layout.removeWidget(self.image_display)
            self.image_display.deleteLater()
            self.image_display = None
        
        self.overlay_widget.show()  # show the upload button again