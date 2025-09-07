"""app/ui/managers/events/event_coordinator.py

Generic event coordination system for MealGenie views.
Combines debouncing, signal management, and event routing into
a unified coordinator for complex UI event handling patterns.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Union
from weakref import WeakKeyDictionary

from PySide6.QtCore import QObject, Signal

from _dev_tools import DebugLogger
from .debouncer import Debouncer, DebouncingOptions, DebouncingStrategy
from .event_router import EventFilter, EventPriority, EventRouter
from .signal_manager import ConnectionInfo, ConnectionScope, SignalManager

class EventCoordinator(QObject):
    """
    Unified event coordination system combining debouncing, signal management, and event routing.
    
    Provides a single interface for managing complex UI event patterns including:
    - Debounced user interactions (search, filtering, input validation)
    - Managed signal connections with automatic cleanup
    - Priority-based event routing with filtering
    - Coordinated multi-component event handling
    - Lifecycle-aware connection management
    
    Key Benefits:
    - Prevents excessive updates during rapid user interactions
    - Automatic memory leak prevention through managed connections
    - Flexible event routing for complex UI workflows
    - Centralized event handling configuration
    - Performance monitoring and debugging capabilities
    
    Usage:
        class RecipeBrowserView(ScrollableNavView):
            def __init__(self):
                super().__init__()
                
                # Initialize event coordinator
                self.event_coordinator = EventCoordinator(self)
                
                # Setup debounced filtering
                self.event_coordinator.setup_debounced_handler(
                    "filter_update",
                    self._apply_filters,
                    delay_ms=300,
                    strategy=DebouncingStrategy.TRAILING
                )
                
                # Setup managed signal connections
                self.event_coordinator.connect_signals([
                    {
                        'sender': self.search_input,
                        'signal_name': 'textChanged',
                        'receiver': self,
                        'slot': lambda text: self.event_coordinator.trigger_debounced("filter_update", {"search": text})
                    }
                ])
                
                # Setup event routing
                self.event_coordinator.register_event_route(
                    "recipe_selection",
                    self._handle_recipe_selection,
                    EventPriority.HIGH
                )
    """
    
    # Coordination signals
    coordination_started = Signal(str)              # coordinator_name
    debounced_action_triggered = Signal(str, int)   # action_name, delay_ms
    event_coordination_complete = Signal(str, int)  # event_name, total_handlers
    coordinator_cleanup_complete = Signal()
    
    def __init__(self, 
                 parent: QObject = None,
                 coordinator_name: str = "EventCoordinator"):
        """
        Initialize the event coordinator.
        
        Args:
            parent: Parent object for Qt memory management
            coordinator_name: Name for debugging and logging
        """
        super().__init__(parent)
        self.coordinator_name = coordinator_name
        
        # Initialize component managers
        self.debouncer = Debouncer(self)
        self.signal_manager = SignalManager(self)
        self.event_router = EventRouter(self)
        
        # Coordination state
        self._active_coordinations: Dict[str, Dict[str, Any]] = {}
        self._coordination_chains: Dict[str, List[str]] = {}
        
        # Performance tracking
        self._coordination_metrics: Dict[str, Dict[str, Any]] = {}
        
        self.coordination_started.emit(self.coordinator_name)
        
        DebugLogger.log(f"EventCoordinator '{coordinator_name}' initialized", "debug")
    
    # ── Debounced Event Handling ────────────────────────────────────────────────────────────────────────────────
    
    def setup_debounced_handler(self,
                               action_name: str,
                               handler: Callable,
                               delay_ms: int = 250,
                               strategy: DebouncingStrategy = DebouncingStrategy.TRAILING,
                               max_wait_ms: Optional[int] = None) -> str:
        """
        Setup a debounced event handler.
        
        Args:
            action_name: Unique name for the debounced action
            handler: Function to execute when debounced
            delay_ms: Debounce delay in milliseconds
            strategy: Debouncing strategy
            max_wait_ms: Maximum wait time before forcing execution
            
        Returns:
            str: Action identifier for later reference
        """
        options = DebouncingOptions(
            delay_ms=delay_ms,
            strategy=strategy,
            max_wait_ms=max_wait_ms
        )
        
        debounced_func = self.debouncer.debounce(handler, options, action_name)
        
        DebugLogger.log(
            f"Setup debounced handler: {action_name} "
            f"(delay: {delay_ms}ms, strategy: {strategy.value})",
            "debug"
        )
        
        return action_name
    
    def trigger_debounced(self, action_name: str, *args, **kwargs) -> Any:
        """
        Trigger a debounced action.
        
        Args:
            action_name: Name of the registered debounced action
            *args, **kwargs: Arguments to pass to the handler
            
        Returns:
            Result from debounced function (if executed immediately)
        """
        debounced_func = self.debouncer.get_debounced_function(action_name)
        if debounced_func:
            self.debounced_action_triggered.emit(action_name, debounced_func.options.delay_ms)
            return debounced_func(*args, **kwargs)
        else:
            DebugLogger.log(f"Debounced action '{action_name}' not found", "warning")
            return None
    
    def cancel_debounced(self, action_name: str) -> bool:
        """Cancel a pending debounced action."""
        return self.debouncer.cancel_function(action_name)
    
    def flush_debounced(self, action_name: str) -> Any:
        """Force immediate execution of a debounced action."""
        return self.debouncer.flush_function(action_name)
    
    # ── Signal Connection Management ────────────────────────────────────────────────────────────────────────────
    
    def connect_signal(self,
                      sender: QObject,
                      signal_name: str,
                      receiver: QObject,
                      slot: Callable,
                      scope: ConnectionScope = ConnectionScope.VIEW_LIFECYCLE,
                      connection_id: Optional[str] = None) -> str:
        """
        Create a managed signal connection.
        
        Args:
            sender: Object emitting the signal
            signal_name: Name of the signal
            receiver: Object receiving the signal
            slot: Slot function to connect
            scope: Connection lifecycle scope
            connection_id: Optional custom connection identifier
            
        Returns:
            str: Connection ID for later reference
        """
        return self.signal_manager.connect(
            sender, signal_name, receiver, slot, scope, connection_id
        )
    
    def connect_signals(self, connection_specs: List[Dict[str, Any]]) -> List[str]:
        """
        Create multiple managed signal connections in batch.
        
        Args:
            connection_specs: List of connection specification dictionaries
            
        Returns:
            List[str]: List of connection IDs
        """
        return self.signal_manager.bulk_connect(connection_specs)
    
    def disconnect_signal(self, connection_id: str) -> bool:
        """Disconnect a managed signal connection."""
        return self.signal_manager.disconnect(connection_id)
    
    def disconnect_signals_by_scope(self, scope: ConnectionScope) -> int:
        """Disconnect all connections in a specific scope."""
        return self.signal_manager.disconnect_by_scope(scope)
    
    # ── Event Routing ───────────────────────────────────────────────────────────────────────────────────────────
    
    def register_event_route(self,
                            route_name: str,
                            handler: Callable[[Dict[str, Any]], Any],
                            priority: EventPriority = EventPriority.NORMAL,
                            filters: Optional[List[EventFilter]] = None,
                            description: str = "",
                            group: Optional[str] = None) -> bool:
        """
        Register an event route.
        
        Args:
            route_name: Unique route name
            handler: Function to handle the event
            priority: Route execution priority
            filters: Optional list of event filters
            description: Route description
            group: Optional group name for bulk operations
            
        Returns:
            bool: True if route was registered successfully
        """
        return self.event_router.register_route(
            route_name, handler, priority, filters, description, group
        )
    
    def route_event(self, event_name: str, event_data: Optional[Dict[str, Any]] = None) -> List[Any]:
        """
        Route an event to all matching handlers.
        
        Args:
            event_name: Name/type of the event
            event_data: Event data to pass to handlers
            
        Returns:
            List[Any]: Results from executed route handlers
        """
        if event_data is None:
            event_data = {}
        
        results = self.event_router.route_event(event_name, event_data)
        
        self.event_coordination_complete.emit(event_name, len(results))
        
        return results
    
    def enable_route(self, route_name: str) -> bool:
        """Enable a specific event route."""
        return self.event_router.enable_route(route_name)
    
    def disable_route(self, route_name: str) -> bool:
        """Disable a specific event route."""
        return self.event_router.disable_route(route_name)
    
    # ── Coordination Patterns ──────────────────────────────────────────────────────────────────────────────────
    
    def setup_search_coordination(self,
                                 search_input: QObject,
                                 search_handler: Callable[[str], Any],
                                 delay_ms: int = 300,
                                 min_length: int = 2) -> str:
        """
        Setup coordinated search functionality with debouncing and validation.
        
        Args:
            search_input: Search input widget
            search_handler: Function to handle search execution
            delay_ms: Debounce delay for search input
            min_length: Minimum search term length
            
        Returns:
            str: Coordination identifier
        """
        coordination_id = f"search_coordination_{id(search_input)}"
        
        # Create search validation filter
        search_filter = EventFilter(
            "min_length_filter",
            lambda data: len(data.get('search_term', '').strip()) >= min_length,
            f"Search term must be at least {min_length} characters"
        )
        
        # Setup debounced search handler
        def debounced_search_wrapper(search_term: str):
            return self.route_event("search_execution", {
                "search_term": search_term,
                "coordination_id": coordination_id
            })
        
        self.setup_debounced_handler(
            f"search_{coordination_id}",
            debounced_search_wrapper,
            delay_ms=delay_ms
        )
        
        # Register search route with validation
        self.register_event_route(
            "search_execution",
            lambda data: search_handler(data.get('search_term', '')),
            EventPriority.HIGH,
            filters=[search_filter],
            description="Coordinated search execution",
            group="search_coordination"
        )
        
        # Connect search input to debounced handler
        self.connect_signal(
            search_input,
            "textChanged",
            self,
            lambda text: self.trigger_debounced(f"search_{coordination_id}", text),
            ConnectionScope.VIEW_LIFECYCLE
        )
        
        self._active_coordinations[coordination_id] = {
            'type': 'search',
            'search_input': search_input,
            'handler': search_handler,
            'delay_ms': delay_ms,
            'min_length': min_length
        }
        
        DebugLogger.log(f"Setup search coordination: {coordination_id}", "debug")
        return coordination_id
    
    def setup_filter_coordination(self,
                                 filter_controls: Dict[str, QObject],
                                 filter_handler: Callable[[Dict[str, Any]], Any],
                                 delay_ms: int = 250,
                                 batch_updates: bool = True) -> str:
        """
        Setup coordinated filtering with multiple controls and debouncing.
        
        Args:
            filter_controls: Dictionary of control_name -> widget mappings
            filter_handler: Function to handle filter updates
            delay_ms: Debounce delay for filter updates
            batch_updates: Whether to batch multiple rapid filter changes
            
        Returns:
            str: Coordination identifier
        """
        coordination_id = f"filter_coordination_{hash(tuple(filter_controls.keys()))}"
        
        # Setup debounced filter handler
        def debounced_filter_wrapper(**filter_data):
            return self.route_event("filter_execution", {
                "filters": filter_data,
                "coordination_id": coordination_id
            })
        
        self.setup_debounced_handler(
            f"filter_{coordination_id}",
            debounced_filter_wrapper,
            delay_ms=delay_ms,
            strategy=DebouncingStrategy.TRAILING
        )
        
        # Register filter route
        self.register_event_route(
            "filter_execution",
            lambda data: filter_handler(data.get('filters', {})),
            EventPriority.NORMAL,
            description="Coordinated filter execution",
            group="filter_coordination"
        )
        
        # Connect all filter controls
        connection_specs = []
        for control_name, control_widget in filter_controls.items():
            # Determine appropriate signal based on widget type
            signal_name = self._get_appropriate_signal(control_widget)
            
            if signal_name:
                connection_specs.append({
                    'sender': control_widget,
                    'signal_name': signal_name,
                    'receiver': self,
                    'slot': lambda value, name=control_name: self._handle_filter_change(coordination_id, name, value),
                    'scope': ConnectionScope.VIEW_LIFECYCLE
                })
        
        self.connect_signals(connection_specs)
        
        self._active_coordinations[coordination_id] = {
            'type': 'filter',
            'controls': filter_controls,
            'handler': filter_handler,
            'delay_ms': delay_ms,
            'batch_updates': batch_updates,
            'pending_changes': {}
        }
        
        DebugLogger.log(f"Setup filter coordination: {coordination_id}", "debug")
        return coordination_id
    
    def setup_validation_coordination(self,
                                     form_fields: Dict[str, QObject],
                                     validation_handler: Callable[[Dict[str, Any]], Dict[str, str]],
                                     delay_ms: int = 500) -> str:
        """
        Setup coordinated form validation with debounced validation.
        
        Args:
            form_fields: Dictionary of field_name -> widget mappings
            validation_handler: Function that returns validation errors
            delay_ms: Debounce delay for validation
            
        Returns:
            str: Coordination identifier
        """
        coordination_id = f"validation_coordination_{hash(tuple(form_fields.keys()))}"
        
        # Setup debounced validation handler
        def debounced_validation_wrapper(**field_data):
            validation_errors = validation_handler(field_data)
            return self.route_event("validation_result", {
                "field_data": field_data,
                "validation_errors": validation_errors,
                "coordination_id": coordination_id
            })
        
        self.setup_debounced_handler(
            f"validation_{coordination_id}",
            debounced_validation_wrapper,
            delay_ms=delay_ms
        )
        
        # Register validation result route
        self.register_event_route(
            "validation_result",
            lambda data: self._handle_validation_results(coordination_id, data),
            EventPriority.HIGH,
            description="Coordinated validation result processing",
            group="validation_coordination"
        )
        
        # Connect form field changes
        connection_specs = []
        for field_name, field_widget in form_fields.items():
            signal_name = self._get_appropriate_signal(field_widget)
            
            if signal_name:
                connection_specs.append({
                    'sender': field_widget,
                    'signal_name': signal_name,
                    'receiver': self,
                    'slot': lambda value, name=field_name: self._handle_field_change(coordination_id, name, value),
                    'scope': ConnectionScope.VIEW_LIFECYCLE
                })
        
        self.connect_signals(connection_specs)
        
        self._active_coordinations[coordination_id] = {
            'type': 'validation',
            'fields': form_fields,
            'handler': validation_handler,
            'delay_ms': delay_ms,
            'pending_field_data': {}
        }
        
        DebugLogger.log(f"Setup validation coordination: {coordination_id}", "debug")
        return coordination_id
    
    # ── Coordination Management ────────────────────────────────────────────────────────────────────────────────
    
    def get_coordination_info(self, coordination_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific coordination."""
        return self._active_coordinations.get(coordination_id)
    
    def remove_coordination(self, coordination_id: str) -> bool:
        """
        Remove a coordination and clean up its resources.
        
        Args:
            coordination_id: ID of coordination to remove
            
        Returns:
            bool: True if coordination was found and removed
        """
        coordination_info = self._active_coordinations.get(coordination_id)
        if not coordination_info:
            return False
        
        try:
            # Cancel any pending debounced actions
            coordination_type = coordination_info['type']
            self.cancel_debounced(f"{coordination_type}_{coordination_id}")
            
            # Clean up coordination-specific resources
            if coordination_type == 'filter':
                coordination_info['pending_changes'].clear()
            elif coordination_type == 'validation':
                coordination_info['pending_field_data'].clear()
            
            # Remove from active coordinations
            del self._active_coordinations[coordination_id]
            
            DebugLogger.log(f"Removed coordination: {coordination_id}", "debug")
            return True
            
        except Exception as e:
            DebugLogger.log(f"Error removing coordination '{coordination_id}': {e}", "error")
            return False
    
    def cleanup_all_coordinations(self) -> int:
        """
        Clean up all active coordinations.
        
        Returns:
            int: Number of coordinations cleaned up
        """
        coordination_ids = list(self._active_coordinations.keys())
        cleaned_count = 0
        
        for coordination_id in coordination_ids:
            if self.remove_coordination(coordination_id):
                cleaned_count += 1
        
        # Clean up component managers
        self.debouncer.cancel_all()
        self.signal_manager.cleanup_view_connections()
        
        self.coordinator_cleanup_complete.emit()
        
        DebugLogger.log(f"Cleaned up {cleaned_count} coordinations", "debug")
        return cleaned_count
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics from all components."""
        return {
            'coordinator_name': self.coordinator_name,
            'active_coordinations': len(self._active_coordinations),
            'debouncer_metrics': {
                'active_functions': self.debouncer.get_active_count(),
                'registered_functions': self.debouncer.get_registry_info()
            },
            'signal_manager_metrics': {
                'total_connections': self.signal_manager.get_active_connection_count(),
                'scope_statistics': self.signal_manager.get_scope_statistics()
            },
            'event_router_metrics': self.event_router.get_routing_statistics(),
            'coordination_types': {
                coord_type: sum(1 for coord in self._active_coordinations.values() 
                               if coord['type'] == coord_type)
                for coord_type in ['search', 'filter', 'validation']
            }
        }
    
    # ── Internal Helper Methods ─────────────────────────────────────────────────────────────────────────────────
    
    def _get_appropriate_signal(self, widget: QObject) -> Optional[str]:
        """Determine the appropriate signal name for a widget type."""
        widget_class_name = widget.__class__.__name__
        
        signal_mapping = {
            'QLineEdit': 'textChanged',
            'QTextEdit': 'textChanged',
            'QPlainTextEdit': 'textChanged',
            'QComboBox': 'currentTextChanged',
            'QCheckBox': 'stateChanged',
            'QRadioButton': 'toggled',
            'QSpinBox': 'valueChanged',
            'QDoubleSpinBox': 'valueChanged',
            'QSlider': 'valueChanged',
            'ComboBox': 'currentTextChanged',  # Custom MealGenie ComboBox
        }
        
        return signal_mapping.get(widget_class_name)
    
    def _handle_filter_change(self, coordination_id: str, filter_name: str, value: Any) -> None:
        """Handle individual filter control changes."""
        coordination_info = self._active_coordinations.get(coordination_id)
        if not coordination_info or coordination_info['type'] != 'filter':
            return
        
        # Store pending change
        coordination_info['pending_changes'][filter_name] = value
        
        # Trigger debounced filter update with all pending changes
        self.trigger_debounced(
            f"filter_{coordination_id}",
            **coordination_info['pending_changes']
        )
    
    def _handle_field_change(self, coordination_id: str, field_name: str, value: Any) -> None:
        """Handle individual form field changes."""
        coordination_info = self._active_coordinations.get(coordination_id)
        if not coordination_info or coordination_info['type'] != 'validation':
            return
        
        # Store pending field data
        coordination_info['pending_field_data'][field_name] = value
        
        # Trigger debounced validation with all pending data
        self.trigger_debounced(
            f"validation_{coordination_id}",
            **coordination_info['pending_field_data']
        )
    
    def _handle_validation_results(self, coordination_id: str, data: Dict[str, Any]) -> None:
        """Handle validation results and emit appropriate signals."""
        validation_errors = data.get('validation_errors', {})
        
        # Here you would typically emit signals to update UI with validation results
        # This is a placeholder for the actual validation result handling
        if validation_errors:
            DebugLogger.log(f"Validation errors in {coordination_id}: {validation_errors}", "debug")
        else:
            DebugLogger.log(f"Validation passed for {coordination_id}", "debug")