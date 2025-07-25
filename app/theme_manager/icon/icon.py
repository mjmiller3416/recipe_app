"""app/theme_manager/icon/icon.py

Module providing Icon widget for theme-aware SVG icons.

Icon is a QLabel-based widget that renders an SVG icon and adapts
to theme changes automatically.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from PySide6.QtWidgets import QLabel
from app.theme_manager.icon.config import AppIcon
from app.theme_manager.icon.loader import IconLoader
from app.theme_manager.icon.factory import IconFactory

# ── Icon  ────────────────────────────────────────────────────────────────────────────────────
class Icon(QLabel):
    """A QLabel-based widget for displaying themed SVG icons."""
    def __init__(self, icon: AppIcon, parent=None):
        """
        Args:
            icon (AppIcon): The pre-configured icon enum.
            parent: The parent widget. Defaults to None.
        """
        super().__init__(parent)

        # store the icon and its configuration
        self.app_icon = icon
        spec = icon.spec

        self.setFixedSize(spec.size.value)
        self.setStyleSheet("background-color: transparent;")
        self.setObjectName(spec.name.value)

        # this call handles the initial drawing of the icon.
        IconLoader.register(self)

    def refresh_theme(self, palette: dict[str, str]):
        """Redraw icon using the current theme palette."""
        factory = IconFactory(self.app_icon)
        # change this line to use the new method
        self.setPixmap(factory.pixmap_for_state())
