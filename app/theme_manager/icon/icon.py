"""app/theme_manager/icon/icon.py

Module providing Icon widget for theme-aware SVG icons.

Icon is a QLabel-based widget that renders an SVG icon and adapts
to theme changes automatically.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import QSize

from app.theme_manager.icon.config import Name
from app.theme_manager.icon.loader import IconLoader
from app.theme_manager.icon.factory import IconFactory

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

        # store the icon and its configuration
        self.app_icon = icon
        self._custom_size = None  # Track if using custom size
        spec = icon.spec

        self.setFixedSize(spec.size.value)
        self.setStyleSheet("background-color: transparent;")
        self.setObjectName(spec.name.value)

        # this call handles the initial drawing of the icon.
        IconLoader.register(self)

    def setSize(self, width: int, height: int):
        """
        Manually set the icon size.

        Args:
            width (int): The width in pixels.
            height (int): The height in pixels.
        """
        from app.theme_manager.icon.svg_loader import SVGLoader
        from app.theme_manager.icon.config import State
        
        custom_size = QSize(width, height)
        self.setFixedSize(custom_size)
        self._custom_size = custom_size

        # Create pixmap directly with custom size, bypassing cache
        factory = IconFactory(self.app_icon)
        color = factory.resolve_color(State.DEFAULT)
        
        pixmap = SVGLoader.load(
            file_path=factory.file_path,
            color=color,
            size=custom_size,
            as_icon=False
        )
        self.setPixmap(pixmap)

    def refresh_theme(self, palette: dict[str, str]):
        """Redraw icon using the current theme palette."""
        if self._custom_size:
            # Use custom size with direct SVG loading
            from app.theme_manager.icon.svg_loader import SVGLoader
            from app.theme_manager.icon.config import State
            
            factory = IconFactory(self.app_icon)
            color = factory.resolve_color(State.DEFAULT)
            
            pixmap = SVGLoader.load(
                file_path=factory.file_path,
                color=color,
                size=self._custom_size,
                as_icon=False
            )
            self.setPixmap(pixmap)
        else:
            # Use normal factory method
            factory = IconFactory(self.app_icon)
            self.setPixmap(factory.pixmap_for_state())
