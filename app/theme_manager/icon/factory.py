"""app/theme_manager/icon/factory.py

Module providing IconFactory for generating themed icons.

IconFactory creates theme-aware QIcons and QPixmaps from SVG files by
applying color variants based on the current theme.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon, QPixmap

from .loader import IconLoader
from .svg_loader import SVGLoader
from app.theme_manager.icon.config import IconSpec, AppIcon, State, Type

# ── Themed Icon ──────────────────────────────────────────────────────────────────────────────
class IconFactory:
    """Creates a themed QIcon or QPixmap from an SVG file."""

    def __init__(self, icon: AppIcon):
        """
        Initializes a themed icon instance from an AppIcon enum member.

        Args:
            icon (AppIcon): The pre-configured icon enum member.
        """
        spec: IconSpec = icon.spec
        self.file_path: Path = spec.name.path
        self.size: QSize = spec.size.value
        self.icon_type: Type = spec.type
        self.palette: dict[str, str] = IconLoader.get_palette()

    def resolve_color(self, state: State = State.DEFAULT) -> str:
        """
        Resolves a hex color for the given state from the current palette.

        Args:
            state (State): State enum like State.HOVER, State.CHECKED, etc.

        Returns:
            str: Hex color string (e.g., "#65d3ff")
        """
        role = self.icon_type.state_map.get(state) or self.icon_type.state_map.get(State.DEFAULT)
        return self.palette.get(role, "#FF00FF")

    def _load_icon_or_pixmap(self, state: State = State.DEFAULT, as_icon: bool = True) -> QIcon | QPixmap:
        """
        Internal helper to load a themed QIcon or QPixmap for a given state.

        Args:
            state (State): State enum like State.HOVER, State.CHECKED, etc.
            as_icon (bool): Whether to return a QIcon or QPixmap

        Returns:
            QIcon | QPixmap: Themed icon
        """
        return SVGLoader.load(
            file_path=self.file_path,
            color=self.resolve_color(state),
            size=self.size,
            as_icon=as_icon
        )

    def icon_for_state(self, state: State = State.DEFAULT) -> QIcon:
        """Returns a themed QIcon for a specific state."""
        return self._load_icon_or_pixmap(state, as_icon=True)

    def icon(self) -> QIcon:
        """Returns the default themed QIcon."""
        return self._load_icon_or_pixmap(State.DEFAULT, as_icon=True)

    def pixmap(self) -> QPixmap:
        """Returns the default themed QPixmap."""
        return self._load_icon_or_pixmap(State.DEFAULT, as_icon=False)

    def __repr__(self) -> str:
        return f"<ThemedIcon path='{self.file_path.name}' type='{self.icon_type.name}'>"
