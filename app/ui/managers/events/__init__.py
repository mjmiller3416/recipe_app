"""
Event Management System

Generic event coordination, debouncing, signal management, and routing
components for complex UI interactions in MealGenie.
"""

from .debouncer import Debouncer, DebouncingOptions, DebouncingStrategy
from .event_coordinator import EventCoordinator
from .event_router import EventFilter, EventPriority, EventRouter
from .signal_manager import ConnectionInfo, ConnectionScope, SignalManager

__all__ = [
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