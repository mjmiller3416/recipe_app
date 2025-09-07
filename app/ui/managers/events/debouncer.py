"""app/ui/managers/events/debouncer.py

Generic debouncing utilities for event management in MealGenie views.
Provides configurable debouncing strategies to prevent excessive updates
during user interactions like filtering, searching, and input validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, Optional
from weakref import WeakKeyDictionary

from PySide6.QtCore import QObject, QTimer

from _dev_tools import DebugLogger

class DebouncingStrategy(Enum):
    """Debouncing strategy options."""
    TRAILING = "trailing"  # Execute at the end of the delay period
    LEADING = "leading"    # Execute immediately, then ignore subsequent calls
    THROTTLE = "throttle"  # Execute at most once per delay period


@dataclass
class DebouncingOptions:
    """Configuration options for debouncing behavior."""
    delay_ms: int = 250
    strategy: DebouncingStrategy = DebouncingStrategy.TRAILING
    max_wait_ms: Optional[int] = None  # Maximum time to wait before forcing execution
    immediate_on_first: bool = False   # Execute immediately on first call


class DebouncedFunction:
    """Manages debouncing for a specific function."""
    
    def __init__(self, function: Callable, options: DebouncingOptions):
        self.function = function
        self.options = options
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._execute_trailing)
        
        # State tracking
        self._pending_args: Optional[tuple] = None
        self._pending_kwargs: Optional[Dict[str, Any]] = None
        self._first_call = True
        self._last_execution_time = 0
        self._forced_execution_timer: Optional[QTimer] = None
        
        # Setup max wait timer if configured
        if self.options.max_wait_ms:
            self._forced_execution_timer = QTimer()
            self._forced_execution_timer.setSingleShot(True)
            self._forced_execution_timer.timeout.connect(self._force_execution)
    
    def __call__(self, *args, **kwargs) -> Any:
        """Execute the debounced function with the specified strategy."""
        current_time = self._get_current_time_ms()
        
        # Store arguments for later execution
        self._pending_args = args
        self._pending_kwargs = kwargs
        
        if self.options.strategy == DebouncingStrategy.LEADING:
            return self._execute_leading(current_time)
        elif self.options.strategy == DebouncingStrategy.THROTTLE:
            return self._execute_throttle(current_time)
        else:  # TRAILING (default)
            return self._execute_trailing_setup()
    
    def _execute_leading(self, current_time: float) -> Any:
        """Execute using leading edge strategy."""
        if self._first_call or not self._timer.isActive():
            # Execute immediately
            self._first_call = False
            self._last_execution_time = current_time
            result = self._execute_function()
            
            # Start timer to prevent further executions
            self._timer.start(self.options.delay_ms)
            return result
        
        # Timer is active, ignore this call
        return None
    
    def _execute_throttle(self, current_time: float) -> Any:
        """Execute using throttle strategy."""
        time_since_last = current_time - self._last_execution_time
        
        if self._first_call or time_since_last >= self.options.delay_ms:
            # Execute immediately
            self._first_call = False
            self._last_execution_time = current_time
            return self._execute_function()
        
        # Schedule for later if not already scheduled
        if not self._timer.isActive():
            remaining_time = self.options.delay_ms - time_since_last
            self._timer.start(int(remaining_time))
        
        return None
    
    def _execute_trailing_setup(self) -> None:
        """Setup trailing edge execution."""
        # Reset timer for debouncing
        self._timer.stop()
        self._timer.start(self.options.delay_ms)
        
        # Handle immediate execution on first call
        if self._first_call and self.options.immediate_on_first:
            self._first_call = False
            return self._execute_function()
        
        self._first_call = False
        
        # Start max wait timer if configured
        if self._forced_execution_timer and not self._forced_execution_timer.isActive():
            self._forced_execution_timer.start(self.options.max_wait_ms)
        
        return None
    
    def _execute_trailing(self) -> Any:
        """Execute the trailing edge debounced function."""
        # Stop forced execution timer if active
        if self._forced_execution_timer:
            self._forced_execution_timer.stop()
        
        return self._execute_function()
    
    def _force_execution(self) -> Any:
        """Force execution due to max wait timeout."""
        self._timer.stop()  # Cancel normal debounce timer
        DebugLogger.log("Forced execution due to max wait timeout", "debug")
        return self._execute_function()
    
    def _execute_function(self) -> Any:
        """Execute the wrapped function with current arguments."""
        try:
            if self._pending_args is not None and self._pending_kwargs is not None:
                return self.function(*self._pending_args, **self._pending_kwargs)
            return None
        except Exception as e:
            DebugLogger.log(f"Error executing debounced function: {e}", "error")
            return None
    
    def cancel(self) -> None:
        """Cancel any pending execution."""
        self._timer.stop()
        if self._forced_execution_timer:
            self._forced_execution_timer.stop()
        self._pending_args = None
        self._pending_kwargs = None
    
    def flush(self) -> Any:
        """Force immediate execution of any pending call."""
        if self._timer.isActive():
            self._timer.stop()
            if self._forced_execution_timer:
                self._forced_execution_timer.stop()
            return self._execute_function()
        return None
    
    def _get_current_time_ms(self) -> float:
        """Get current time in milliseconds."""
        from time import perf_counter
        return perf_counter() * 1000


class Debouncer(QObject):
    """
    Generic debouncing manager for UI event handling.
    
    Provides configurable debouncing strategies for preventing excessive
    function calls during rapid user interactions. Supports multiple
    debouncing patterns and automatic cleanup.
    
    Usage:
        # Create debouncer instance
        debouncer = Debouncer()
        
        # Register debounced function
        debounced_filter = debouncer.debounce(
            self._apply_filters,
            DebouncingOptions(delay_ms=300, strategy=DebouncingStrategy.TRAILING)
        )
        
        # Use in signal connections
        self.search_input.textChanged.connect(debounced_filter)
        
        # Or call directly
        debounced_filter("new filter value")
    """
    
    def __init__(self, parent: QObject = None):
        """
        Initialize the debouncer.
        
        Args:
            parent: Optional parent QObject for Qt memory management
        """
        super().__init__(parent)
        
        # Track debounced functions for cleanup
        self._debounced_functions: WeakKeyDictionary[Callable, DebouncedFunction] = WeakKeyDictionary()
        self._function_registry: Dict[str, DebouncedFunction] = {}
        
        DebugLogger.log("Debouncer initialized", "debug")
    
    def debounce(self,
                 function: Callable,
                 options: Optional[DebouncingOptions] = None,
                 key: Optional[str] = None) -> DebouncedFunction:
        """
        Create a debounced version of the given function.
        
        Args:
            function: Function to debounce
            options: Debouncing configuration options
            key: Optional key for function registry (enables later access)
            
        Returns:
            DebouncedFunction: Debounced wrapper function
        """
        if options is None:
            options = DebouncingOptions()
        
        # Check if function is already debounced
        if function in self._debounced_functions:
            existing_debounced = self._debounced_functions[function]
            DebugLogger.log(f"Returning existing debounced function for {function.__name__}", "debug")
            return existing_debounced
        
        # Create new debounced function
        debounced_func = DebouncedFunction(function, options)
        self._debounced_functions[function] = debounced_func
        
        # Register with key if provided
        if key:
            self._function_registry[key] = debounced_func
            DebugLogger.log(f"Registered debounced function with key: {key}", "debug")
        
        DebugLogger.log(
            f"Created debounced function: {function.__name__} "
            f"(delay: {options.delay_ms}ms, strategy: {options.strategy.value})",
            "debug"
        )
        
        return debounced_func
    
    def get_debounced_function(self, key: str) -> Optional[DebouncedFunction]:
        """
        Get a registered debounced function by key.
        
        Args:
            key: Registration key for the function
            
        Returns:
            DebouncedFunction or None if not found
        """
        return self._function_registry.get(key)
    
    def cancel_all(self) -> None:
        """Cancel all pending debounced executions."""
        for debounced_func in self._debounced_functions.values():
            debounced_func.cancel()
        
        for debounced_func in self._function_registry.values():
            debounced_func.cancel()
        
        DebugLogger.log("Cancelled all pending debounced executions", "debug")
    
    def flush_all(self) -> None:
        """Force immediate execution of all pending debounced functions."""
        for debounced_func in self._debounced_functions.values():
            debounced_func.flush()
        
        for debounced_func in self._function_registry.values():
            debounced_func.flush()
        
        DebugLogger.log("Flushed all pending debounced executions", "debug")
    
    def cancel_function(self, key: str) -> bool:
        """
        Cancel pending execution for a specific registered function.
        
        Args:
            key: Registration key for the function
            
        Returns:
            bool: True if function was found and cancelled
        """
        debounced_func = self._function_registry.get(key)
        if debounced_func:
            debounced_func.cancel()
            DebugLogger.log(f"Cancelled debounced function: {key}", "debug")
            return True
        return False
    
    def flush_function(self, key: str) -> Any:
        """
        Force immediate execution for a specific registered function.
        
        Args:
            key: Registration key for the function
            
        Returns:
            Function result or None if not found
        """
        debounced_func = self._function_registry.get(key)
        if debounced_func:
            result = debounced_func.flush()
            DebugLogger.log(f"Flushed debounced function: {key}", "debug")
            return result
        return None
    
    def get_active_count(self) -> int:
        """Get the number of functions with pending executions."""
        active_count = 0
        
        for debounced_func in self._debounced_functions.values():
            if debounced_func._timer.isActive():
                active_count += 1
        
        for debounced_func in self._function_registry.values():
            if debounced_func._timer.isActive():
                active_count += 1
        
        return active_count
    
    def get_registry_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about registered functions."""
        info = {}
        
        for key, debounced_func in self._function_registry.items():
            info[key] = {
                'function_name': debounced_func.function.__name__,
                'delay_ms': debounced_func.options.delay_ms,
                'strategy': debounced_func.options.strategy.value,
                'is_active': debounced_func._timer.isActive(),
                'has_pending': debounced_func._pending_args is not None
            }
        
        return info


