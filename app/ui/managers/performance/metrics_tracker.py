"""app/ui/managers/performance/metrics_tracker.py

Performance metrics tracking for UI components and rendering operations.
"""

from collections import defaultdict, deque
from dataclasses import dataclass, field

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
import time
from typing import Any, Deque, Dict, List, Optional

from PySide6.QtCore import QObject, Signal

from _dev_tools.debug_logger import DebugLogger

# ── Data Classes ───────────────────────────────────────────────────────────────────────────────────────────
@dataclass
class PerformanceMetric:
    """Represents a single performance measurement."""
    
    operation: str
    duration: float
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class PerformanceStats:
    """Aggregated performance statistics for an operation."""
    
    operation: str
    total_calls: int = 0
    total_duration: float = 0.0
    avg_duration: float = 0.0
    min_duration: float = float('inf')
    max_duration: float = 0.0
    last_duration: float = 0.0
    
    def update(self, duration: float):
        """Update statistics with a new measurement."""
        self.total_calls += 1
        self.total_duration += duration
        self.avg_duration = self.total_duration / self.total_calls
        self.min_duration = min(self.min_duration, duration)
        self.max_duration = max(self.max_duration, duration)
        self.last_duration = duration


# ── Metrics Tracker ────────────────────────────────────────────────────────────────────────────────────────
class MetricsTracker(QObject):
    """
    Tracks and aggregates performance metrics for UI operations.
    
    Signals:
        metrics_updated: Emitted when performance metrics are updated
        threshold_exceeded: Emitted when an operation exceeds performance threshold
    """
    
    # Signals
    metrics_updated = Signal(str, float)  # operation, duration
    threshold_exceeded = Signal(str, float, float)  # operation, duration, threshold
    
    def __init__(self, max_history: int = 1000):
        super().__init__()
        
        self._max_history = max_history
        self._metrics_history: Deque[PerformanceMetric] = deque(maxlen=max_history)
        self._operation_stats: Dict[str, PerformanceStats] = defaultdict(PerformanceStats)
        self._active_timers: Dict[str, float] = {}
        self._thresholds: Dict[str, float] = {}
        
        # Default thresholds (in seconds)
        self.set_threshold('render_batch', 0.1)  # 100ms
        self.set_threshold('widget_creation', 0.05)  # 50ms
        self.set_threshold('layout_update', 0.02)  # 20ms
    
    def set_threshold(self, operation: str, threshold_seconds: float):
        """Set performance threshold for an operation."""
        self._thresholds[operation] = threshold_seconds
        DebugLogger.log(f"Set performance threshold for '{operation}': {threshold_seconds*1000:.1f}ms", "debug")
    
    def start_timer(self, operation: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Start timing an operation.
        
        Args:
            operation: Name of the operation being timed
            metadata: Optional metadata to associate with this measurement
            
        Returns:
            Timer ID for stopping the timer
        """
        timer_id = f"{operation}_{time.time()}"
        self._active_timers[timer_id] = time.perf_counter()
        
        return timer_id
    
    def stop_timer(self, timer_id: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Stop timing an operation and record the measurement.
        
        Args:
            timer_id: Timer ID returned from start_timer
            metadata: Optional additional metadata
        """
        if timer_id not in self._active_timers:
            DebugLogger.log(f"Timer '{timer_id}' not found", "warning")
            return
        
        start_time = self._active_timers.pop(timer_id)
        duration = time.perf_counter() - start_time
        
        # Extract operation name from timer ID
        operation = timer_id.rsplit('_', 1)[0]
        
        self._record_metric(operation, duration, metadata or {})
    
    def record_duration(self, operation: str, duration: float, metadata: Optional[Dict[str, Any]] = None):
        """
        Record a performance measurement directly.
        
        Args:
            operation: Name of the operation
            duration: Duration in seconds
            metadata: Optional metadata to associate with this measurement
        """
        self._record_metric(operation, duration, metadata or {})
    
    def _record_metric(self, operation: str, duration: float, metadata: Dict[str, Any]):
        """Record a performance metric internally."""
        # Create metric record
        metric = PerformanceMetric(
            operation=operation,
            duration=duration,
            timestamp=time.time(),
            metadata=metadata
        )
        
        # Add to history
        self._metrics_history.append(metric)
        
        # Update operation statistics
        if operation not in self._operation_stats:
            self._operation_stats[operation] = PerformanceStats(operation=operation)
        
        self._operation_stats[operation].update(duration)
        
        # Emit signal
        self.metrics_updated.emit(operation, duration)
        
        # Check threshold
        if operation in self._thresholds:
            threshold = self._thresholds[operation]
            if duration > threshold:
                self.threshold_exceeded.emit(operation, duration, threshold)
                DebugLogger.log(
                    f"Performance threshold exceeded for '{operation}': "
                    f"{duration*1000:.1f}ms > {threshold*1000:.1f}ms",
                    "warning"
                )
        
        # Log performance data
        DebugLogger.log(
            f"Performance: {operation} took {duration*1000:.2f}ms "
            f"(avg: {self._operation_stats[operation].avg_duration*1000:.2f}ms)",
            "debug"
        )
    
    def get_stats(self, operation: Optional[str] = None) -> Dict[str, PerformanceStats]:
        """
        Get performance statistics.
        
        Args:
            operation: Specific operation to get stats for, or None for all
            
        Returns:
            Dictionary of operation stats
        """
        if operation:
            return {operation: self._operation_stats.get(operation, PerformanceStats(operation=operation))}
        
        return dict(self._operation_stats)
    
    def get_recent_metrics(self, operation: Optional[str] = None, count: int = 100) -> List[PerformanceMetric]:
        """
        Get recent performance metrics.
        
        Args:
            operation: Filter by operation name, or None for all
            count: Maximum number of recent metrics to return
            
        Returns:
            List of recent performance metrics
        """
        metrics = list(self._metrics_history)
        
        if operation:
            metrics = [m for m in metrics if m.operation == operation]
        
        return metrics[-count:] if count else metrics
    
    def clear_history(self):
        """Clear performance metrics history."""
        self._metrics_history.clear()
        self._operation_stats.clear()
        DebugLogger.log("Performance metrics history cleared", "debug")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all performance metrics."""
        return {
            'total_operations': len(self._operation_stats),
            'total_measurements': len(self._metrics_history),
            'operations': {
                name: {
                    'calls': stats.total_calls,
                    'avg_ms': round(stats.avg_duration * 1000, 2),
                    'min_ms': round(stats.min_duration * 1000, 2),
                    'max_ms': round(stats.max_duration * 1000, 2),
                    'total_ms': round(stats.total_duration * 1000, 2),
                }
                for name, stats in self._operation_stats.items()
            }
        }


# ── Context Manager ────────────────────────────────────────────────────────────────────────────────────────
class performance_timer:
    """Context manager for timing operations."""
    
    def __init__(self, tracker: MetricsTracker, operation: str, metadata: Optional[Dict[str, Any]] = None):
        self.tracker = tracker
        self.operation = operation
        self.metadata = metadata or {}
        self.timer_id = None
    
    def __enter__(self):
        self.timer_id = self.tracker.start_timer(self.operation, self.metadata)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.timer_id:
            self.tracker.stop_timer(self.timer_id, self.metadata)