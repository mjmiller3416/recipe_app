"""helpers/icon_helpers/widgets/rounded_icon.py

Defines the RoundedIcon class, a QLabel subclass for displaying SVG icons
within a colored rounded rectangle background.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QLabel, QWidget

from core.application.config import ICON_COLOR
from core.helpers.debug_logger import DebugLogger
from ..loader import SVGLoader, icon_path

# ── Class Definition ────────────────────────────────────────────────────────────
class RoundedIcon(QLabel):
    """
    A QLabel subclass that displays an SVG icon centered within a colored
    rounded rectangle background.

    The size of the label is fixed to the specified logical size.
    """

    def __init__(
        self,
        name:   str,                    # Name of the SVG file (e.g., "my_icon.svg" or "my_icon")
        size:   QSize,                  # Logical size of the entire widget (background included)
        icon_color:  str = ICON_COLOR,  # Color for the SVG icon itself
        background_color: str = "#E0E0E0", # Default background color (light gray)
        border_radius: int = 4,         # Corner radius in logical pixels
        icon_padding: int = 3,          # Padding around icon in logical pixels
        source_color: str = "#000",     # Original color in SVG to replace
        parent: QWidget | None = None   # Parent widget
    ):
        """
        Initialize the RoundedIcon.

        Args:
            name (str): Name of the SVG file (without path, extension optional).
            size (QSize): Desired logical size for the widget.
            icon_color (str, optional): Color to apply to the SVG. Defaults to ICON_COLOR.
            background_color (str, optional): Color for the rounded background. Defaults to "#E0E0E0".
            border_radius (int, optional): Radius for the background corners. Defaults to 4.
            icon_padding (int, optional): Padding between icon and background edge. Defaults to 3.
            source_color (str, optional): Source color in the SVG for replacement. Defaults to "#000".
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)

        # ── Resolve SVG Path ──
        # Use the imported icon_path function
        full_path = icon_path(name)
        # Basic check if path resolution worked (icon_path should handle logging)
        if "invalid.svg" in full_path: # Check against the default invalid path from icon_path
             DebugLogger.log(f"RoundedIcon path for '{name}' could not be resolved or is invalid.", "error")
             # Optionally set a default placeholder or leave blank
             self.setText("?") # Placeholder text
             self.setFixedSize(size)
             self.setAlignment(Qt.AlignCenter)
             self.setStyleSheet(f"background-color: {background_color}; "
                                f"border-radius: {border_radius}px; "
                                f"color: {icon_color};") # Basic fallback style
             return

        # ── Load SVG Icon with Background using the new loader method ──
        pix = SVGLoader.load_with_background(
            path=full_path,
            icon_color=icon_color,
            background_color=background_color,
            border_radius=border_radius,
            size=size,
            icon_padding=icon_padding,
            source=source_color,
            as_icon=False # We need the QPixmap for QLabel
        )

        # ── Set Widget Properties ──
        if not pix.isNull(): # Check if pixmap loading was successful
            self.setPixmap(pix)
        else:
            # Fallback if pixmap is null after loading attempt
            DebugLogger.log(f"RoundedIcon failed to load pixmap for '{name}'.", "error")
            self.setText("!") # Error placeholder
            self.setStyleSheet(f"background-color: {background_color}; "
                               f"border-radius: {border_radius}px; "
                               f"color: red;") # Error indication style

        # Set the size of the QLabel widget itself to the requested logical size
        self.setFixedSize(size)
        # Center the pixmap within the label area
        self.setAlignment(Qt.AlignCenter)
        # Remove any default margins the label might have
        self.setContentsMargins(0, 0, 0, 0)
        # Ensure the QLabel background is transparent, as the pixmap handles the visual background
        self.setStyleSheet("background-color: transparent; border: none;")