# ── Utility Functions ───────────────────────────────────────────────────────────────────────────────────────────

def create_debounced_function(function: Callable,
                             delay_ms: int = 250,
                             strategy: DebouncingStrategy = DebouncingStrategy.TRAILING,
                             max_wait_ms: Optional[int] = None) -> DebouncedFunction:
    """
    Convenience function to create a debounced function with simple parameters.
    
    Args:
        function: Function to debounce
        delay_ms: Debounce delay in milliseconds
        strategy: Debouncing strategy to use
        max_wait_ms: Maximum wait time before forcing execution
        
    Returns:
        DebouncedFunction: Debounced wrapper
    """
    options = DebouncingOptions(
        delay_ms=delay_ms,
        strategy=strategy,
        max_wait_ms=max_wait_ms
    )
    return DebouncedFunction(function, options)


def debounce_decorator(delay_ms: int = 250,
                      strategy: DebouncingStrategy = DebouncingStrategy.TRAILING,
                      max_wait_ms: Optional[int] = None):
    """
    Decorator to create debounced methods.
    
    Usage:
        class MyView:
            @debounce_decorator(delay_ms=300)
            def _on_filter_changed(self, value):
                # This will be debounced
                pass
    """
    def decorator(func):
        options = DebouncingOptions(
            delay_ms=delay_ms,
            strategy=strategy,
            max_wait_ms=max_wait_ms
        )
        return DebouncedFunction(func, options)
    return decorator