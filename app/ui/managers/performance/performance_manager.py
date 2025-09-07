"""app/ui/managers/performance/performance_manager.py

Comprehensive performance management system for UI components.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
import gc
from typing import Any, Callable, Dict, List, Optional, TypeVar
import weakref

from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtWidgets import QWidget

from _dev_tools.debug_logger import DebugLogger
from .metrics_tracker import MetricsTracker, performance_timer
from .object_pool import ObjectPool, WidgetPool, create_widget_pool
from .progressive_renderer import (
    CallbackProgressiveRenderer,
    ProgressiveRenderer,
    ProgressiveRenderTarget,
)

# ── Type Variables ─────────────────────────────────────────────────────────────────────────────────────────
T = TypeVar('T')


# ── Performance Manager ────────────────────────────────────────────────────────────────────────────────────
class PerformanceManager(QObject):
    """
    Comprehensive performance management system for UI components.

    Provides object pooling, progressive rendering, memory management,
    and performance metrics tracking.

    Signals:
        memory_cleanup_started: Emitted when memory cleanup starts
        memory_cleanup_completed: Emitted when memory cleanup completes
        performance_warning: Emitted when performance threshold is exceeded
    """

    # Signals
    memory_cleanup_started = Signal()
    memory_cleanup_completed = Signal(int)  # objects_cleaned
    performance_warning = Signal(str, float, float)  # operation, duration, threshold

    def __init__(self, parent: Optional[QObject] = None):
        """Initialize performance manager."""
        super().__init__(parent)

        # Core components
        self._metrics_tracker = MetricsTracker()
        self._object_pools: Dict[str, ObjectPool] = {}
        self._widget_pools: Dict[str, WidgetPool] = {}
        self._progressive_renderers: Dict[str, ProgressiveRenderer] = {}

        # Memory management
        self._memory_cleanup_timer = QTimer()
        self._memory_cleanup_timer.timeout.connect(self._periodic_memory_cleanup)
        self._memory_cleanup_interval = 60000  # 60 seconds
        self._weak_references: List[weakref.ReferenceType] = []

        # Connect signals
        self._setup_signal_connections()

        # Start periodic cleanup
        self.start_memory_management()

    def _setup_signal_connections(self):
        """Setup signal connections between components."""
        # Connect metrics tracker signals
        self._metrics_tracker.threshold_exceeded.connect(self.performance_warning.emit)
        self._metrics_tracker.threshold_exceeded.connect(self._handle_performance_warning)

    def _handle_performance_warning(self, operation: str, duration: float, threshold: float):
        """Handle performance warnings."""
        DebugLogger.log(
            f"Performance warning: {operation} took {duration*1000:.1f}ms "
            f"(threshold: {threshold*1000:.1f}ms)",
            "warning"
        )

    # ── Metrics Management ─────────────────────────────────────────────────────────────────────────────────
    def get_metrics_tracker(self) -> MetricsTracker:
        """Get the metrics tracker instance."""
        return self._metrics_tracker

    def start_timer(self, operation: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Start timing an operation."""
        return self._metrics_tracker.start_timer(operation, metadata)

    def stop_timer(self, timer_id: str, metadata: Optional[Dict[str, Any]] = None):
        """Stop timing an operation."""
        self._metrics_tracker.stop_timer(timer_id, metadata)

    def record_duration(self, operation: str, duration: float, metadata: Optional[Dict[str, Any]] = None):
        """Record a performance measurement directly."""
        self._metrics_tracker.record_duration(operation, duration, metadata)

    def set_performance_threshold(self, operation: str, threshold_seconds: float):
        """Set performance threshold for an operation."""
        self._metrics_tracker.set_threshold(operation, threshold_seconds)

    def performance_context(self, operation: str, metadata: Optional[Dict[str, Any]] = None):
        """Get a performance timing context manager."""
        return performance_timer(self._metrics_tracker, operation, metadata)

    # ── Object Pool Management ─────────────────────────────────────────────────────────────────────────────
    def create_object_pool(
        self,
        name: str,
        factory: Callable[..., T],
        max_pool_size: int = 50,
        reset_callback: Optional[Callable[[T], None]] = None,
        cleanup_callback: Optional[Callable[[T], None]] = None
    ) -> ObjectPool[T]:
        """
        Create a generic object pool.

        Args:
            name: Unique name for the pool
            factory: Function to create new objects
            max_pool_size: Maximum number of objects to keep in pool
            reset_callback: Optional callback to reset object state
            cleanup_callback: Optional callback to cleanup objects

        Returns:
            Created object pool
        """
        if name in self._object_pools:
            DebugLogger.log(f"Object pool '{name}' already exists", "warning")
            return self._object_pools[name]

        pool = ObjectPool(
            factory=factory,
            max_pool_size=max_pool_size,
            reset_callback=reset_callback,
            cleanup_callback=cleanup_callback
        )

        self._object_pools[name] = pool
        DebugLogger.log(f"Created object pool '{name}' with max size {max_pool_size}", "debug")

        return pool

    def create_widget_pool(
        self,
        name: str,
        widget_factory: Callable[..., QWidget],
        parent_widget: Optional[QWidget] = None,
        max_pool_size: int = 50
    ) -> WidgetPool:
        """
        Create a widget pool.

        Args:
            name: Unique name for the pool
            widget_factory: Function to create new widgets
            parent_widget: Parent widget for created widgets
            max_pool_size: Maximum number of widgets to keep in pool

        Returns:
            Created widget pool
        """
        if name in self._widget_pools:
            DebugLogger.log(f"Widget pool '{name}' already exists", "warning")
            return self._widget_pools[name]

        pool = create_widget_pool(widget_factory, parent_widget, max_pool_size)
        self._widget_pools[name] = pool

        DebugLogger.log(f"Created widget pool '{name}' with max size {max_pool_size}", "debug")

        return pool

    def get_object_pool(self, name: str) -> Optional[ObjectPool]:
        """Get an object pool by name."""
        return self._object_pools.get(name)

    def get_widget_pool(self, name: str) -> Optional[WidgetPool]:
        """Get a widget pool by name."""
        return self._widget_pools.get(name)

    def clear_pool(self, name: str):
        """Clear an object or widget pool."""
        if name in self._object_pools:
            self._object_pools[name].clear_pool()
        elif name in self._widget_pools:
            self._widget_pools[name].clear_pool()
        else:
            DebugLogger.log(f"Pool '{name}' not found", "warning")

    def clear_all_pools(self):
        """Clear all object and widget pools."""
        for pool in self._object_pools.values():
            pool.clear_pool()
        for pool in self._widget_pools.values():
            pool.clear_pool()

        DebugLogger.log("All pools cleared", "debug")

    # ── Progressive Rendering ──────────────────────────────────────────────────────────────────────────────
    def create_progressive_renderer(
        self,
        name: str,
        target: ProgressiveRenderTarget,
        default_batch_size: int = 5,
        default_delay_ms: int = 10
    ) -> ProgressiveRenderer:
        """
        Create a progressive renderer.

        Args:
            name: Unique name for the renderer
            target: Target object that handles rendering
            default_batch_size: Default number of items per batch
            default_delay_ms: Default delay between batches in milliseconds

        Returns:
            Created progressive renderer
        """
        if name in self._progressive_renderers:
            DebugLogger.log(f"Progressive renderer '{name}' already exists", "warning")
            return self._progressive_renderers[name]

        renderer = ProgressiveRenderer(target, default_batch_size, default_delay_ms)
        self._progressive_renderers[name] = renderer

        DebugLogger.log(
            f"Created progressive renderer '{name}' "
            f"(batch size: {default_batch_size}, delay: {default_delay_ms}ms)",
            "debug"
        )

        return renderer

    def create_callback_renderer(
        self,
        name: str,
        render_callback: Callable[[List[T], int, int], None],
        completion_callback: Optional[Callable[[], None]] = None,
        default_batch_size: int = 5,
        default_delay_ms: int = 10
    ) -> CallbackProgressiveRenderer:
        """
        Create a callback-based progressive renderer.

        Args:
            name: Unique name for the renderer
            render_callback: Callback for rendering batches
            completion_callback: Optional callback for completion
            default_batch_size: Default number of items per batch
            default_delay_ms: Default delay between batches in milliseconds

        Returns:
            Created callback progressive renderer
        """
        if name in self._progressive_renderers:
            DebugLogger.log(f"Progressive renderer '{name}' already exists", "warning")
            return self._progressive_renderers[name]

        renderer = CallbackProgressiveRenderer(
            render_callback=render_callback,
            completion_callback=completion_callback,
            default_batch_size=default_batch_size,
            default_delay_ms=default_delay_ms
        )

        self._progressive_renderers[name] = renderer

        DebugLogger.log(
            f"Created callback progressive renderer '{name}' "
            f"(batch size: {default_batch_size}, delay: {default_delay_ms}ms)",
            "debug"
        )

        return renderer

    def get_progressive_renderer(self, name: str) -> Optional[ProgressiveRenderer]:
        """Get a progressive renderer by name."""
        return self._progressive_renderers.get(name)

    def start_progressive_rendering(
        self,
        name: str,
        items: List[T],
        batch_size: Optional[int] = None,
        delay_ms: Optional[int] = None
    ) -> bool:
        """
        Start progressive rendering for a named renderer.

        Args:
            name: Name of the renderer
            items: Items to render progressively
            batch_size: Number of items per batch (uses renderer default if None)
            delay_ms: Delay between batches in milliseconds (uses renderer default if None)

        Returns:
            True if rendering started, False if renderer not found
        """
        renderer = self.get_progressive_renderer(name)
        if not renderer:
            DebugLogger.log(f"Progressive renderer '{name}' not found", "warning")
            return False

        renderer.start_rendering(items, batch_size, delay_ms)
        return True

    def stop_progressive_rendering(self, name: str) -> bool:
        """
        Stop progressive rendering for a named renderer.

        Args:
            name: Name of the renderer

        Returns:
            True if rendering stopped, False if renderer not found
        """
        renderer = self.get_progressive_renderer(name)
        if not renderer:
            DebugLogger.log(f"Progressive renderer '{name}' not found", "warning")
            return False

        renderer.cancel_rendering()
        return True

    # ── Memory Management ──────────────────────────────────────────────────────────────────────────────────
    def start_memory_management(self, interval_ms: Optional[int] = None):
        """
        Start periodic memory management.

        Args:
            interval_ms: Cleanup interval in milliseconds (uses default if None)
        """
        if interval_ms:
            self._memory_cleanup_interval = interval_ms

        self._memory_cleanup_timer.start(self._memory_cleanup_interval)
        DebugLogger.log(f"Started memory management (interval: {self._memory_cleanup_interval}ms)", "debug")

    def stop_memory_management(self):
        """Stop periodic memory management."""
        self._memory_cleanup_timer.stop()
        DebugLogger.log("Stopped memory management", "debug")

    def trigger_memory_cleanup(self):
        """Trigger immediate memory cleanup."""
        self._periodic_memory_cleanup()

    def _periodic_memory_cleanup(self):
        """Perform periodic memory cleanup."""
        self.memory_cleanup_started.emit()

        cleaned_objects = 0

        # Clean up dead weak references
        alive_refs = []
        for ref in self._weak_references:
            if ref() is None:
                cleaned_objects += 1
            else:
                alive_refs.append(ref)

        self._weak_references = alive_refs

        # Force garbage collection
        collected = gc.collect()
        cleaned_objects += collected

        self.memory_cleanup_completed.emit(cleaned_objects)

        DebugLogger.log(f"Memory cleanup completed: {cleaned_objects} objects cleaned", "debug")

    def track_object(self, obj: Any):
        """
        Track an object for memory management.

        Args:
            obj: Object to track
        """
        self._weak_references.append(weakref.ref(obj))

    # ── Statistics and Reporting ───────────────────────────────────────────────────────────────────────────
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        # Metrics summary
        metrics_summary = self._metrics_tracker.get_summary()

        # Pool statistics
        pool_stats = {}
        for name, pool in self._object_pools.items():
            pool_stats[f"object_pool_{name}"] = pool.statistics

        for name, pool in self._widget_pools.items():
            pool_stats[f"widget_pool_{name}"] = pool.statistics

        # Renderer status
        renderer_status = {}
        for name, renderer in self._progressive_renderers.items():
            renderer_status[name] = renderer.progress_info

        # Memory statistics
        memory_stats = {
            'tracked_objects': len([ref for ref in self._weak_references if ref() is not None]),
            'dead_references': len([ref for ref in self._weak_references if ref() is None]),
            'total_references': len(self._weak_references),
        }

        return {
            'metrics': metrics_summary,
            'pools': pool_stats,
            'renderers': renderer_status,
            'memory': memory_stats,
            'cleanup_interval_ms': self._memory_cleanup_interval,
        }

    def log_performance_summary(self):
        """Log performance summary to debug output."""
        summary = self.get_performance_summary()

        DebugLogger.log("=== Performance Summary ===", "info")
        DebugLogger.log(f"Metrics: {summary['metrics']['total_operations']} operations, "
                       f"{summary['metrics']['total_measurements']} measurements", "info")
        DebugLogger.log(f"Pools: {len(summary['pools'])} pools active", "info")
        DebugLogger.log(f"Renderers: {len(summary['renderers'])} renderers", "info")
        DebugLogger.log(f"Memory: {summary['memory']['tracked_objects']} objects tracked", "info")

    # ── Cleanup ────────────────────────────────────────────────────────────────────────────────────────────
    def cleanup(self):
        """Clean up all performance management resources."""
        # Stop memory management
        self.stop_memory_management()

        # Clear all pools
        self.clear_all_pools()

        # Cancel all progressive rendering
        for name, renderer in self._progressive_renderers.items():
            if renderer.is_rendering:
                renderer.cancel_rendering()

        # Clear metrics
        self._metrics_tracker.clear_history()

        # Clear collections
        self._object_pools.clear()
        self._widget_pools.clear()
        self._progressive_renderers.clear()
        self._weak_references.clear()

        DebugLogger.log("Performance manager cleanup completed", "debug")
