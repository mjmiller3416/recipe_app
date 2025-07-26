"""app/theme_manager/icon/icon.py

Module providing Icon widget for theme-aware SVG icons.

Icon is a QLabel-based widget that renders an SVG icon and adapts
to theme changes automatically.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QLabel

from app.theme_manager.icon.config import Name, State
from app.theme_manager.icon.factory import IconFactory
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

        # store the icon and its configuration
        self.app_icon = icon
        self._custom_size = None  # Track if using custom size
        self._custom_color = None  # Track if using custom color
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

    def setColor(self, color: str):
        """
        Manually set the icon color.

        Args:
            color (str): Hex color code (e.g., "#FF0000") or palette role name.
        """
        from app.theme_manager.icon.svg_loader import SVGLoader

        self._custom_color = color

        # determine the size to use
        size = self._custom_size if self._custom_size else self.app_icon.spec.size.value

        # get the actual color value if it's a palette role
        actual_color = color
        if not color.startswith("#"):
            # assume it's a palette role, get it from the current palette
            palette = IconLoader.get_palette()
            actual_color = palette.get(color, "#000000")

        pixmap = SVGLoader.load(
            file_path=self.app_icon.spec.name.path,
            color=actual_color,
            size=size,
            as_icon=False
        )
        self.setPixmap(pixmap)

    def refresh_theme(self, palette: dict[str, str]):
        """Redraw icon using the current theme palette."""
        if self._custom_size or self._custom_color:
            # use direct SVG loading for custom size/color
            from app.theme_manager.icon.svg_loader import SVGLoader

            # determine size
            size = self._custom_size if self._custom_size else self.app_icon.spec.size.value

            # determine color
            if self._custom_color:
                if self._custom_color.startswith("#"):
                    color = self._custom_color
                else:
                    # it's a palette role, get updated color from new palette
                    color = palette.get(self._custom_color, "#000000")
            else:
                # use default color
                color = palette.get("icon_on_surface", "#000000")

            pixmap = SVGLoader.load(
                file_path=self.app_icon.spec.name.path,
                color=color,
                size=size,
                as_icon=False
            )
            self.setPixmap(pixmap)
        else:
            # use normal factory method with default color
            from app.theme_manager.icon.svg_loader import SVGLoader

            color = palette.get("icon_on_surface", "#000000")
            pixmap = SVGLoader.load(
                file_path=self.app_icon.spec.name.path,
                color=color,
                size=self.app_icon.spec.size.value,
                as_icon=False
            )
            self.setPixmap(pixmap)
