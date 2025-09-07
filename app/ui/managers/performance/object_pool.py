"""app/ui/managers/performance/object_pool.py

Generic object pool implementation for efficient widget management and reuse.
"""

from abc import ABC, abstractmethod
from collections import deque
from typing import Any, Callable, Deque, Dict, Generic, List, Optional, TypeVar, Union

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
import weakref

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QWidget

from _dev_tools.debug_logger import DebugLogger

# ── Type Variables ─────────────────────────────────────────────────────────────────────────────────────────
T = TypeVar('T')


# ── Abstract Base ──────────────────────────────────────────────────────────────────────────────────────────
class PoolableObject(ABC):
    """Interface for objects that can be pooled."""
    
    @abstractmethod
    def reset_state(self):
        """Reset object state for reuse."""
        pass
    
    @abstractmethod
    def cleanup(self):
        """Clean up object resources."""
        pass


# ── Generic Object Pool ────────────────────────────────────────────────────────────────────────────────────
class ObjectPool(Generic[T], QObject):
    """
    Generic object pool for efficient reuse of expensive objects.
    
    Signals:
        object_created: Emitted when a new object is created
        object_reused: Emitted when an object is reused from pool
        object_returned: Emitted when an object is returned to pool
        pool_cleared: Emitted when pool is cleared
    """
    
    # Signals
    object_created = Signal(object)  # object
    object_reused = Signal(object)   # object
    object_returned = Signal(object) # object
    pool_cleared = Signal()
    
    def __init__(
        self,
        factory: Callable[..., T],
        max_pool_size: int = 50,
        reset_callback: Optional[Callable[[T], None]] = None,
        cleanup_callback: Optional[Callable[[T], None]] = None
    ):
        """
        Initialize object pool.
        
        Args:
            factory: Function to create new objects
            max_pool_size: Maximum number of objects to keep in pool
            reset_callback: Optional callback to reset object state
            cleanup_callback: Optional callback to cleanup objects
        """
        super().__init__()
        
        self._factory = factory
        self._max_pool_size = max_pool_size
        self._reset_callback = reset_callback
        self._cleanup_callback = cleanup_callback
        
        self._available_objects: Deque[T] = deque(maxlen=max_pool_size)
        self._in_use_objects: List[T] = []
        self._creation_args: Optional[tuple] = None
        self._creation_kwargs: Optional[Dict[str, Any]] = None
        
        # Statistics
        self._total_created = 0
        self._total_reused = 0
        self._total_returned = 0
    
    def set_creation_args(self, *args, **kwargs):
        """Set arguments for object creation."""
        self._creation_args = args
        self._creation_kwargs = kwargs
    
    def get_object(self, *args, **kwargs) -> T:
        """
        Get an object from pool or create new one.
        
        Args:
            *args: Arguments for object creation (if needed)
            **kwargs: Keyword arguments for object creation (if needed)
            
        Returns:
            Object instance
        """
        # Try to reuse from pool first
        if self._available_objects:
            obj = self._available_objects.popleft()
            self._in_use_objects.append(obj)
            
            # Reset object state
            self._reset_object(obj)
            
            self._total_reused += 1
            self.object_reused.emit(obj)
            
            DebugLogger.log(
                f"Reused object from pool (pool size: {len(self._available_objects)}, "
                f"in use: {len(self._in_use_objects)})",
                "debug"
            )
            return obj
        
        # Create new object if pool is empty
        create_args = args or self._creation_args or ()
        create_kwargs = kwargs or self._creation_kwargs or {}
        
        obj = self._factory(*create_args, **create_kwargs)
        self._in_use_objects.append(obj)
        
        self._total_created += 1
        self.object_created.emit(obj)
        
        DebugLogger.log(
            f"Created new object (total created: {self._total_created}, "
            f"in use: {len(self._in_use_objects)})",
            "debug"
        )
        return obj
    
    def return_object(self, obj: T):
        """
        Return object to pool for reuse.
        
        Args:
            obj: Object to return to pool
        """
        if obj not in self._in_use_objects:
            DebugLogger.log("Attempted to return object not in use", "warning")
            return
        
        self._in_use_objects.remove(obj)
        
        # Reset object state
        self._reset_object(obj)
        
        # Add to pool if not at capacity
        if len(self._available_objects) < self._max_pool_size:
            self._available_objects.append(obj)
            self._total_returned += 1
            self.object_returned.emit(obj)
            
            DebugLogger.log(
                f"Returned object to pool (pool size: {len(self._available_objects)})",
                "debug"
            )
        else:
            # Pool full - cleanup object
            self._cleanup_object(obj)
            DebugLogger.log("Pool full, cleaned up excess object", "debug")
    
    def return_all_objects(self):
        """Return all in-use objects to the pool."""
        objects_to_return = self._in_use_objects.copy()
        for obj in objects_to_return:
            self.return_object(obj)
    
    def clear_pool(self):
        """Clear all objects from pool."""
        # Cleanup available objects
        while self._available_objects:
            obj = self._available_objects.popleft()
            self._cleanup_object(obj)
        
        # Cleanup in-use objects
        for obj in self._in_use_objects:
            self._cleanup_object(obj)
        self._in_use_objects.clear()
        
        # Reset statistics
        self._total_created = 0
        self._total_reused = 0
        self._total_returned = 0
        
        self.pool_cleared.emit()
        DebugLogger.log("Object pool cleared", "debug")
    
    def _reset_object(self, obj: T):
        """Reset object state for reuse."""
        # Try PoolableObject interface first
        if hasattr(obj, 'reset_state') and callable(getattr(obj, 'reset_state')):
            obj.reset_state()
        elif self._reset_callback:
            self._reset_callback(obj)
    
    def _cleanup_object(self, obj: T):
        """Clean up object resources."""
        # Try PoolableObject interface first
        if hasattr(obj, 'cleanup') and callable(getattr(obj, 'cleanup')):
            obj.cleanup()
        elif self._cleanup_callback:
            self._cleanup_callback(obj)
        
        # For Qt widgets, use deleteLater
        if isinstance(obj, QWidget):
            obj.deleteLater()
    
    # ── Properties ──────────────────────────────────────────────────────────────────────────────────────────
    @property
    def pool_size(self) -> int:
        """Get current pool size."""
        return len(self._available_objects)
    
    @property
    def in_use_count(self) -> int:
        """Get number of objects currently in use."""
        return len(self._in_use_objects)
    
    @property
    def total_count(self) -> int:
        """Get total number of managed objects."""
        return len(self._available_objects) + len(self._in_use_objects)
    
    @property
    def statistics(self) -> Dict[str, int]:
        """Get pool statistics."""
        return {
            'total_created': self._total_created,
            'total_reused': self._total_reused,
            'total_returned': self._total_returned,
            'pool_size': self.pool_size,
            'in_use_count': self.in_use_count,
            'total_count': self.total_count,
            'max_pool_size': self._max_pool_size,
        }


