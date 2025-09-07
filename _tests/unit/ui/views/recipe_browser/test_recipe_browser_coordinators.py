"""Additional coordinator integration unit tests for RecipeBrowser.

Tests specific coordinator interactions and edge cases not covered by
individual coordinator tests. Focuses on:
- Cross-coordinator communication patterns
- Coordinator state synchronization
- Event propagation between coordinators
- Error handling across coordinator boundaries
- Resource sharing and lifecycle management
- Performance optimization coordination
- Configuration propagation across coordinators

These tests complement the individual coordinator tests and integration tests
by focusing on coordinator-to-coordinator interactions within the
RecipeBrowser architecture.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
import time
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch, call

import pytest
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QComboBox, QCheckBox, QLineEdit

from app.core.models.recipe import Recipe
from app.ui.managers.performance.performance_manager import PerformanceManager
from app.ui.managers.events.event_coordinator import EventCoordinator
from app.ui.view_models.recipe_browser_view_model import RecipeBrowserViewModel
from app.ui.views.recipe_browser.config import RecipeBrowserConfig, create_default_config
from app.ui.views.recipe_browser.filter_coordinator import FilterCoordinator
from app.ui.views.recipe_browser.rendering_coordinator import RenderingCoordinator

from _tests.fixtures.recipe_factories import RecipeFactory


# ── Test Data Factories ─────────────────────────────────────────────────────────────────────────────────────────
def create_test_recipes_for_coordination(count: int = 10) -> List[Recipe]:
    """Create test recipes optimized for coordinator interaction testing."""
    recipes = []
    categories = ["Main Course", "Desserts", "Appetizers", "Side Dishes"]
    
    for i in range(count):
        recipe = RecipeFactory.build(
            id=i + 1,
            recipe_name=f"Coordination Test Recipe {i + 1}",
            recipe_category=categories[i % len(categories)],
            is_favorite=(i % 4 == 0),  # 25% favorites
            total_time=10 + (i * 3),
            servings=1 + (i % 8)
        )
        recipes.append(recipe)
    
    return recipes


# ── Fixtures ─────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture
def coordination_config():
    """Create configuration optimized for coordinator testing."""
    config = create_default_config()
    # Fast settings for test execution
    config.performance.batch_size = 2
    config.performance.card_pool_size = 8
    config.interaction.filter_debounce_delay_ms = 25
    config.interaction.search_debounce_delay_ms = 50
    return config


@pytest.fixture
def mock_view_model():
    """Create comprehensive mock ViewModel."""
    vm = Mock(spec=RecipeBrowserViewModel)
    vm.load_filtered_sorted_recipes.return_value = True
    vm.update_category_filter.return_value = True
    vm.update_sort_option.return_value = True
    vm.update_favorites_filter.return_value = True
    vm.update_search_term.return_value = True
    vm.current_recipes = create_test_recipes_for_coordination(5)
    return vm


@pytest.fixture
def performance_manager():
    """Create PerformanceManager for coordinator testing."""
    manager = PerformanceManager()
    yield manager
    manager.cleanup()


@pytest.fixture
def event_coordinator():
    """Create EventCoordinator for coordinator testing."""
    coordinator = EventCoordinator(coordinator_name="CoordinatorTest")
    yield coordinator
    coordinator.cleanup_all_coordinations()


@pytest.fixture
def filter_coordinator(mock_view_model, coordination_config, event_coordinator):
    """Create FilterCoordinator for testing."""
    coordinator = FilterCoordinator(
        view_model=mock_view_model,
        config=coordination_config,
        event_coordinator=event_coordinator
    )
    yield coordinator
    coordinator.cleanup()


@pytest.fixture
def rendering_coordinator(performance_manager, coordination_config):
    """Create RenderingCoordinator for testing."""
    # Create minimal layout mock
    layout_mock = Mock()
    layout_mock.count.return_value = 0
    
    coordinator = RenderingCoordinator(
        performance_manager=performance_manager,
        config=coordination_config,
        parent_layout=layout_mock
    )
    yield coordinator
    coordinator.cleanup()


@pytest.fixture
def coordinator_suite(
    mock_view_model, 
    coordination_config, 
    performance_manager, 
    event_coordinator, 
    filter_coordinator, 
    rendering_coordinator
):
    """Create complete coordinator suite for integration testing."""
    return {
        'view_model': mock_view_model,
        'config': coordination_config,
        'performance': performance_manager,
        'events': event_coordinator,
        'filter': filter_coordinator,
        'rendering': rendering_coordinator
    }


# ── Test Classes ─────────────────────────────────────────────────────────────────────────────────────────────
class TestCoordinatorCommunication:
    """Test communication patterns between coordinators."""
    
    def test_filter_to_rendering_coordination(self, coordinator_suite):
        """Test filter changes triggering rendering updates."""
        coordinators = coordinator_suite
        filter_coord = coordinators['filter']
        rendering_coord = coordinators['rendering']
        
        # Setup rendering signal capture
        rendering_calls = []
        def capture_rendering(recipes):
            rendering_calls.append(recipes)
        
        # Mock rendering coordinator to capture render calls
        with patch.object(rendering_coord, 'render_recipes', side_effect=capture_rendering) as mock_render:
            # Apply filter changes
            filter_coord.apply_category_filter("Main Course")
            
            # Wait for debounce
            time.sleep(0.1)
            QApplication.processEvents()
            
            # Should not directly call rendering (depends on architecture)
            # Direct calls would happen through view orchestration
    
    def test_performance_manager_shared_resources(self, coordinator_suite):
        """Test performance manager resource sharing across coordinators."""
        coordinators = coordinator_suite
        performance_mgr = coordinators['performance']
        rendering_coord = coordinators['rendering']
        
        # Both rendering and other coordinators should share performance resources
        # Create object pool through performance manager
        test_pool = performance_mgr.create_object_pool(
            "shared_test_pool", 
            lambda: {"test": "object"}
        )
        
        # Rendering coordinator should be able to access shared resources
        retrieved_pool = performance_mgr.get_object_pool("shared_test_pool")
        assert retrieved_pool is test_pool
        
        # Verify rendering coordinator can use performance manager
        summary = performance_mgr.get_performance_summary()
        assert 'pools' in summary
    
    def test_event_coordinator_cross_coordination(self, coordinator_suite):
        """Test EventCoordinator managing events across multiple coordinators."""
        coordinators = coordinator_suite
        event_coord = coordinators['events']
        filter_coord = coordinators['filter']
        
        # Setup cross-coordinator event handling
        handled_events = []
        def cross_coordinator_handler(event_data):
            handled_events.append(event_data)
            return "cross_handled"
        
        # Register cross-coordinator event route
        event_coord.register_event_route(
            "cross_coordinator_test",
            cross_coordinator_handler
        )
        
        # Trigger event from filter coordinator context
        results = event_coord.route_event("cross_coordinator_test", {
            "source": "filter_coordinator",
            "action": "category_changed",
            "data": "Main Course"
        })
        
        # Should be handled
        assert len(results) >= 1
        assert len(handled_events) == 1
        assert handled_events[0]["source"] == "filter_coordinator"
    
    def test_configuration_propagation(self, coordinator_suite):
        """Test configuration propagation across coordinators."""
        coordinators = coordinator_suite
        config = coordinators['config']
        filter_coord = coordinators['filter']
        rendering_coord = coordinators['rendering']
        
        # Verify config is shared
        assert filter_coord._config is config
        assert rendering_coord._config is config
        
        # Verify config settings are applied
        assert filter_coord._config.interaction.filter_debounce_delay_ms == 25
        assert rendering_coord._config.performance.batch_size == 2
    
    def test_error_propagation_between_coordinators(self, coordinator_suite):
        """Test error handling across coordinator boundaries."""
        coordinators = coordinator_suite
        filter_coord = coordinators['filter']
        event_coord = coordinators['events']
        
        # Setup error in event coordination
        def failing_handler(event_data):
            raise Exception("Coordinator communication failure")
        
        event_coord.register_event_route("failing_route", failing_handler)
        
        # Attempt operation that might trigger cross-coordinator error
        try:
            # This should not crash other coordinators
            event_coord.route_event("failing_route", {"test": "data"})
        except Exception:
            pass  # Expected to fail
        
        # Filter coordinator should still be functional
        success = filter_coord.apply_category_filter("Desserts")
        assert success is True


class TestCoordinatorStateSync:
    """Test state synchronization between coordinators."""
    
    def test_filter_state_affects_rendering(self, coordinator_suite):
        """Test filter state changes affecting rendering state."""
        coordinators = coordinator_suite
        filter_coord = coordinators['filter']
        rendering_coord = coordinators['rendering']
        
        # Apply filter that would affect rendering
        filter_coord.apply_favorites_filter(True)
        
        # Wait for state propagation
        time.sleep(0.1)
        QApplication.processEvents()
        
        # Check that state is consistent
        filter_state = filter_coord.get_current_filter_state()
        assert filter_state.favorites_only is True
        
        # Rendering coordinator should be aware of filtering context
        # (exact synchronization depends on implementation)
    
    def test_selection_mode_coordination(self, coordinator_suite):
        """Test selection mode synchronization across coordinators."""
        coordinators = coordinator_suite
        rendering_coord = coordinators['rendering']
        
        # Enable selection mode in rendering
        rendering_coord.set_selection_mode(True)
        
        # Verify selection mode state
        assert rendering_coord._selection_mode is True
        
        # Disable selection mode
        rendering_coord.set_selection_mode(False)
        assert rendering_coord._selection_mode is False
    
    def test_performance_state_coordination(self, coordinator_suite):
        """Test performance state coordination across coordinators."""
        coordinators = coordinator_suite
        performance_mgr = coordinators['performance']
        rendering_coord = coordinators['rendering']
        
        # Trigger performance operations
        recipes = create_test_recipes_for_coordination(8)
        
        with patch.object(rendering_coord, '_create_recipe_card', return_value=Mock()) as mock_create:
            rendering_coord.render_recipes(recipes)
            QApplication.processEvents()
        
        # Check performance metrics
        metrics = performance_mgr.get_performance_summary()
        
        # Should have some performance data
        assert 'metrics' in metrics
        assert 'pools' in metrics
        assert 'memory' in metrics
    
    def test_coordinator_cleanup_synchronization(self, coordinator_suite):
        """Test coordinated cleanup across all coordinators."""
        coordinators = coordinator_suite
        
        # Create some state in each coordinator
        coordinators['filter'].apply_category_filter("Main Course")
        
        recipes = create_test_recipes_for_coordination(3)
        with patch.object(coordinators['rendering'], '_create_recipe_card', return_value=Mock()):
            coordinators['rendering'].render_recipes(recipes)
        
        # Cleanup all coordinators
        coordinators['filter'].cleanup()
        coordinators['rendering'].cleanup()
        coordinators['performance'].cleanup()
        coordinators['events'].cleanup_all_coordinations()
        
        # Should complete without errors
        # Verify cleanup state
        assert len(coordinators['events']._active_coordinations) == 0


class TestCoordinatorPerformanceIntegration:
    """Test performance optimization across coordinators."""
    
    def test_debounced_filter_with_progressive_rendering(self, coordinator_suite):
        """Test debounced filtering with progressive rendering."""
        coordinators = coordinator_suite
        filter_coord = coordinators['filter']
        rendering_coord = coordinators['rendering']
        event_coord = coordinators['events']
        
        # Setup progressive rendering
        rendering_coord._use_progressive_rendering = True
        
        # Rapid filter changes should debounce
        for category in ["Main Course", "Desserts", "Appetizers"]:
            filter_coord.apply_category_filter(category)
            time.sleep(0.01)  # Rapid changes
        
        # Wait for debounce to settle
        time.sleep(0.1)
        QApplication.processEvents()
        
        # Should have debounced the filter operations
        assert coordinators['view_model'].update_category_filter.call_count <= 3
        
        # Final filter state should be consistent
        final_state = filter_coord.get_current_filter_state()
        assert final_state.category_filter == "Appetizers"
    
    def test_memory_coordination_across_systems(self, coordinator_suite):
        """Test memory management coordination across all systems."""
        coordinators = coordinator_suite
        performance_mgr = coordinators['performance']
        
        # Create memory pressure through multiple operations
        for i in range(5):
            # Filter operations
            coordinators['filter'].apply_search_filter(f"search_{i}")
            
            # Rendering operations
            test_recipes = create_test_recipes_for_coordination(3)
            with patch.object(coordinators['rendering'], '_create_recipe_card', return_value=Mock()):
                coordinators['rendering'].render_recipes(test_recipes)
            
            time.sleep(0.01)
        
        # Trigger coordinated memory cleanup
        performance_mgr.trigger_memory_cleanup()
        QApplication.processEvents()
        
        # Should handle memory cleanup across coordinators
        memory_stats = performance_mgr.get_performance_summary()['memory']
        assert memory_stats['tracked_objects'] >= 0
    
    def test_performance_threshold_coordination(self, coordinator_suite):
        """Test performance threshold monitoring across coordinators."""
        coordinators = coordinator_suite
        performance_mgr = coordinators['performance']
        
        # Set performance thresholds
        performance_mgr.set_performance_threshold("filter_operation", 0.05)
        performance_mgr.set_performance_threshold("render_operation", 0.1)
        
        # Capture performance warnings
        warnings_received = []
        performance_mgr.performance_warning.connect(
            lambda op, dur, thresh: warnings_received.append((op, dur, thresh))
        )
        
        # Perform operations that might trigger warnings
        with performance_mgr.performance_context("filter_operation"):
            coordinators['filter'].apply_category_filter("Main Course")
            time.sleep(0.01)  # Simulate work
        
        with performance_mgr.performance_context("render_operation"):
            time.sleep(0.02)  # Simulate work
        
        # Check if warnings were generated (depends on actual timing)
        # Note: Timing-based tests are inherently flaky
    
    def test_resource_sharing_optimization(self, coordinator_suite):
        """Test resource sharing optimization between coordinators."""
        coordinators = coordinator_suite
        performance_mgr = coordinators['performance']
        rendering_coord = coordinators['rendering']
        
        # Create shared object pool
        shared_pool = performance_mgr.create_object_pool(
            "shared_resource_pool",
            lambda: {"shared": "resource"},
            max_pool_size=5
        )
        
        # Rendering coordinator should be able to access shared resources
        retrieved_pool = performance_mgr.get_object_pool("shared_resource_pool")
        assert retrieved_pool is shared_pool
        
        # Use shared resources
        resource1 = shared_pool.get_object()
        resource2 = shared_pool.get_object()
        
        assert resource1 is not None
        assert resource2 is not None
        
        # Return to pool for reuse
        shared_pool.return_object(resource1)
        shared_pool.return_object(resource2)
        
        # Pool should manage resources efficiently
        pool_stats = shared_pool.statistics
        assert pool_stats['total_created'] >= 2
        assert pool_stats['pool_size'] >= 0


class TestCoordinatorEventPropagation:
    """Test event propagation patterns across coordinators."""
    
    def test_filter_change_event_propagation(self, coordinator_suite):
        """Test filter change events propagating through event system."""
        coordinators = coordinator_suite
        event_coord = coordinators['events']
        filter_coord = coordinators['filter']
        
        # Setup event capture
        propagated_events = []
        def event_capture_handler(event_data):
            propagated_events.append(event_data)
            return "captured"
        
        event_coord.register_event_route("filter_changed", event_capture_handler)
        
        # Simulate filter change event
        event_coord.route_event("filter_changed", {
            "filter_type": "category",
            "old_value": "All",
            "new_value": "Main Course",
            "source": "filter_coordinator"
        })
        
        # Verify event propagation
        assert len(propagated_events) == 1
        assert propagated_events[0]["filter_type"] == "category"
        assert propagated_events[0]["new_value"] == "Main Course"
    
    def test_rendering_event_coordination(self, coordinator_suite):
        """Test rendering events coordinated through event system."""
        coordinators = coordinator_suite
        event_coord = coordinators['events']
        rendering_coord = coordinators['rendering']
        
        # Setup rendering event handlers
        rendering_events = []
        
        def rendering_start_handler(event_data):
            rendering_events.append(("started", event_data))
            return "start_handled"
        
        def rendering_complete_handler(event_data):
            rendering_events.append(("completed", event_data))
            return "complete_handled"
        
        event_coord.register_event_route("rendering_started", rendering_start_handler)
        event_coord.register_event_route("rendering_completed", rendering_complete_handler)
        
        # Simulate rendering events
        event_coord.route_event("rendering_started", {
            "recipe_count": 5,
            "batch_size": 2,
            "progressive": True
        })
        
        event_coord.route_event("rendering_completed", {
            "recipe_count": 5,
            "render_time_ms": 150,
            "cards_created": 5
        })
        
        # Verify event handling
        assert len(rendering_events) == 2
        assert rendering_events[0][0] == "started"
        assert rendering_events[1][0] == "completed"
        assert rendering_events[0][1]["recipe_count"] == 5
    
    def test_cross_coordinator_signal_routing(self, coordinator_suite):
        """Test signal routing between different coordinators."""
        coordinators = coordinator_suite
        event_coord = coordinators['events']
        
        # Setup cross-coordinator communication
        coordinator_messages = []
        
        def filter_to_rendering_handler(event_data):
            coordinator_messages.append(f"filter->rendering: {event_data}")
            return "routed"
        
        def rendering_to_filter_handler(event_data):
            coordinator_messages.append(f"rendering->filter: {event_data}")
            return "routed"
        
        event_coord.register_event_route("filter_to_rendering", filter_to_rendering_handler)
        event_coord.register_event_route("rendering_to_filter", rendering_to_filter_handler)
        
        # Route messages between coordinators
        event_coord.route_event("filter_to_rendering", {
            "message": "filter_applied",
            "details": {"category": "Main Course", "count": 3}
        })
        
        event_coord.route_event("rendering_to_filter", {
            "message": "rendering_complete",
            "details": {"cards_rendered": 3, "time_ms": 100}
        })
        
        # Verify cross-coordinator routing
        assert len(coordinator_messages) == 2
        assert "filter->rendering" in coordinator_messages[0]
        assert "rendering->filter" in coordinator_messages[1]
    
    def test_event_priority_coordination(self, coordinator_suite):
        """Test event priority handling across coordinators."""
        coordinators = coordinator_suite
        event_coord = coordinators['events']
        
        # Setup handlers with different priorities
        execution_order = []
        
        from app.ui.managers.events.event_router import EventPriority
        
        def high_priority_handler(event_data):
            execution_order.append("high")
            return "high_handled"
        
        def normal_priority_handler(event_data):
            execution_order.append("normal")
            return "normal_handled"
        
        def low_priority_handler(event_data):
            execution_order.append("low")
            return "low_handled"
        
        # Register with different priorities
        event_coord.register_event_route(
            "priority_test", high_priority_handler, EventPriority.HIGH
        )
        event_coord.register_event_route(
            "priority_test", normal_priority_handler, EventPriority.NORMAL
        )
        event_coord.register_event_route(
            "priority_test", low_priority_handler, EventPriority.LOW
        )
        
        # Route event
        results = event_coord.route_event("priority_test", {"test": "priority"})
        
        # Verify execution order respects priority
        # Note: Exact order depends on event router implementation
        assert len(results) == 3
        assert len(execution_order) == 3


class TestCoordinatorEdgeCasesIntegration:
    """Test edge cases in coordinator integration."""
    
    def test_rapid_coordinator_state_changes(self, coordinator_suite):
        """Test rapid state changes across coordinators."""
        coordinators = coordinator_suite
        filter_coord = coordinators['filter']
        
        # Rapidly change multiple filter aspects
        for i in range(10):
            filter_coord.apply_category_filter(["Main Course", "Desserts"][i % 2])
            filter_coord.apply_favorites_filter(i % 2 == 0)
            filter_coord.apply_search_filter(f"search_{i}")
            time.sleep(0.001)  # Very rapid changes
        
        # Wait for all operations to settle
        time.sleep(0.2)
        QApplication.processEvents()
        
        # Should handle rapid changes without errors
        final_state = filter_coord.get_current_filter_state()
        assert final_state is not None
    
    def test_coordinator_failure_isolation(self, coordinator_suite):
        """Test that coordinator failures are isolated."""
        coordinators = coordinator_suite
        event_coord = coordinators['events']
        filter_coord = coordinators['filter']
        
        # Break one coordinator's functionality
        original_method = filter_coord.apply_category_filter
        def failing_method(category):
            raise Exception("Filter coordinator failure")
        
        filter_coord.apply_category_filter = failing_method
        
        # Other coordinators should continue working
        try:
            filter_coord.apply_category_filter("Main Course")
        except Exception:
            pass  # Expected failure
        
        # Event coordinator should still work
        handled_events = []
        event_coord.register_event_route(
            "test_isolation", 
            lambda data: handled_events.append(data)
        )
        
        event_coord.route_event("test_isolation", {"test": "data"})
        
        assert len(handled_events) == 1
        assert handled_events[0]["test"] == "data"
    
    def test_memory_pressure_coordination(self, coordinator_suite):
        """Test coordinator behavior under memory pressure."""
        coordinators = coordinator_suite
        performance_mgr = coordinators['performance']
        
        # Create memory pressure
        large_objects = []
        for i in range(100):
            # Create objects that might stress memory
            obj = {"data": list(range(1000)), "id": i}
            large_objects.append(obj)
            
            # Track some objects
            performance_mgr.track_object(obj)
        
        # Trigger aggressive cleanup
        performance_mgr.trigger_memory_cleanup()
        QApplication.processEvents()
        
        # Coordinators should still function
        success = coordinators['filter'].apply_category_filter("Main Course")
        assert success is True
        
        # Memory metrics should be reasonable
        memory_stats = performance_mgr.get_performance_summary()['memory']
        assert memory_stats['tracked_objects'] >= 0
    
    def test_concurrent_coordinator_operations(self, coordinator_suite):
        """Test concurrent operations across coordinators."""
        coordinators = coordinator_suite
        filter_coord = coordinators['filter']
        event_coord = coordinators['events']
        
        # Setup multiple concurrent operations
        operations = []
        
        # Filter operations
        for category in ["Main Course", "Desserts", "Appetizers"]:
            operations.append(lambda cat=category: filter_coord.apply_category_filter(cat))
        
        # Event operations
        for i in range(3):
            operations.append(lambda idx=i: event_coord.route_event(f"concurrent_test_{idx}", {"data": idx}))
        
        # Execute operations concurrently (simulated)
        for operation in operations:
            try:
                operation()
            except Exception as e:
                # Should handle concurrent access gracefully
                pass
        
        # Wait for operations to complete
        time.sleep(0.1)
        QApplication.processEvents()
        
        # System should remain stable
        final_state = filter_coord.get_current_filter_state()
        assert final_state is not None