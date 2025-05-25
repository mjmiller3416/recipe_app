"""
config/paths/__init__.py

Provides centralized access to application paths and stylesheet mappings.
"""

from .app_paths import AppPaths
from .qss_paths import QssPaths

__all__ = ["AppPaths", "QssPaths"]
