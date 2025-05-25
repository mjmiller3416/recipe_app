"""style_manager/__init__.py

Central theme management system for the recipe application.
"""

from .loaders.theme_loader import ThemeLoader
from .loaders.icon_loader import IconLoader
from .loaders.widget_loader import WidgetLoader

__all__ = [
    "ThemeLoader",
    "IconLoader",
    "WidgetLoader",
]