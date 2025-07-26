# app/theme_manager/icon/__init__.py

"""Icons subpackage: Simplified theme-aware icon system."""
from app.theme_manager.icon.icon import Icon
from app.theme_manager.icon.loader import IconLoader
from app.theme_manager.icon.mixin import IconMixin
from app.theme_manager.icon.config import Name, State, Type
from app.theme_manager.icon.svg_loader import SVGLoader

__all__ = [
    "IconMixin",
    "Icon", 
    "IconLoader",
    "SVGLoader",
    "Name",
    "State",
    "Type",
]
