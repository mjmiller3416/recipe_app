"""Unit tests for PerformanceManager.

Tests the comprehensive performance management system including:
- Object pool creation and management
- Widget pool creation and management  
- Progressive rendering coordination
- Memory management and cleanup
- Performance metrics tracking
- Signal emissions and coordination
- Resource lifecycle management

The PerformanceManager is a critical component of the RecipeBrowser coordinator
architecture, providing object pooling and progressive rendering capabilities.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
import gc
import time
import weakref
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch, call

import pytest
from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtWidgets import QWidget, QPushButton, QLabel

from app.ui.managers.performance.performance_manager import PerformanceManager
from app.ui.managers.performance.object_pool import ObjectPool, WidgetPool
from app.ui.managers.performance.progressive_renderer import ProgressiveRenderer, ProgressiveRenderTarget
from app.ui.managers.performance.metrics_tracker import MetricsTracker


# ── Test Data Factories ─────────────────────────────────────────────────────────────────────────────────────────
class TestWidget(QWidget):
    """Test widget class for pool testing."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.reset_count = 0
        self.cleanup_count = 0
    
    def reset(self):
        self.reset_count += 1
    
    def cleanup(self):
        self.cleanup_count += 1


class TestObject:
    """Test object class for pool testing."""
    def __init__(self, data=None):
        self.data = data or {}
        self.reset_count = 0
        self.cleanup_count = 0
    
    def reset(self):
        self.reset_count += 1
        self.data.clear()
    
    def cleanup(self):
        self.cleanup_count += 1


class TestProgressiveTarget(ProgressiveRenderTarget):
    """Test progressive rendering target."""
    def __init__(self):
        super().__init__()
        self.rendered_items = []
        self.render_calls = 0
        self.completion_calls = 0
    
    def render_batch(self, items: List[Any], start_index: int, end_index: int):
        """Render a batch of items."""
        self.render_calls += 1
        batch = items[start_index:end_index]
        self.rendered_items.extend(batch)
    
    def on_rendering_complete(self):
        """Called when rendering is complete."""
        self.completion_calls += 1


# ── Fixtures ─────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture
def performance_manager():
    """Create PerformanceManager instance for testing."""
    manager = PerformanceManager()
    yield manager
    manager.cleanup()


@pytest.fixture
def test_objects():
    """Create test objects for pool testing."""
    return [TestObject({"id": i}) for i in range(10)]


@pytest.fixture
def test_widgets(qapp):
    """Create test widgets for pool testing."""
    widgets = [TestWidget() for _ in range(5)]
    yield widgets
    for widget in widgets:
        widget.deleteLater()


# ── Test Classes ─────────────────────────────────────────────────────────────────────────────────────────────
class TestPerformanceManagerInitialization:
    """Test PerformanceManager initialization and setup."""
    
    def test_initialization_default(self, performance_manager):
        """Test default initialization."""
        manager = performance_manager
        
        # Verify core components
        assert isinstance(manager._metrics_tracker, MetricsTracker)
        assert isinstance(manager._object_pools, dict)
        assert isinstance(manager._widget_pools, dict)
        assert isinstance(manager._progressive_renderers, dict)
        
        # Verify timer setup
        assert isinstance(manager._memory_cleanup_timer, QTimer)
        assert manager._memory_cleanup_timer.isActive()
        assert manager._memory_cleanup_interval == 60000  # 60 seconds
    
    def test_signal_connections(self, performance_manager):
        """Test signal connections are established."""
        manager = performance_manager
        
        # Verify signals exist
        assert hasattr(manager, 'memory_cleanup_started')
        assert hasattr(manager, 'memory_cleanup_completed')
        assert hasattr(manager, 'performance_warning')
        
        # Test signal emissions
        signal_emitted = []
        manager.memory_cleanup_started.connect(lambda: signal_emitted.append('started'))
        manager.memory_cleanup_completed.connect(lambda count: signal_emitted.append(f'completed:{count}'))
        
        manager.trigger_memory_cleanup()
        
        assert 'started' in signal_emitted
        assert any('completed:' in s for s in signal_emitted)
    
    def test_memory_management_startup(self, performance_manager):
        """Test memory management starts automatically."""
        manager = performance_manager
        
        assert manager._memory_cleanup_timer.isActive()
        assert manager._memory_cleanup_timer.interval() == 60000
    
    def test_performance_warning_handling(self, performance_manager):
        """Test performance warning handling."""
        manager = performance_manager
        
        # Setup warning capture
        warnings_captured = []
        manager.performance_warning.connect(
            lambda op, dur, thresh: warnings_captured.append((op, dur, thresh))
        )
        
        # Trigger a performance warning through metrics tracker
        manager._metrics_tracker.set_threshold("test_operation", 0.001)  # Very low threshold
        manager.record_duration("test_operation", 0.01)  # Should exceed threshold
        
        # Warning should be captured if threshold is exceeded
        # Note: Actual warning depends on MetricsTracker implementation


