"""helpers/ui_helpers/image_label.py

Defines the Image class, a QLabel subclass for displaying square images with size validation.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtWidgets import QLabel


# ── Class Definition ────────────────────────────────────────────────────────────
class SquareImage(QLabel):
    """A QLabel subclass designed to load, validate, and display scaled square images.

    Args:
        image_path (str): Path to the source image file.
        target_size (int): Desired width and height for the displayed image.
        parent (QWidget, optional): Parent widget.

    Raises:
        FileNotFoundError: If the image file cannot be loaded.
        ValueError: If the original image is not square (1:1 aspect ratio).
        ValueError: If the target size requires upscaling the original image.
    """
    def __init__(self, image_path: str, target_size: int, parent=None):
        super().__init__(parent)

        self.image_path = image_path
        self.target_size = target_size

        # ── Load Image ──
        original_pixmap = QPixmap(self.image_path)

        # validate image loading
        if original_pixmap.isNull():
            raise FileNotFoundError(f"Error: Could not load image at '{self.image_path}'. Check the path and file integrity.")

        # validate image size
        original_dims = original_pixmap.size()
        if original_dims.width() != original_dims.height():
            raise ValueError(f"Error: Image '{self.image_path}' ({original_dims.width()}x{original_dims.height()}) "
                             f"is not square. Only 1:1 aspect ratio images are supported.")

        original_width = original_dims.width()

        # validate target size
        if self.target_size > original_width:
            raise ValueError(f"Error: Target size ({self.target_size}x{self.target_size}) requires upscaling "
                             f"the original image '{self.image_path}' ({original_width}x{original_width}). "
                             f"Upscaling is not allowed due to quality loss.")

        # ── Scale Image ──
        scaled_pixmap = original_pixmap.scaled(self.target_size, self.target_size,
                                               Qt.AspectRatioMode.KeepAspectRatio,
                                               Qt.TransformationMode.SmoothTransformation)

        # set the scaled image to the label
        self.setPixmap(scaled_pixmap)
        self.setFixedSize(self.target_size, self.target_size)
