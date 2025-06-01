"""helpers/ui_helpers/rounded_image_label.py

Provides the RoundedImage class and a factory function for creating QLabel widgets with rounded images.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from typing import Tuple, Union

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QLabel


# ── Class Definition ────────────────────────────────────────────────────────────
class RoundedImage(QLabel):
    """A QLabel subclass that displays an image with rounded corners.

    Applies a Qt stylesheet mask to create smooth vector-rounded edges without manual painting.
    """

    def __init__(
        self,
        image_path: str,
        size: Union[int, QSize] = 300,
        radii: Union[int, Tuple[int, int, int, int]] = 20
    ) -> None:
        """Initialize the RoundedImage.

        Args:
            image_path (str): Path to the source image file.
            size (int or QSize, optional): Dimension (square) or QSize object. Defaults to 300.
            radii (int or Tuple[int, int, int, int], optional): Corner radius values.
        """
        super().__init__()

        # ── Normalize Size ──
        if isinstance(size, int):
            size = QSize(size, size)
        elif not isinstance(size, QSize):
            raise ValueError("size must be an int or QSize")

        self.setFixedSize(size)

        # ── Normalize Radii Values ──
        if isinstance(radii, int):
            tl = tr = br = bl = radii
        elif isinstance(radii, (tuple, list)) and len(radii) == 4:
            tl, tr, br, bl = radii
        else:
            raise ValueError("radii must be an int or a 4-tuple of ints")

        # ── Construct Stylesheet ──
        stylesheet = f"""
        QLabel {{
            border-image: url('{image_path}') 0 0 0 0 stretch stretch;
            border-top-left-radius: {tl}px;
            border-top-right-radius: {tr}px;
            border-bottom-right-radius: {br}px;
            border-bottom-left-radius: {bl}px;
        }}
        """
        self.setStyleSheet(stylesheet)