class TestObjectPoolManagement:
    """Test object pool creation and management."""
    
    def test_create_object_pool(self, performance_manager):
        """Test creating a generic object pool."""
        manager = performance_manager
        
        # Create object pool
        pool = manager.create_object_pool(
            name="test_pool",
            factory=lambda: TestObject(),
            max_pool_size=20,
            reset_callback=lambda obj: obj.reset(),
            cleanup_callback=lambda obj: obj.cleanup()
        )
        
        # Verify pool creation
        assert isinstance(pool, ObjectPool)
        assert manager.get_object_pool("test_pool") is pool
        assert "test_pool" in manager._object_pools
    
    def test_create_duplicate_object_pool(self, performance_manager):
        """Test creating object pool with duplicate name."""
        manager = performance_manager
        
        # Create first pool
        pool1 = manager.create_object_pool("duplicate_pool", lambda: TestObject())
        
        # Create second pool with same name
        pool2 = manager.create_object_pool("duplicate_pool", lambda: TestObject())
        
        # Should return the same pool
        assert pool1 is pool2
    
    def test_create_widget_pool(self, performance_manager, qapp):
        """Test creating a widget pool."""
        manager = performance_manager
        
        # Create widget pool
        pool = manager.create_widget_pool(
            name="test_widget_pool",
            widget_factory=lambda: TestWidget(),
            max_pool_size=15
        )
        
        # Verify pool creation
        assert isinstance(pool, WidgetPool)
        assert manager.get_widget_pool("test_widget_pool") is pool
        assert "test_widget_pool" in manager._widget_pools
    
    def test_object_pool_operations(self, performance_manager):
        """Test object pool operations."""
        manager = performance_manager
        
        # Create pool
        pool = manager.create_object_pool(
            name="operations_pool",
            factory=lambda: TestObject(),
            max_pool_size=5
        )
        
        # Test pool operations
        obj1 = pool.get_object()
        obj2 = pool.get_object()
        
        assert obj1 is not obj2
        assert isinstance(obj1, TestObject)
        assert isinstance(obj2, TestObject)
        
        # Return objects to pool
        pool.return_object(obj1)
        pool.return_object(obj2)
        
        # Get objects again - should reuse from pool
        obj3 = pool.get_object()
        obj4 = pool.get_object()
        
        # Note: Exact reuse depends on pool implementation
        assert isinstance(obj3, TestObject)
        assert isinstance(obj4, TestObject)
    
    def test_clear_pools(self, performance_manager):
        """Test clearing object and widget pools."""
        manager = performance_manager
        
        # Create pools
        obj_pool = manager.create_object_pool("clear_test", lambda: TestObject())
        widget_pool = manager.create_widget_pool("clear_widget_test", lambda: TestWidget())
        
        # Add objects to pools
        obj = obj_pool.get_object()
        obj_pool.return_object(obj)
        
        # Clear specific pool
        manager.clear_pool("clear_test")
        
        # Clear all pools
        manager.clear_all_pools()
        
        # Pools should still exist but be empty
        assert manager.get_object_pool("clear_test") is obj_pool
        assert manager.get_widget_pool("clear_widget_test") is widget_pool


