"""
UI Managers

Complex UI state management and coordination components that handle
multi-widget orchestration, application state, and workflow coordination.
"""

from .tab_manager import TabManager, TabOperation, TabState

__all__ = [
    "TabManager",
    "TabState", 
    "TabOperation",
]