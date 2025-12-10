"""app/ui/components/dialogs/crop_dialog.py

A dialog for cropping images with a square selection area.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QDialog,
    QWidget)

from _dev_tools import DebugLogger
from app.config import AppConfig
from app.ui.components.images.image_cropper import ImageCropper
from app.ui.components.widgets.button import Button
from app.ui.utils import load_pixmap_or_warn, center_on_screen


class DialogWindow(QDialog):
    """Base dialog with frameless window and title bar."""

    def __init__(self, title: str = "", width: int = 800, height: int = 600, parent=None):
        super().__init__(parent)  # <-- Fixed: Just pass parent to QDialog

        # Window setup
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setMinimumSize(400, 300)
        self.resize(width, height)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Content area - subclasses add widgets here
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(self.content_widget)

        center_on_screen(self)

class CropDialog(DialogWindow):
    """A dialog for cropping images with a square selection area."""

    crop_finalized = Signal(QPixmap)
    select_new_image_requested = Signal()

    def __init__(self, image_path: str, parent=None):
        """Initializes the CropDialog.
        Args:
            image_path (str): Path to the initial image to be cropped.
            parent (QWidget, optional): Parent widget that owns the dialog.
        """
        super().__init__(title="Crop Recipe Image", width=800, height=800, parent=parent)  # <-- Fixed

        self.initial_image_path = image_path
        self.original_pixmap = load_pixmap_or_warn(image_path, self)

        self._build_ui()
        self._connect_signals()

        self.image_cropper.set_original_pixmap(self.original_pixmap)

    def _build_ui(self):
        """Builds the UI layout for the crop dialog."""
        # ── Instructions ──
        self.instruction_label = QLabel(
            "Adjust the square selection to choose your crop area.\n"
            "Minimum crop size is 280x280 pixels."
        )
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instruction_label.setWordWrap(True)
        self.content_layout.addWidget(self.instruction_label)

        # ── Cropper Area ──
        cropper_frame = QFrame()
        cropper_frame.setFrameShape(QFrame.Shape.StyledPanel)
        cropper_layout = QVBoxLayout(cropper_frame) # layout for the frame itself
        cropper_layout.setContentsMargins(0,0,0,0)

        self.image_cropper = ImageCropper(self.original_pixmap)
        cropper_layout.addWidget(self.image_cropper)

        self.content_layout.addWidget(cropper_frame, 1) # add frame to self.content_layout

        # ── Buttons ──
        (
            self.btn_select_new,
            self.btn_cancel,
            self.btn_save,
            self.buttons_layout,
        ) = self._build_crop_buttons()

        self.content_layout.addLayout(self.buttons_layout)

    def _connect_signals(self):
        self.btn_save.clicked.connect(self._on_save)
        self.btn_cancel.clicked.connect(self.reject) # QDialog's reject slot
        self.btn_select_new.clicked.connect(self._on_select_new)

    @Slot()
    def _on_save(self):
        cropped_pixmap = self.image_cropper.get_cropped_qpixmap()
        if not cropped_pixmap.isNull():
            # Validate final size against original minimum
            if cropped_pixmap.width() < AppConfig.MIN_CROP_DIM_ORIGINAL or cropped_pixmap.height() < AppConfig.MIN_CROP_DIM_ORIGINAL:
                pass # Assume cropper logic enforced this

            self.crop_finalized.emit(cropped_pixmap)
            self.accept() # QDialog's accept slot
        else:
            # Handle error - e.g., show a message
            DebugLogger.log("Failed to get valid cropped image from dialog", "error")
            # Potentially show a QMessageBox to the user

    def _build_crop_buttons(self) -> tuple[Button, Button, Button, QHBoxLayout]:
        """Create Select-New, Cancel and Save buttons with standard layout."""
        btn_select_new = Button("Select New Image")
        btn_select_new.setObjectName("Button")

        btn_cancel = Button("Cancel")
        btn_cancel.setObjectName("Button")

        btn_save = Button("Save Crop")
        btn_save.setObjectName("Button")
        btn_save.setDefault(True)

        layout = QHBoxLayout()
        layout.setSpacing(10)
        layout.addWidget(btn_select_new)
        layout.addSpacerItem(
            QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )
        layout.addWidget(btn_cancel)
        layout.addWidget(btn_save)

        return btn_select_new, btn_cancel, btn_save, layout

    @Slot()
    def _on_select_new(self):
        self.select_new_image_requested.emit()
        # Close this dialog with a custom code, or just reject.
        # If UploadRecipeImage handles the signal by re-opening file dialog,
        # then this dialog just needs to close.
        self.done(AppConfig.SELECT_NEW_IMAGE_CODE)

    # Optional: Method to get the pixmap if not using signals for some reason
    def get_final_cropped_pixmap(self) -> QPixmap:
        return self.image_cropper.get_cropped_qpixmap()

    # Override showEvent to ensure the pixmap is scaled correctly after layout adjustments
    def showEvent(self, event):
        super().showEvent(event)
        # Ensures the cropper label has its final size before initial scaling
        if not self.original_pixmap.isNull():
             self.image_cropper._update_scaled_pixmap_and_crop_rect()