# ── Widget Pool ────────────────────────────────────────────────────────────────────────────────────────────
class WidgetPool(ObjectPool[QWidget]):
    """Specialized object pool for Qt widgets."""
    
    def __init__(
        self,
        widget_factory: Callable[..., QWidget],
        parent_widget: Optional[QWidget] = None,
        max_pool_size: int = 50
    ):
        """
        Initialize widget pool.
        
        Args:
            widget_factory: Function to create new widgets
            parent_widget: Parent widget for created widgets
            max_pool_size: Maximum number of widgets to keep in pool
        """
        super().__init__(
            factory=widget_factory,
            max_pool_size=max_pool_size,
            reset_callback=self._reset_widget,
            cleanup_callback=self._cleanup_widget
        )
        
        self._parent_widget = weakref.ref(parent_widget) if parent_widget else None
    
    def set_parent_widget(self, parent: QWidget):
        """Set parent widget for creating new widgets."""
        self._parent_widget = weakref.ref(parent) if parent else None
    
    def get_widget(self, *args, **kwargs) -> QWidget:
        """Get a widget from pool, ensuring proper parent."""
        # Add parent to kwargs if not provided
        if self._parent_widget and 'parent' not in kwargs:
            parent = self._parent_widget()
            if parent:
                kwargs['parent'] = parent
        
        return self.get_object(*args, **kwargs)
    
    def _reset_widget(self, widget: QWidget):
        """Reset widget state for reuse."""
        # Standard widget reset
        widget.setVisible(False)
        widget.setEnabled(True)
        
        # Call custom reset if available
        if hasattr(widget, 'reset_state') and callable(getattr(widget, 'reset_state')):
            widget.reset_state()
    
    def _cleanup_widget(self, widget: QWidget):
        """Clean up widget resources."""
        # Call custom cleanup if available
        if hasattr(widget, 'cleanup') and callable(getattr(widget, 'cleanup')):
            widget.cleanup()
        
        # Delete widget
        widget.deleteLater()


# ── Factory Functions ──────────────────────────────────────────────────────────────────────────────────────
def create_widget_pool(
    widget_factory: Callable[..., QWidget],
    parent_widget: Optional[QWidget] = None,
    max_pool_size: int = 50
) -> WidgetPool:
    """
    Create a widget pool with the given factory.
    
    Args:
        widget_factory: Function to create new widgets
        parent_widget: Parent widget for created widgets
        max_pool_size: Maximum number of widgets to keep in pool
        
    Returns:
        Configured widget pool
    """
    return WidgetPool(widget_factory, parent_widget, max_pool_size)