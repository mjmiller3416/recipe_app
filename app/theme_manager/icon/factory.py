"""app/theme_manager/icon/factory.py

Module providing IconFactory for creating themed icons and pixmaps.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon, QPixmap

from .loader import IconLoader
from .svg_loader import SVGLoader
from app.theme_manager.icon.config import Name, State, IconSpec, Type

# ── Icon Factory ─────────────────────────────────────────────────────────────────────────────
class IconFactory:
    """Creates a themed QIcon or QPixmap from an SVG file with caching."""

    # class-level cache to store generated icons and pixmaps
    _cache: dict[tuple, QIcon | QPixmap] = {}

    def __init__(self, icon: Name):
        """
        Initializes a themed icon instance from an AppIcon enum member.
        Args:
            icon (AppIcon): The pre-configured icon enum.
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
            state (State): The state for which to resolve the color.
        """
        role = self.icon_type.state_map.get(state) or self.icon_type.state_map.get(State.DEFAULT)
        return self.palette.get(role, "#FF00FF")

    def _load_icon_or_pixmap(
            self,
            state: State = State.DEFAULT,
            as_icon: bool = True
    ) -> QIcon | QPixmap:
        """
        Internal helper to load a themed icon, utilizing a cache.
        Args:
            state (State): The state for which to load the icon or pixmap.
            as_icon (bool): If True, returns a QIcon; otherwise, returns a QPixmap.
        Returns:
            QIcon or QPixmap: The themed icon or pixmap for the specified state.
        """
        color = self.resolve_color(state)

        # create a unique key for the cache
        cache_key = (self.file_path, self.size.width(), self.size.height(), color, as_icon)

        # return from cache if available
        if cache_key in self._cache:
            return self._cache[cache_key]

        # otherwise, load, cache, and return the new icon/pixmap
        new_item = SVGLoader.load(
            file_path=self.file_path, #
            color=color,
            size=self.size, #
            as_icon=as_icon #
        )
        self._cache[cache_key] = new_item
        return new_item

    def icon_for_state(self, state: State = State.DEFAULT) -> QIcon:
        """
        Returns a themed QIcon for a specific state.
        Args:
            state (State): The state for which to get the icon.
        Returns:
            QIcon: The themed icon for the specified state.
        """
        return self._load_icon_or_pixmap(state, as_icon=True)

    def pixmap_for_state(self, state: State = State.DEFAULT) -> QPixmap:
        """
        Returns a themed QPixmap for a specific state.
        Args:
            state (State): The state for which to get the pixmap.
        Returns:
            QPixmap: The themed pixmap for the specified state.
        """
        return self._load_icon_or_pixmap(state, as_icon=False)

    def __repr__(self) -> str:
        return f"<IconFactory path='{self.file_path.name}' type='{self.icon_type.name}'>"

    @classmethod
    def clear_cache(cls):
        """Clears the icon cache. Useful for memory management if needed."""
        cls._cache.clear()
