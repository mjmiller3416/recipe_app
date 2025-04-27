"""helpers/ui_helpers/separator.py

Defines the Separator class, a reusable vertical or horizontal line widget with optional color customization.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtWidgets import QFrame
from PySide6.QtCore import QSize

# ── Class Definition ────────────────────────────────────────────────────────────
class Separator(QFrame):
    """
    A reusable separator line with optional color styling.

    Usage:
        Separator.vertical(height, color="#ccc")
        Separator.horizontal(width, color="#ccc")
    """

    def __init__(self, orientation: str, size: int, color: str = "#38383a", parent=None):
        """Initialize the Separator with orientation, size, and color.

        Args:
            orientation (str): 'vertical' or 'horizontal'.
            size (int): Length of the separator in the main direction.
            color (str, optional): Color hex code or name. Defaults to dark gray.
            parent (QWidget, optional): Optional parent widget.
        """
        super().__init__(parent)

        # ── Set Orientation ──
        if orientation == "vertical":
            self.setFrameShape(QFrame.VLine)
            self.setFixedHeight(size)
            self.setFixedWidth(2)  # Important to lock width for vertical
        elif orientation == "horizontal":
            self.setFrameShape(QFrame.HLine)
            self.setFixedWidth(size)
            self.setFixedHeight(1)  # Important to lock height for horizontal
        else:
            raise ValueError("Orientation must be 'vertical' or 'horizontal'.")

        self.setFrameShadow(QFrame.Plain)
        self.setLineWidth(1)

        # ── Set Color ──
        self.setStyleSheet(f"background-color: {color}; border: none;")

    @classmethod
    def vertical(cls, height: int, color: str = "#38383a", parent=None) -> "Separator":
        """Create a vertical Separator.

        Args:
            height (int): Height of the vertical separator.
            color (str, optional): Color hex code or name. Defaults to dark gray.
            parent (QWidget, optional): Optional parent widget.

        Returns:
            Separator: The configured vertical separator widget.
        """
        return cls("vertical", height, color, parent)

    @classmethod
    def horizontal(cls, width: int, color: str = "#38383a", parent=None) -> "Separator":
        """Create a horizontal Separator.

        Args:
            width (int): Width of the horizontal separator.
            color (str, optional): Color hex code or name. Defaults to dark gray.
            parent (QWidget, optional): Optional parent widget.

        Returns:
            Separator: The configured horizontal separator widget.
        """
        return cls("horizontal", width, color, parent)