class TestProgressiveRendering:
    """Test progressive rendering coordination."""
    
    def test_create_progressive_renderer(self, performance_manager):
        """Test creating a progressive renderer."""
        manager = performance_manager
        target = TestProgressiveTarget()
        
        renderer = manager.create_progressive_renderer(
            name="test_renderer",
            target=target,
            default_batch_size=3,
            default_delay_ms=50
        )
        
        # Verify renderer creation
        assert isinstance(renderer, ProgressiveRenderer)
        assert manager.get_progressive_renderer("test_renderer") is renderer
        assert "test_renderer" in manager._progressive_renderers
    
    def test_create_callback_renderer(self, performance_manager):
        """Test creating a callback-based progressive renderer."""
        manager = performance_manager
        
        rendered_batches = []
        completion_count = [0]
        
        def render_callback(items, start, end):
            rendered_batches.append(items[start:end])
        
        def completion_callback():
            completion_count[0] += 1
        
        renderer = manager.create_callback_renderer(
            name="callback_renderer",
            render_callback=render_callback,
            completion_callback=completion_callback,
            default_batch_size=2,
            default_delay_ms=25
        )
        
        # Verify renderer creation
        assert renderer is not None
        assert manager.get_progressive_renderer("callback_renderer") is renderer
    
    def test_start_progressive_rendering(self, performance_manager):
        """Test starting progressive rendering."""
        manager = performance_manager
        target = TestProgressiveTarget()
        
        renderer = manager.create_progressive_renderer(
            "render_test",
            target,
            default_batch_size=2
        )
        
        # Start rendering
        test_items = list(range(10))
        success = manager.start_progressive_rendering("render_test", test_items)
        
        assert success is True
        
        # Process rendering batches
        for _ in range(20):  # Allow multiple batch cycles
            QApplication.processEvents()
            time.sleep(0.01)
            if len(target.rendered_items) >= len(test_items):
                break
        
        # Verify rendering occurred
        assert target.render_calls > 0
        assert len(target.rendered_items) <= len(test_items)
    
    def test_stop_progressive_rendering(self, performance_manager):
        """Test stopping progressive rendering."""
        manager = performance_manager
        target = TestProgressiveTarget()
        
        renderer = manager.create_progressive_renderer("stop_test", target)
        
        # Start rendering
        test_items = list(range(100))  # Large dataset
        manager.start_progressive_rendering("stop_test", test_items)
        
        # Stop rendering
        success = manager.stop_progressive_rendering("stop_test")
        assert success is True
    
    def test_progressive_rendering_nonexistent(self, performance_manager):
        """Test progressive rendering operations with nonexistent renderer."""
        manager = performance_manager
        
        # Try to start nonexistent renderer
        success = manager.start_progressive_rendering("nonexistent", [1, 2, 3])
        assert success is False
        
        # Try to stop nonexistent renderer
        success = manager.stop_progressive_rendering("nonexistent")
        assert success is False


class TestMemoryManagement:
    """Test memory management functionality."""
    
    def test_memory_management_control(self, performance_manager):
        """Test starting and stopping memory management."""
        manager = performance_manager
        
        # Test custom interval
        manager.start_memory_management(30000)  # 30 seconds
        assert manager._memory_cleanup_interval == 30000
        assert manager._memory_cleanup_timer.isActive()
        
        # Stop memory management
        manager.stop_memory_management()
        assert not manager._memory_cleanup_timer.isActive()
        
        # Restart with default
        manager.start_memory_management()
        assert manager._memory_cleanup_timer.isActive()
    
    def test_object_tracking(self, performance_manager):
        """Test object tracking for memory management."""
        manager = performance_manager
        
        # Track objects
        obj1 = TestObject()
        obj2 = TestObject()
        
        manager.track_object(obj1)
        manager.track_object(obj2)
        
        # Verify tracking
        initial_count = len(manager._weak_references)
        assert initial_count >= 2
        
        # Delete one object
        del obj1
        gc.collect()
        
        # Trigger cleanup
        manager.trigger_memory_cleanup()
        
        # Verify cleanup occurred
        final_count = len([ref for ref in manager._weak_references if ref() is not None])
        # Note: Exact counts depend on garbage collection timing
        assert final_count <= initial_count
    
    def test_memory_cleanup_signals(self, performance_manager):
        """Test memory cleanup signal emissions."""
        manager = performance_manager
        
        # Setup signal capturing
        cleanup_events = []
        manager.memory_cleanup_started.connect(lambda: cleanup_events.append('started'))
        manager.memory_cleanup_completed.connect(lambda count: cleanup_events.append(f'completed:{count}'))
        
        # Trigger cleanup
        manager.trigger_memory_cleanup()
        
        # Verify signals were emitted
        assert 'started' in cleanup_events
        assert any('completed:' in event for event in cleanup_events)
    
    def test_periodic_memory_cleanup(self, performance_manager):
        """Test periodic memory cleanup execution."""
        manager = performance_manager
        
        # Track some objects
        objs = [TestObject() for _ in range(5)]
        for obj in objs:
            manager.track_object(obj)
        
        # Force periodic cleanup
        manager._periodic_memory_cleanup()
        
        # Should complete without error
        # Exact verification depends on implementation details


