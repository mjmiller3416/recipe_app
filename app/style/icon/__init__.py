# app/theme_manager/icon/__init__.py

"""Icons subpackage: Simplified theme-aware icon system."""
from app.style.icon.icon import Icon
from app.style.icon.loader import IconLoader
from app.style.icon.mixin import IconMixin
from app.style.icon.config import Name, State, Type
from app.style.icon.svg_loader import SVGLoader

__all__ = [
    "IconMixin",
    "Icon",
    "IconLoader",
    "SVGLoader",
    "Name",
    "State",
    "Type",
]
