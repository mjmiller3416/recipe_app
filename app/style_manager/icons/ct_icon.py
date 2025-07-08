"""Module providing CTIcon widget for theme-aware SVG icons.

CTIcon is a QLabel-based widget that renders an SVG icon and adapts
to theme changes automatically.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QLabel

from app.style_manager.icons.loader import IconLoader
from app.style_manager.icons.factory import IconFactory


# ── Class Definition ────────────────────────────────────────────────────────────
class CTIcon(QLabel):
    """
    QLabel widget that displays a themed SVG icon.
    Automatically updates when the application theme changes.
    """

    def __init__(
        self,
        file_path: Path,
        icon_size: QSize,
        variant: str = "DEFAULT",
        parent=None
    ):
        super().__init__(parent)

        self.file_path = file_path
        self.size = icon_size
        self.variant = variant.upper()

        self.setFixedSize(self.size)
        self.setStyleSheet("background-color: transparent;")
        self.setObjectName(Path(file_path).stem)

        IconLoader().register(self)  # auto-tracked for theme refresh
        self.refresh_theme(IconLoader().palette)

    def refresh_theme(self, palette: dict):
        """Refreshes the displayed icon with current theme colors."""
        themed_icon = IconFactory(self.file_path, self.size, self.variant)
        self.setPixmap(themed_icon.pixmap())
