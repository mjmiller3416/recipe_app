"""helpers/ui_helpers/rounded_image_label.py

Provides the RoundedImage class and a factory function for creating QLabel widgets with rounded images.
"""

from pathlib import Path
# ── Imports ─────────────────────────────────────────────────────────────────────
from typing import Tuple, Union

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QLabel


# ── Class Definition ────────────────────────────────────────────────────────────
class RoundedImage(QLabel):
    def __init__(
        self,
        image_path: str,
        size: Union[int, QSize] = 300,
        radii: Union[int, Tuple[int, int, int, int]] = 20
    ) -> None:
        super().__init__()
        self._image_path = image_path # Store original path
        self._size_arg = size        # Store original size arg
        self._radii_arg = radii      # Store original radii arg
        self._apply_style()

    def _apply_style(self) -> None:
        # Normalize Size
        current_size: QSize
        if isinstance(self._size_arg, int):
            current_size = QSize(self._size_arg, self._size_arg)
        elif isinstance(self._size_arg, QSize):
            current_size = self._size_arg
        else:
            # Fallback or raise error, for now, using a default
            print(f"Warning: Invalid size '{self._size_arg}' for RoundedImage. Using 300x300.")
            current_size = QSize(300, 300)
        
        self.setFixedSize(current_size)

        # Normalize Radii Values
        tl: int; tr: int; br: int; bl: int
        if isinstance(self._radii_arg, int):
            tl = tr = br = bl = self._radii_arg
        elif isinstance(self._radii_arg, (tuple, list)) and len(self._radii_arg) == 4:
            tl, tr, br, bl = self._radii_arg
        else:
            # Fallback or raise error
            print(f"Warning: Invalid radii '{self._radii_arg}' for RoundedImage. Using 20px.")
            tl = tr = br = bl = 20
            
        # Construct Stylesheet
        # Ensure the path is suitable for CSS url() (forward slashes)
        css_path = Path(self._image_path).as_posix() if self._image_path else ""
        
        stylesheet = f"""
        QLabel {{
            border-image: url('{css_path}') 0 0 0 0 stretch stretch;
            border-top-left-radius: {tl}px;
            border-top-right-radius: {tr}px;
            border-bottom-right-radius: {br}px;
            border-bottom-left-radius: {bl}px;
            background-color: transparent; /* Ensure no opaque background interferes */
        }}
        """
        self.setStyleSheet(stylesheet)
        self.update() # Ensure repaint

    def set_image_path(self, image_path: str) -> None:
        """Updates the image displayed by this widget."""
        self._image_path = image_path
        self._apply_style()

    def clear_image(self) -> None:
        """Clears the displayed image."""
        self._image_path = "" # Or path to a transparent placeholder
        self._apply_style() # Re-apply with empty path, effectively clearing