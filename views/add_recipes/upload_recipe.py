"""views/add_recipes/upload_recipe.py

This module provides the functionality to upload a recipe image.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFileDialog
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QSize

from ui.components.dialogs import MessageDialog
from style_manager import WidgetLoader
from config import STYLES, UPLOAD_RECIPE_IMAGE

from core.helpers import DebugLogger
from ui.iconkit import ToolButtonIcon

# ── Class Definition ────────────────────────────────────────────────────────────
class UploadRecipeImage(QWidget):
    """Widget for uploading a recipe image."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("UploadRecipeImage")
        WidgetLoader.apply_widget_style(self, STYLES["UPLOAD_IMAGE"])
        
        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        """Builds the UI components for uploading a recipe image."""

        # Main layout for the widget
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.upload_button = ToolButtonIcon(
            file_path   = UPLOAD_RECIPE_IMAGE["ICON_UPLOAD"]["FILE_PATH"],
            icon_size   = UPLOAD_RECIPE_IMAGE["ICON_UPLOAD"]["ICON_SIZE"],
            button_size = UPLOAD_RECIPE_IMAGE["ICON_UPLOAD"]["BUTTON_SIZE"],
            variant     = UPLOAD_RECIPE_IMAGE["ICON_UPLOAD"]["DYNAMIC"],
        )


        self.layout.addWidget(self.upload_button, alignment=Qt.AlignCenter)
        
    def _connect_signals(self):
        self.upload_button.clicked.connect(self.upload_image)

    def upload_image(self):
        """Open file dialog to select an image and display it."""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select Recipe Image", "", "Images (*.png *.jpg *.jpeg)", options=options
        )
        
        if file_name:
            pixmap = QPixmap(file_name)
            if not pixmap.isNull():
                self.image_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
                DebugLogger.log(f"Image uploaded: {file_name}")
            else:
                MessageDialog.show_error("Invalid image file.")