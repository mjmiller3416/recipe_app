# app/theme_manager/icon/__init__.py

"""Icons subpackage: Simplified theme-aware icon system."""
from app.appearance.icon.icon import Icon
from app.appearance.icon.loader import IconLoader
from app.appearance.icon.mixin import IconMixin
from app.appearance.icon.config import Name, State, Type
from app.appearance.icon.svg_loader import SVGLoader

__all__ = [
    "IconMixin",
    "Icon",
    "IconLoader",
    "SVGLoader",
    "Name",
    "State",
    "Type",
]