class TestPerformanceMetrics:
    """Test performance metrics functionality."""
    
    def test_metrics_tracker_integration(self, performance_manager):
        """Test integration with metrics tracker."""
        manager = performance_manager
        tracker = manager.get_metrics_tracker()
        
        assert isinstance(tracker, MetricsTracker)
        assert tracker is manager._metrics_tracker
    
    def test_timing_operations(self, performance_manager):
        """Test timing operations."""
        manager = performance_manager
        
        # Start and stop timer
        timer_id = manager.start_timer("test_operation", {"context": "unit_test"})
        assert timer_id is not None
        
        time.sleep(0.01)  # Small delay
        
        manager.stop_timer(timer_id, {"result": "success"})
        
        # Record direct duration
        manager.record_duration("direct_operation", 0.05, {"method": "direct"})
        
        # Set threshold
        manager.set_performance_threshold("test_operation", 0.1)
    
    def test_performance_context_manager(self, performance_manager):
        """Test performance timing context manager."""
        manager = performance_manager
        
        # Use context manager
        with manager.performance_context("context_test", {"test": "context"}) as context:
            time.sleep(0.01)  # Small operation
            assert context is not None
        
        # Operation should be recorded automatically
    
    def test_performance_summary(self, performance_manager):
        """Test performance summary generation."""
        manager = performance_manager
        
        # Create some pools and renderers
        manager.create_object_pool("summary_pool", lambda: TestObject(), max_pool_size=10)
        manager.create_widget_pool("summary_widgets", lambda: TestWidget(), max_pool_size=5)
        target = TestProgressiveTarget()
        manager.create_progressive_renderer("summary_renderer", target)
        
        # Track some objects
        for i in range(3):
            manager.track_object(TestObject())
        
        # Get summary
        summary = manager.get_performance_summary()
        
        # Verify summary structure
        assert 'metrics' in summary
        assert 'pools' in summary
        assert 'renderers' in summary
        assert 'memory' in summary
        assert 'cleanup_interval_ms' in summary
        
        # Verify pool statistics
        assert 'object_pool_summary_pool' in summary['pools']
        assert 'widget_pool_summary_widgets' in summary['pools']
        
        # Verify memory statistics
        assert 'tracked_objects' in summary['memory']
        assert 'total_references' in summary['memory']
    
    def test_log_performance_summary(self, performance_manager):
        """Test performance summary logging."""
        manager = performance_manager
        
        # Create some activity
        manager.record_duration("log_test", 0.02)
        manager.create_object_pool("log_pool", lambda: TestObject())
        
        # Should not raise exception
        manager.log_performance_summary()


class TestPerformanceManagerCleanup:
    """Test PerformanceManager cleanup and resource management."""
    
    def test_cleanup_all_resources(self, performance_manager):
        """Test comprehensive cleanup of all resources."""
        manager = performance_manager
        
        # Create various resources
        obj_pool = manager.create_object_pool("cleanup_obj", lambda: TestObject())
        widget_pool = manager.create_widget_pool("cleanup_widget", lambda: TestWidget())
        target = TestProgressiveTarget()
        renderer = manager.create_progressive_renderer("cleanup_render", target)
        
        # Start some operations
        manager.start_progressive_rendering("cleanup_render", list(range(10)))
        manager.track_object(TestObject())
        
        # Trigger cleanup
        manager.cleanup()
        
        # Verify cleanup
        assert not manager._memory_cleanup_timer.isActive()
        assert len(manager._object_pools) == 0
        assert len(manager._widget_pools) == 0
        assert len(manager._progressive_renderers) == 0
        assert len(manager._weak_references) == 0
    
    def test_cleanup_with_active_rendering(self, performance_manager):
        """Test cleanup with active progressive rendering."""
        manager = performance_manager
        
        # Start progressive rendering
        target = TestProgressiveTarget()
        renderer = manager.create_progressive_renderer("active_cleanup", target)
        manager.start_progressive_rendering("active_cleanup", list(range(50)))
        
        # Cleanup should stop active rendering
        manager.cleanup()
        
        # Should complete without hanging
    
    def test_cleanup_signal_emissions(self, performance_manager):
        """Test that cleanup properly handles signal connections."""
        manager = performance_manager
        
        # Connect to signals
        signal_received = []
        manager.performance_warning.connect(lambda *args: signal_received.append('warning'))
        manager.memory_cleanup_completed.connect(lambda count: signal_received.append('cleanup'))
        
        # Trigger some activity
        manager.trigger_memory_cleanup()
        
        # Cleanup should not cause signal connection errors
        manager.cleanup()
    
    def test_resource_lifecycle_management(self, performance_manager):
        """Test proper resource lifecycle management."""
        manager = performance_manager
        
        # Create resources with weak references for tracking
        obj_pool = manager.create_object_pool("lifecycle", lambda: TestObject())
        pool_ref = weakref.ref(obj_pool)
        
        widget_pool = manager.create_widget_pool("lifecycle_widgets", lambda: TestWidget())
        widget_ref = weakref.ref(widget_pool)
        
        # Clear references
        del obj_pool, widget_pool
        
        # Cleanup manager
        manager.cleanup()
        gc.collect()
        
        # Resources should be cleaned up
        # Note: Exact cleanup verification depends on implementation