"""app/ui/managers/events/signal_manager.py

Signal connection and lifecycle management for MealGenie views.
Provides automatic cleanup, connection tracking, and debugging utilities
to prevent memory leaks and manage complex signal/slot patterns.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from weakref import WeakKeyDictionary, WeakSet, ref

from PySide6.QtCore import QMetaObject, QObject, Signal

from _dev_tools import DebugLogger

class ConnectionScope(Enum):
    """Scope of signal connections for lifecycle management."""
    VIEW_LIFECYCLE = "view_lifecycle"      # Cleaned up when view is destroyed
    SESSION_LIFECYCLE = "session"          # Cleaned up on application session end
    PERMANENT = "permanent"                # Never automatically cleaned up
    TEMPORARY = "temporary"                # Cleaned up on explicit request


@dataclass
class ConnectionInfo:
    """Information about a signal connection."""
    sender: QObject
    signal_name: str
    receiver: QObject
    slot: Callable
    scope: ConnectionScope
    connection_id: str
    created_at: float
    meta_connection: Optional[QMetaObject.Connection] = None
    
    def __post_init__(self):
        """Generate connection ID if not provided."""
        if not self.connection_id:
            sender_name = getattr(self.sender, 'objectName', lambda: 'Unknown')()
            receiver_name = getattr(self.receiver, 'objectName', lambda: 'Unknown')()
            slot_name = getattr(self.slot, '__name__', 'unknown_slot')
            self.connection_id = f"{sender_name}.{self.signal_name}->{receiver_name}.{slot_name}"


class SignalManager(QObject):
    """
    Manages signal connections with automatic cleanup and lifecycle tracking.
    
    Provides centralized management of Qt signal connections with:
    - Automatic cleanup based on object lifecycle
    - Connection scope management
    - Connection tracking and debugging
    - Memory leak prevention
    - Bulk connection operations
    
    Usage:
        class MyView(QWidget):
            def __init__(self):
                super().__init__()
                self.signal_manager = SignalManager(self)
                
                # Connect with automatic cleanup
                self.signal_manager.connect(
                    self.button, "clicked",
                    self, self._on_button_clicked,
                    scope=ConnectionScope.VIEW_LIFECYCLE
                )
    """
    
    # Signals for monitoring connection lifecycle
    connection_created = Signal(str)      # connection_id
    connection_removed = Signal(str)      # connection_id
    connections_cleared = Signal(str)     # scope_name
    
    def __init__(self, parent: QObject = None):
        """
        Initialize the signal manager.
        
        Args:
            parent: Parent object for Qt memory management
        """
        super().__init__(parent)
        
        # Connection tracking
        self._connections: Dict[str, ConnectionInfo] = {}
        self._connections_by_scope: Dict[ConnectionScope, Set[str]] = {
            scope: set() for scope in ConnectionScope
        }
        self._connections_by_sender: WeakKeyDictionary[QObject, Set[str]] = WeakKeyDictionary()
        self._connections_by_receiver: WeakKeyDictionary[QObject, Set[str]] = WeakKeyDictionary()
        
        # Weak references to objects for cleanup
        self._tracked_objects: WeakSet[QObject] = WeakSet()
        
        DebugLogger.log("SignalManager initialized", "debug")
    
    def connect(self,
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
            signal_name: Name of the signal (without signal signature)
            receiver: Object receiving the signal
            slot: Slot function to connect
            scope: Connection lifecycle scope
            connection_id: Optional custom connection identifier
            
        Returns:
            str: Connection ID for later reference
        """
        try:
            # Get the actual signal object
            signal_obj = getattr(sender, signal_name, None)
            if signal_obj is None:
                raise AttributeError(f"Signal '{signal_name}' not found on {sender}")
            
            if not isinstance(signal_obj, Signal):
                raise TypeError(f"'{signal_name}' is not a Signal")
            
            # Create connection info
            connection_info = ConnectionInfo(
                sender=sender,
                signal_name=signal_name,
                receiver=receiver,
                slot=slot,
                scope=scope,
                connection_id=connection_id or "",
                created_at=self._get_current_time_ms()
            )
            
            # Make the actual Qt connection
            meta_connection = signal_obj.connect(slot)
            connection_info.meta_connection = meta_connection
            
            # Store connection info
            conn_id = connection_info.connection_id
            self._connections[conn_id] = connection_info
            self._connections_by_scope[scope].add(conn_id)
            
            # Track by sender/receiver for cleanup
            if sender not in self._connections_by_sender:
                self._connections_by_sender[sender] = set()
            self._connections_by_sender[sender].add(conn_id)
            
            if receiver not in self._connections_by_receiver:
                self._connections_by_receiver[receiver] = set()
            self._connections_by_receiver[receiver].add(conn_id)
            
            # Track objects for lifecycle management
            self._tracked_objects.add(sender)
            self._tracked_objects.add(receiver)
            
            # Setup cleanup on object destruction if in VIEW_LIFECYCLE scope
            if scope == ConnectionScope.VIEW_LIFECYCLE:
                self._setup_object_cleanup(sender, conn_id)
                self._setup_object_cleanup(receiver, conn_id)
            
            self.connection_created.emit(conn_id)
            
            DebugLogger.log(
                f"Connected signal: {conn_id} (scope: {scope.value})",
                "debug"
            )
            
            return conn_id
            
        except Exception as e:
            DebugLogger.log(f"Error connecting signal: {e}", "error")
            raise
    
    def disconnect(self, connection_id: str) -> bool:
        """
        Disconnect a managed signal connection.
        
        Args:
            connection_id: Connection identifier
            
        Returns:
            bool: True if connection was found and disconnected
        """
        connection_info = self._connections.get(connection_id)
        if not connection_info:
            return False
        
        try:
            # Disconnect the Qt connection
            if connection_info.meta_connection:
                signal_obj = getattr(connection_info.sender, connection_info.signal_name, None)
                if signal_obj and isinstance(signal_obj, Signal):
                    signal_obj.disconnect(connection_info.meta_connection)
            
            # Remove from tracking
            self._remove_connection_tracking(connection_id, connection_info)
            
            self.connection_removed.emit(connection_id)
            
            DebugLogger.log(f"Disconnected signal: {connection_id}", "debug")
            return True
            
        except Exception as e:
            DebugLogger.log(f"Error disconnecting signal {connection_id}: {e}", "error")
            return False
    
    def disconnect_by_scope(self, scope: ConnectionScope) -> int:
        """
        Disconnect all connections in a specific scope.
        
        Args:
            scope: Scope to clear
            
        Returns:
            int: Number of connections disconnected
        """
        connection_ids = list(self._connections_by_scope[scope])
        disconnected_count = 0
        
        for conn_id in connection_ids:
            if self.disconnect(conn_id):
                disconnected_count += 1
        
        self.connections_cleared.emit(scope.value)
        
        DebugLogger.log(
            f"Disconnected {disconnected_count} connections in scope: {scope.value}",
            "debug"
        )
        
        return disconnected_count
    
    def disconnect_by_sender(self, sender: QObject) -> int:
        """
        Disconnect all connections from a specific sender.
        
        Args:
            sender: Sender object
            
        Returns:
            int: Number of connections disconnected
        """
        connection_ids = list(self._connections_by_sender.get(sender, set()))
        disconnected_count = 0
        
        for conn_id in connection_ids:
            if self.disconnect(conn_id):
                disconnected_count += 1
        
        DebugLogger.log(
            f"Disconnected {disconnected_count} connections from sender: {sender}",
            "debug"
        )
        
        return disconnected_count
    
    def disconnect_by_receiver(self, receiver: QObject) -> int:
        """
        Disconnect all connections to a specific receiver.
        
        Args:
            receiver: Receiver object
            
        Returns:
            int: Number of connections disconnected
        """
        connection_ids = list(self._connections_by_receiver.get(receiver, set()))
        disconnected_count = 0
        
        for conn_id in connection_ids:
            if self.disconnect(conn_id):
                disconnected_count += 1
        
        DebugLogger.log(
            f"Disconnected {disconnected_count} connections to receiver: {receiver}",
            "debug"
        )
        
        return disconnected_count
    
    def disconnect_all(self) -> int:
        """
        Disconnect all managed connections.
        
        Returns:
            int: Number of connections disconnected
        """
        connection_ids = list(self._connections.keys())
        disconnected_count = 0
        
        for conn_id in connection_ids:
            if self.disconnect(conn_id):
                disconnected_count += 1
        
        DebugLogger.log(f"Disconnected all {disconnected_count} connections", "debug")
        return disconnected_count
    
    def bulk_connect(self, connection_specs: List[Dict[str, Any]]) -> List[str]:
        """
        Create multiple connections in batch.
        
        Args:
            connection_specs: List of connection specification dictionaries
                Each dict should contain: sender, signal_name, receiver, slot
                Optional keys: scope, connection_id
                
        Returns:
            List[str]: List of created connection IDs
        """
        connection_ids = []
        
        for spec in connection_specs:
            try:
                conn_id = self.connect(
                    sender=spec['sender'],
                    signal_name=spec['signal_name'],
                    receiver=spec['receiver'],
                    slot=spec['slot'],
                    scope=spec.get('scope', ConnectionScope.VIEW_LIFECYCLE),
                    connection_id=spec.get('connection_id')
                )
                connection_ids.append(conn_id)
            except Exception as e:
                DebugLogger.log(f"Error in bulk connect: {e}", "error")
        
        DebugLogger.log(f"Bulk connected {len(connection_ids)} signals", "debug")
        return connection_ids
    
    def get_connection_info(self, connection_id: str) -> Optional[ConnectionInfo]:
        """Get information about a specific connection."""
        return self._connections.get(connection_id)
    
    def get_connections_by_scope(self, scope: ConnectionScope) -> List[ConnectionInfo]:
        """Get all connections in a specific scope."""
        connection_ids = self._connections_by_scope[scope]
        return [self._connections[conn_id] for conn_id in connection_ids 
                if conn_id in self._connections]
    
    def get_active_connection_count(self) -> int:
        """Get the total number of active connections."""
        return len(self._connections)
    
    def get_scope_statistics(self) -> Dict[str, int]:
        """Get connection count statistics by scope."""
        stats = {}
        for scope, connection_ids in self._connections_by_scope.items():
            # Count only existing connections (cleanup may have removed some)
            active_count = sum(1 for conn_id in connection_ids if conn_id in self._connections)
            stats[scope.value] = active_count
        return stats
    
    def has_connection(self, connection_id: str) -> bool:
        """Check if a connection exists and is active."""
        return connection_id in self._connections
    
    def is_connected(self, sender: QObject, signal_name: str, receiver: QObject, slot: Callable) -> bool:
        """
        Check if a specific signal connection exists.
        
        Args:
            sender: Signal sender
            signal_name: Signal name
            receiver: Signal receiver
            slot: Slot function
            
        Returns:
            bool: True if connection exists
        """
        for connection_info in self._connections.values():
            if (connection_info.sender == sender and
                connection_info.signal_name == signal_name and
                connection_info.receiver == receiver and
                connection_info.slot == slot):
                return True
        return False
    
    def cleanup_view_connections(self) -> int:
        """
        Cleanup all VIEW_LIFECYCLE connections.
        
        Returns:
            int: Number of connections cleaned up
        """
        return self.disconnect_by_scope(ConnectionScope.VIEW_LIFECYCLE)
    
    def cleanup_temporary_connections(self) -> int:
        """
        Cleanup all TEMPORARY connections.
        
        Returns:
            int: Number of connections cleaned up
        """
        return self.disconnect_by_scope(ConnectionScope.TEMPORARY)
    
    def _setup_object_cleanup(self, obj: QObject, connection_id: str) -> None:
        """Setup automatic cleanup when object is destroyed."""
        def cleanup_callback():
            if connection_id in self._connections:
                self.disconnect(connection_id)
        
        # Use weak reference to avoid keeping object alive
        obj_ref = ref(obj, lambda _: cleanup_callback())
    
    def _remove_connection_tracking(self, connection_id: str, connection_info: ConnectionInfo) -> None:
        """Remove connection from all tracking structures."""
        # Remove from main connections
        self._connections.pop(connection_id, None)
        
        # Remove from scope tracking
        self._connections_by_scope[connection_info.scope].discard(connection_id)
        
        # Remove from sender/receiver tracking
        if connection_info.sender in self._connections_by_sender:
            self._connections_by_sender[connection_info.sender].discard(connection_id)
        
        if connection_info.receiver in self._connections_by_receiver:
            self._connections_by_receiver[connection_info.receiver].discard(connection_id)
    
    def _get_current_time_ms(self) -> float:
        """Get current time in milliseconds."""
        from time import perf_counter
        return perf_counter() * 1000
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get comprehensive debug information about all connections."""
        debug_info = {
            'total_connections': len(self._connections),
            'scope_statistics': self.get_scope_statistics(),
            'tracked_objects_count': len(self._tracked_objects),
            'connections_by_sender_count': len(self._connections_by_sender),
            'connections_by_receiver_count': len(self._connections_by_receiver),
            'connections_detail': []
        }
        
        for conn_id, conn_info in self._connections.items():
            sender_name = getattr(conn_info.sender, 'objectName', lambda: 'Unknown')()
            receiver_name = getattr(conn_info.receiver, 'objectName', lambda: 'Unknown')()
            
            debug_info['connections_detail'].append({
                'id': conn_id,
                'sender': sender_name,
                'signal': conn_info.signal_name,
                'receiver': receiver_name,
                'scope': conn_info.scope.value,
                'created_at': conn_info.created_at
            })
        
        return debug_info


# ── Utility Functions ───────────────────────────────────────────────────────────────────────────────────────────

def create_managed_connections(parent: QObject, 
                             connection_specs: List[Dict[str, Any]],
                             default_scope: ConnectionScope = ConnectionScope.VIEW_LIFECYCLE) -> SignalManager:
    """
    Convenience function to create a SignalManager and make multiple connections.
    
    Args:
        parent: Parent object for the SignalManager
        connection_specs: List of connection specifications
        default_scope: Default scope for connections without explicit scope
        
    Returns:
        SignalManager: Configured signal manager
    """
    manager = SignalManager(parent)
    
    # Set default scope for specs that don't have one
    for spec in connection_specs:
        if 'scope' not in spec:
            spec['scope'] = default_scope
    
    manager.bulk_connect(connection_specs)
    return manager