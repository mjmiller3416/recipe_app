"""app/ui/managers/events/event_router.py

Event routing system for complex UI interactions in MealGenie.
Provides priority-based event routing, filtering, and conditional
execution for coordinated multi-component event handling.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from weakref import WeakKeyDictionary

from PySide6.QtCore import QObject, Signal

from _dev_tools import DebugLogger

class EventPriority(Enum):
    """Event routing priority levels."""
    CRITICAL = 0    # System-critical events (errors, shutdowns)
    HIGH = 10       # Important UI updates (navigation, user feedback)
    NORMAL = 50     # Standard user interactions
    LOW = 100       # Background operations, logging
    DEFERRED = 200  # Non-essential operations


@dataclass
class EventFilter:
    """Configurable event filter."""
    name: str
    condition: Callable[[Dict[str, Any]], bool]
    description: str = ""
    active: bool = True
    
    def matches(self, event_data: Dict[str, Any]) -> bool:
        """Check if event matches this filter."""
        if not self.active:
            return True
        
        try:
            return self.condition(event_data)
        except Exception as e:
            DebugLogger.log(f"Error in event filter '{self.name}': {e}", "error")
            return False


@dataclass
class EventRoute:
    """Event route configuration."""
    name: str
    handler: Callable[[Dict[str, Any]], Any]
    priority: EventPriority = EventPriority.NORMAL
    filters: List[EventFilter] = field(default_factory=list)
    enabled: bool = True
    description: str = ""
    execution_count: int = field(default=0, init=False)
    last_execution_time: Optional[float] = field(default=None, init=False)
    
    def should_handle(self, event_data: Dict[str, Any]) -> bool:
        """Check if this route should handle the event."""
        if not self.enabled:
            return False
        
        # Check all filters
        for event_filter in self.filters:
            if not event_filter.matches(event_data):
                return False
        
        return True
    
    def execute(self, event_data: Dict[str, Any]) -> Any:
        """Execute the route handler."""
        try:
            self.execution_count += 1
            self.last_execution_time = self._get_current_time_ms()
            return self.handler(event_data)
        except Exception as e:
            DebugLogger.log(f"Error executing route '{self.name}': {e}", "error")
            raise
    
    def _get_current_time_ms(self) -> float:
        """Get current time in milliseconds."""
        from time import perf_counter
        return perf_counter() * 1000


class EventRouter(QObject):
    """
    Priority-based event router for complex UI interactions.
    
    Manages event routing with:
    - Priority-based execution order
    - Configurable event filtering
    - Conditional route execution
    - Performance monitoring
    - Route lifecycle management
    
    Usage:
        class MyView(QWidget):
            def __init__(self):
                super().__init__()
                self.event_router = EventRouter(self)
                
                # Register routes
                self.event_router.register_route(
                    "filter_update",
                    self._handle_filter_update,
                    EventPriority.HIGH,
                    filters=[
                        EventFilter("has_search_term", lambda data: "search_term" in data)
                    ]
                )
                
                # Route events
                self.event_router.route_event("filter_update", {
                    "search_term": "recipe",
                    "category": "main_dish"
                })
    """
    
    # Signals for monitoring routing activity
    event_routed = Signal(str, int)          # event_name, routes_executed
    route_executed = Signal(str, float)      # route_name, execution_time_ms
    route_failed = Signal(str, str)          # route_name, error_message
    filter_rejected = Signal(str, str)       # route_name, filter_name
    
    def __init__(self, parent: QObject = None):
        """
        Initialize the event router.
        
        Args:
            parent: Parent object for Qt memory management
        """
        super().__init__(parent)
        
        # Route registry organized by priority
        self._routes_by_priority: Dict[EventPriority, List[EventRoute]] = {
            priority: [] for priority in EventPriority
        }
        
        # Route lookup by name
        self._routes_by_name: Dict[str, EventRoute] = {}
        
        # Global filters applied to all events
        self._global_filters: List[EventFilter] = []
        
        # Event routing statistics
        self._routing_stats: Dict[str, Dict[str, Any]] = {}
        
        # Route groups for bulk operations
        self._route_groups: Dict[str, Set[str]] = {}
        
        DebugLogger.log("EventRouter initialized", "debug")
    
    def register_route(self,
                      name: str,
                      handler: Callable[[Dict[str, Any]], Any],
                      priority: EventPriority = EventPriority.NORMAL,
                      filters: Optional[List[EventFilter]] = None,
                      description: str = "",
                      group: Optional[str] = None) -> bool:
        """
        Register an event route.
        
        Args:
            name: Unique route name
            handler: Function to handle the event
            priority: Route execution priority
            filters: Optional list of event filters
            description: Route description for debugging
            group: Optional group name for bulk operations
            
        Returns:
            bool: True if route was registered successfully
        """
        if name in self._routes_by_name:
            DebugLogger.log(f"Route '{name}' already exists, skipping registration", "warning")
            return False
        
        try:
            route = EventRoute(
                name=name,
                handler=handler,
                priority=priority,
                filters=filters or [],
                description=description
            )
            
            # Store in priority-ordered list
            self._routes_by_priority[priority].append(route)
            
            # Store in name lookup
            self._routes_by_name[name] = route
            
            # Add to group if specified
            if group:
                if group not in self._route_groups:
                    self._route_groups[group] = set()
                self._route_groups[group].add(name)
            
            DebugLogger.log(
                f"Registered route: {name} (priority: {priority.name}, "
                f"filters: {len(route.filters)})",
                "debug"
            )
            
            return True
            
        except Exception as e:
            DebugLogger.log(f"Error registering route '{name}': {e}", "error")
            return False
    
    def unregister_route(self, name: str) -> bool:
        """
        Unregister an event route.
        
        Args:
            name: Route name to unregister
            
        Returns:
            bool: True if route was found and unregistered
        """
        route = self._routes_by_name.get(name)
        if not route:
            return False
        
        try:
            # Remove from priority list
            self._routes_by_priority[route.priority].remove(route)
            
            # Remove from name lookup
            del self._routes_by_name[name]
            
            # Remove from groups
            for group_routes in self._route_groups.values():
                group_routes.discard(name)
            
            DebugLogger.log(f"Unregistered route: {name}", "debug")
            return True
            
        except Exception as e:
            DebugLogger.log(f"Error unregistering route '{name}': {e}", "error")
            return False
    
    def route_event(self, event_name: str, event_data: Dict[str, Any]) -> List[Any]:
        """
        Route an event to all matching handlers in priority order.
        
        Args:
            event_name: Name/type of the event
            event_data: Event data to pass to handlers
            
        Returns:
            List[Any]: Results from executed route handlers
        """
        start_time = self._get_current_time_ms()
        results = []
        routes_executed = 0
        
        try:
            # Add event metadata
            enriched_data = {
                **event_data,
                '_event_name': event_name,
                '_event_timestamp': start_time
            }
            
            # Check global filters first
            if not self._check_global_filters(enriched_data):
                DebugLogger.log(f"Event '{event_name}' rejected by global filters", "debug")
                return results
            
            # Execute routes in priority order
            for priority in sorted(EventPriority, key=lambda p: p.value):
                priority_routes = self._routes_by_priority[priority]
                
                for route in priority_routes:
                    if route.should_handle(enriched_data):
                        try:
                            route_start = self._get_current_time_ms()
                            result = route.execute(enriched_data)
                            route_end = self._get_current_time_ms()
                            
                            results.append(result)
                            routes_executed += 1
                            
                            # Emit performance signal
                            self.route_executed.emit(route.name, route_end - route_start)
                            
                        except Exception as e:
                            error_msg = f"Route execution failed: {e}"
                            self.route_failed.emit(route.name, error_msg)
                            DebugLogger.log(f"Route '{route.name}' failed: {e}", "error")
                    else:
                        # Log filter rejection
                        for event_filter in route.filters:
                            if not event_filter.matches(enriched_data):
                                self.filter_rejected.emit(route.name, event_filter.name)
                                break
            
            # Update statistics
            self._update_routing_stats(event_name, routes_executed, start_time)
            
            # Emit routing completion signal
            self.event_routed.emit(event_name, routes_executed)
            
            end_time = self._get_current_time_ms()
            DebugLogger.log(
                f"Routed event '{event_name}': {routes_executed} routes executed "
                f"in {end_time - start_time:.2f}ms",
                "debug"
            )
            
            return results
            
        except Exception as e:
            DebugLogger.log(f"Error routing event '{event_name}': {e}", "error")
            return results
    
    def add_global_filter(self, event_filter: EventFilter) -> None:
        """
        Add a global filter that applies to all events.
        
        Args:
            event_filter: Filter to add globally
        """
        self._global_filters.append(event_filter)
        DebugLogger.log(f"Added global filter: {event_filter.name}", "debug")
    
    def remove_global_filter(self, filter_name: str) -> bool:
        """
        Remove a global filter by name.
        
        Args:
            filter_name: Name of filter to remove
            
        Returns:
            bool: True if filter was found and removed
        """
        for i, event_filter in enumerate(self._global_filters):
            if event_filter.name == filter_name:
                self._global_filters.pop(i)
                DebugLogger.log(f"Removed global filter: {filter_name}", "debug")
                return True
        return False
    
    def enable_route(self, name: str) -> bool:
        """Enable a specific route."""
        route = self._routes_by_name.get(name)
        if route:
            route.enabled = True
            DebugLogger.log(f"Enabled route: {name}", "debug")
            return True
        return False
    
    def disable_route(self, name: str) -> bool:
        """Disable a specific route."""
        route = self._routes_by_name.get(name)
        if route:
            route.enabled = False
            DebugLogger.log(f"Disabled route: {name}", "debug")
            return True
        return False
    
    def enable_group(self, group_name: str) -> int:
        """
        Enable all routes in a group.
        
        Args:
            group_name: Name of the route group
            
        Returns:
            int: Number of routes enabled
        """
        route_names = self._route_groups.get(group_name, set())
        enabled_count = 0
        
        for route_name in route_names:
            if self.enable_route(route_name):
                enabled_count += 1
        
        DebugLogger.log(f"Enabled {enabled_count} routes in group: {group_name}", "debug")
        return enabled_count
    
    def disable_group(self, group_name: str) -> int:
        """
        Disable all routes in a group.
        
        Args:
            group_name: Name of the route group
            
        Returns:
            int: Number of routes disabled
        """
        route_names = self._route_groups.get(group_name, set())
        disabled_count = 0
        
        for route_name in route_names:
            if self.disable_route(route_name):
                disabled_count += 1
        
        DebugLogger.log(f"Disabled {disabled_count} routes in group: {group_name}", "debug")
        return disabled_count
    
    def get_route(self, name: str) -> Optional[EventRoute]:
        """Get route by name."""
        return self._routes_by_name.get(name)
    
    def get_routes_by_priority(self, priority: EventPriority) -> List[EventRoute]:
        """Get all routes with a specific priority."""
        return self._routes_by_priority[priority].copy()
    
    def get_group_routes(self, group_name: str) -> List[EventRoute]:
        """Get all routes in a specific group."""
        route_names = self._route_groups.get(group_name, set())
        return [self._routes_by_name[name] for name in route_names if name in self._routes_by_name]
    
    def get_route_count(self) -> int:
        """Get total number of registered routes."""
        return len(self._routes_by_name)
    
    def get_enabled_route_count(self) -> int:
        """Get number of enabled routes."""
        return sum(1 for route in self._routes_by_name.values() if route.enabled)
    
    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get comprehensive routing statistics."""
        stats = {
            'total_routes': len(self._routes_by_name),
            'enabled_routes': self.get_enabled_route_count(),
            'priority_distribution': {},
            'global_filters': len(self._global_filters),
            'route_groups': len(self._route_groups),
            'event_statistics': self._routing_stats.copy()
        }
        
        # Priority distribution
        for priority in EventPriority:
            stats['priority_distribution'][priority.name] = len(self._routes_by_priority[priority])
        
        return stats
    
    def clear_all_routes(self) -> int:
        """
        Clear all registered routes.
        
        Returns:
            int: Number of routes cleared
        """
        route_count = len(self._routes_by_name)
        
        # Clear all data structures
        for priority_list in self._routes_by_priority.values():
            priority_list.clear()
        
        self._routes_by_name.clear()
        self._route_groups.clear()
        
        DebugLogger.log(f"Cleared {route_count} routes", "debug")
        return route_count
    
    def _check_global_filters(self, event_data: Dict[str, Any]) -> bool:
        """Check if event passes all global filters."""
        for event_filter in self._global_filters:
            if not event_filter.matches(event_data):
                return False
        return True
    
    def _update_routing_stats(self, event_name: str, routes_executed: int, start_time: float) -> None:
        """Update routing statistics for an event."""
        if event_name not in self._routing_stats:
            self._routing_stats[event_name] = {
                'total_executions': 0,
                'total_routes_executed': 0,
                'average_routes_per_event': 0,
                'last_execution_time': 0
            }
        
        stats = self._routing_stats[event_name]
        stats['total_executions'] += 1
        stats['total_routes_executed'] += routes_executed
        stats['average_routes_per_event'] = stats['total_routes_executed'] / stats['total_executions']
        stats['last_execution_time'] = start_time
    
    def _get_current_time_ms(self) -> float:
        """Get current time in milliseconds."""
        from time import perf_counter
        return perf_counter() * 1000


# ── Utility Functions ───────────────────────────────────────────────────────────────────────────────────────────

def create_basic_filters() -> Dict[str, EventFilter]:
    """Create a set of commonly used event filters."""
    return {
        'has_data': EventFilter(
            'has_data',
            lambda data: bool(data and len(data) > 1),  # More than just metadata
            'Filter events that have actual data'
        ),
        'has_search_term': EventFilter(
            'has_search_term',
            lambda data: 'search_term' in data and bool(data['search_term'].strip()),
            'Filter events with non-empty search term'
        ),
        'has_category': EventFilter(
            'has_category',
            lambda data: 'category' in data and bool(data['category']),
            'Filter events with category information'
        ),
        'during_business_hours': EventFilter(
            'during_business_hours',
            lambda data: 9 <= self._get_current_hour() <= 17,
            'Filter events during business hours (9 AM - 5 PM)'
        )
    }


def _get_current_hour() -> int:
    """Get current hour for time-based filtering."""
    from datetime import datetime
    return datetime.now().hour