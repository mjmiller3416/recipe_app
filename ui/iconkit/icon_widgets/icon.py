"""ui/iconkit/icon_widgets/icon.py

Defines the Icon class, a QLabel-based widget for displaying SVG icons with theme-aware coloring.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QLabel

from core.controllers.icon_controller import IconController
from ui.iconkit.themed_icon import ThemedIcon


# ── Class Definition ────────────────────────────────────────────────────────────
class Icon(QLabel):
    """
    QLabel widget that displays a themed SVG icon.
    Automatically updates when the application theme changes.
    """

    def __init__(
        self,
        file_name: str,
        size: QSize,
        variant: str = "default",
        parent=None
    ):
        super().__init__(parent)

        self.file_name = file_name
        self.size = size
        self.variant = variant

        self.setFixedSize(self.size)
        self.setStyleSheet("background-color: transparent;")

        IconController().register(self)  # auto-tracked for theme refresh
        self.refresh_theme(IconController().palette)

    def refresh_theme(self, palette: dict):
        """Refreshes the displayed icon with current theme colors."""
        themed_icon = ThemedIcon(self.file_name, self.size, self.variant)
        self.setPixmap(themed_icon.pixmap())
