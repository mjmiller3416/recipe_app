"""app/theme_manager/icon/icon.py

Module providing Icon widget for theme-aware SVG icons.

Icon is a QLabel-based widget that renders an SVG icon and adapts
to theme changes automatically.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QLabel

from app.config import FALLBACK_COLOR
from app.theme_manager.icon.config import Name, State
from app.theme_manager.icon.loader import IconLoader
from app.theme_manager.icon.svg_loader import SVGLoader

# ── Icon  ────────────────────────────────────────────────────────────────────────────────────
class Icon(QLabel):
    """A QLabel-based widget for displaying themed SVG icons."""
    def __init__(self, icon: Name, parent=None):
        """
        Args:
            icon (Name): The pre-configured icon enum.
            parent: The parent widget. Defaults to None.
        """
        super().__init__(parent)

        # Store the icon configuration
        self._icon_enum = icon
        self._icon_spec = icon.spec
        self._custom_size = None
        self._custom_color = None

        # Set up the widget
        self.setFixedSize(self._icon_spec.size.value)
        self.setStyleSheet("background-color: transparent;")
        self.setObjectName(self._icon_spec.name.value)

        # Register for theme updates and render initial icon
        IconLoader.register(self)

    def setSize(self, width: int, height: int):
        """Set custom icon size."""
        self._custom_size = QSize(width, height)
        self.setFixedSize(self._custom_size)
        self._render_icon()

    def setColor(self, color: str):
        """Set custom icon color (hex color or palette role)."""
        self._custom_color = color
        self._render_icon()

    def _render_icon(self):
        """Render the icon with current settings."""
        # Determine size
        size = self._custom_size if self._custom_size else self._icon_spec.size.value

        # Determine color
        if self._custom_color:
            if self._custom_color.startswith("#"):
                color = self._custom_color
            else:
                # It's a palette role
                palette = IconLoader.get_palette()
                color = palette.get(self._custom_color, FALLBACK_COLOR)
        else:
            # Use default color
            palette = IconLoader.get_palette()
            color = palette.get("on_surface", FALLBACK_COLOR)

        # Load and set the pixmap
        pixmap = SVGLoader.load(
            file_path=self._icon_spec.name.path,
            color=color,
            size=size,
            as_icon=False
        )
        self.setPixmap(pixmap)

    def refresh_theme(self, palette: dict[str, str]):
        """Called by IconLoader when theme changes."""
        self._render_icon()
