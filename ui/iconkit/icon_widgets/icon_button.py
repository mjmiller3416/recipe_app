"""helpers/icon_helpers/widgets/icon_button.py

Defines the IconButton class, a QPushButton with built-in dynamic hover and checked icon support.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QPushButton

from config.config import ICON_COLOR, ICON_COLOR_CHECKED, ICON_COLOR_HOVER

from ..effects import ApplyHoverEffects
from ..factory import IconFactory


# ── Class Definition ────────────────────────────────────────────────────────────
class IconButton(QPushButton):
    """A QPushButton subclass that displays dynamic icons for default, hover, and checked states.

    Icons automatically update based on hover and checked status.
    """

    def __init__(
        self,
        path: str,
        size: QSize,
        default_color: str = ICON_COLOR,
        hover_color:   str = ICON_COLOR_HOVER,
        checked_color: str = ICON_COLOR_CHECKED,
        parent=None
    ):
        """Initialize the IconButton with dynamic icons.

        Args:
            path (str): Path to the base SVG icon file.
            size (QSize): Desired icon size.
            default_color (str, optional): Color for default state. Defaults to ICON_COLOR.
            hover_color (str, optional): Color for hover state. Defaults to ICON_COLOR_HOVER.
            checked_color (str, optional): Color for checked state. Defaults to ICON_COLOR_CHECKED.
            parent (QWidget, optional): Parent widget.
        """
        super().__init__(parent)

        # ── Create Icon ──
        default_i, hover_i, checked_i = IconFactory.make_icons(
            path, size, default_color, hover_color, checked_color
        )

        # ── Setup Button ──
        self.setIcon(default_i if not self.isChecked() else checked_i)
        self.setIconSize(size)
        self.setStyleSheet("background:transparent; border:none;")

        # ── Apply Hover Effects ──
        ApplyHoverEffects.apply(self, default_i, hover_i, checked_i)
