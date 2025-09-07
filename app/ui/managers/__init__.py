"""
UI Managers

Complex UI state management and coordination components that handle
multi-widget orchestration, application state, and workflow coordination.
"""

from .events import (
    ConnectionInfo, ConnectionScope, Debouncer, DebouncingOptions, DebouncingStrategy,
    EventCoordinator, EventFilter, EventPriority, EventRouter, SignalManager,
)
from .performance import (
    MetricsTracker, ObjectPool, PerformanceManager, ProgressiveRenderer,
)
from .tab_manager import TabManager, TabOperation, TabState

__all__ = [
    "TabManager",
    "TabState", 
    "TabOperation",
    "PerformanceManager",
    "ObjectPool",
    "ProgressiveRenderer", 
    "MetricsTracker",
    "EventCoordinator",
    "Debouncer", 
    "DebouncingStrategy", 
    "DebouncingOptions",
    "SignalManager", 
    "ConnectionScope", 
    "ConnectionInfo",
    "EventRouter", 
    "EventPriority", 
    "EventFilter",
]