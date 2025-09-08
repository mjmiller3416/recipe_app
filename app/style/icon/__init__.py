# app/theme_manager/icon/__init__.py

"""Icons subpackage: Simplified theme-aware icon system."""
from app.style.icon.config import Icon, Name, State, Type
from app.style.icon.icon import AppIcon
from app.style.icon.loader import IconLoader
from app.style.icon.svg_loader import SVGLoader


__all__ = [
    "AppIcon",
    "IconLoader",
    "SVGLoader",
    "Name",
    "State",
    "Type",
    "Icon",  # Alias for Name enum
]
