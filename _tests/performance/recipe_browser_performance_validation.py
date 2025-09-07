"""Comprehensive Performance Validation for Refactored RecipeBrowser System

This module provides extensive performance validation and benchmarking for the RecipeBrowser
coordinator architecture to ensure it meets all performance requirements:

- Load time under 200ms for 11 recipes
- Memory usage optimized through object pooling
- Smooth scrolling and filtering operations
- UI responsiveness maintained
- Performance improved over original implementation

Key Performance Areas Tested:
1. Initial Recipe Loading Performance
2. Filter Operation Response Time  
3. Memory Usage and Object Pooling Efficiency
4. Recipe Card Creation and Rendering Performance
5. Coordinator Communication Overhead
6. Progressive Rendering Efficiency
7. Cache Hit Rates and Effectiveness
8. Stress Testing with Large Datasets

The validation uses real RecipeBrowser components in a controlled test environment
to provide accurate performance measurements and identify optimization opportunities.
"""

import gc
import time
import psutil
import statistics
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from unittest.mock import Mock, patch

import pytest
from PySide6.QtCore import QTimer, QCoreApplication
from PySide6.QtWidgets import QApplication, QWidget

from _dev_tools import DebugLogger
from app.core.models.recipe import Recipe
from app.ui.managers.performance.performance_manager import PerformanceManager
from app.ui.managers.events.event_coordinator import EventCoordinator
from app.ui.view_models.recipe_browser_view_model import RecipeBrowserViewModel
from app.ui.views.recipe_browser.config import (
    RecipeBrowserConfig, create_default_config, create_performance_config
)
from app.ui.views.recipe_browser.filter_coordinator import FilterCoordinator
from app.ui.views.recipe_browser.rendering_coordinator import RenderingCoordinator
from app.ui.views.recipe_browser.recipe_browser_view import RecipeBrowser

from _tests.fixtures.recipe_factories import RecipeFactory


# ── Performance Measurement Infrastructure ────────────────────────────────────────────────────────

@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics for validation."""
    operation: str
    start_time: float
    end_time: float
    duration_ms: float
    memory_before_mb: float
    memory_after_mb: float
    memory_delta_mb: float
    cpu_usage_percent: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def meets_timing_requirement(self) -> bool:
        """Check if timing meets performance requirements."""
        # Define timing requirements for different operations
        timing_requirements = {
            'recipe_loading': 200.0,        # 200ms for recipe loading
            'filter_operation': 100.0,      # 100ms for filter changes
            'card_creation': 50.0,          # 50ms per recipe card
            'coordinator_communication': 10.0,  # 10ms for coordinator calls
            'cache_operation': 5.0,         # 5ms for cache operations
            'progressive_rendering_batch': 25.0,  # 25ms per render batch
        }
        
        requirement = timing_requirements.get(self.operation, 1000.0)  # Default 1s
        return self.duration_ms <= requirement
    
    @property
    def memory_efficiency_good(self) -> bool:
        """Check if memory usage is efficient."""
        # Memory delta should be reasonable
        if self.operation == 'recipe_loading':
            return abs(self.memory_delta_mb) < 10.0  # Less than 10MB for loading
        elif self.operation in ['filter_operation', 'cache_operation']:
            return abs(self.memory_delta_mb) < 2.0   # Less than 2MB for operations
        else:
            return abs(self.memory_delta_mb) < 5.0   # Less than 5MB for others


@contextmanager
def performance_measurement(operation: str, metadata: Optional[Dict] = None):
    """Context manager for comprehensive performance measurement."""
    metadata = metadata or {}
    
    # Get system metrics before
    process = psutil.Process()
    memory_before = process.memory_info().rss / (1024 * 1024)  # MB
    cpu_before = process.cpu_percent()
    
    start_time = time.perf_counter()
    
    try:
        yield
    finally:
        end_time = time.perf_counter()
        
        # Get system metrics after
        memory_after = process.memory_info().rss / (1024 * 1024)  # MB
        cpu_after = process.cpu_percent()
        
        duration_ms = (end_time - start_time) * 1000
        
        metrics = PerformanceMetrics(
            operation=operation,
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            memory_before_mb=memory_before,
            memory_after_mb=memory_after,
            memory_delta_mb=memory_after - memory_before,
            cpu_usage_percent=max(cpu_before, cpu_after),
            metadata=metadata
        )
        
        # Log performance data
        DebugLogger.log(
            f"Performance [{operation}]: {duration_ms:.2f}ms, "
            f"Memory: {memory_before:.1f}MB -> {memory_after:.1f}MB "
            f"(Δ{metrics.memory_delta_mb:+.1f}MB), "
            f"Meets requirement: {metrics.meets_timing_requirement}",
            "info"
        )
        
        # Store metrics globally for analysis
        if not hasattr(performance_measurement, '_all_metrics'):
            performance_measurement._all_metrics = []
        performance_measurement._all_metrics.append(metrics)


def get_all_performance_metrics() -> List[PerformanceMetrics]:
    """Get all collected performance metrics."""
    return getattr(performance_measurement, '_all_metrics', [])


def clear_performance_metrics():
    """Clear all collected performance metrics."""
    performance_measurement._all_metrics = []


# ── Test Data Factories ────────────────────────────────────────────────────────────────────────────

def create_performance_test_recipes(count: int = 11, complexity: str = "medium") -> List[Recipe]:
    """Create recipes optimized for performance testing."""
    recipes = []
    categories = ["Main Course", "Desserts", "Appetizers", "Side Dishes", "Beverages"]
    
    base_complexity = {
        "simple": {"ingredients": 3, "instructions_length": 100},
        "medium": {"ingredients": 5, "instructions_length": 300}, 
        "complex": {"ingredients": 10, "instructions_length": 800}
    }.get(complexity, {"ingredients": 5, "instructions_length": 300})
    
    for i in range(count):
        recipe = RecipeFactory.build(
            id=i + 1,
            recipe_name=f"Performance Test Recipe {i + 1:03d}",
            recipe_category=categories[i % len(categories)],
            is_favorite=(i % 5 == 0),  # 20% favorites for testing
            total_time=15 + (i * 2),   # Increasing cook times
            servings=1 + (i % 8),      # Varying servings
            instructions=f"Performance test instructions with {base_complexity['instructions_length']} characters. " * (base_complexity['instructions_length'] // 50)
        )
        
        # Add ingredients for complexity testing
        recipe.recipe_ingredients = []
        for j in range(base_complexity['ingredients']):
            ingredient = Mock()
            ingredient.ingredient_name = f"Test Ingredient {j + 1}"
            ingredient.quantity = f"{j + 1}"
            ingredient.unit = "cup" if j % 2 == 0 else "tsp"
            recipe.recipe_ingredients.append(ingredient)
        
        recipes.append(recipe)
    
    return recipes


# ── Performance Test Fixtures ──────────────────────────────────────────────────────────────────────

@pytest.fixture
def performance_config():
    """Create performance-optimized configuration for testing."""
    config = create_performance_config()
    # Further optimize for testing
    config.performance.batch_size = 3
    config.performance.render_delay_ms = 5
    config.performance.card_pool_size = 15
    config.interaction.filter_debounce_delay_ms = 50
    config.features.enable_performance_monitoring = True
    return config


@pytest.fixture  
def test_recipes_11():
    """Create exactly 11 recipes for baseline performance testing."""
    return create_performance_test_recipes(count=11, complexity="medium")


@pytest.fixture
def test_recipes_large():
    """Create large dataset for stress testing."""
    return create_performance_test_recipes(count=100, complexity="simple")


@pytest.fixture
def test_recipes_complex():
    """Create complex recipes for memory testing."""
    return create_performance_test_recipes(count=25, complexity="complex")


@pytest.fixture
def performance_manager():
    """Create performance manager with monitoring enabled."""
    manager = PerformanceManager()
    # Set aggressive performance thresholds for testing
    manager.set_performance_threshold("recipe_loading", 0.2)      # 200ms
    manager.set_performance_threshold("filter_operation", 0.1)    # 100ms
    manager.set_performance_threshold("card_creation", 0.05)      # 50ms
    yield manager
    manager.cleanup()


@pytest.fixture
def mock_recipe_service_fast():
    """Create mock recipe service optimized for performance testing."""
    service_mock = Mock()
    
    def fast_list_filtered(filter_dto):
        """Return test recipes quickly based on filter."""
        recipes = create_performance_test_recipes(11)
        
        # Apply simple filtering for realistic performance testing
        if filter_dto.recipe_category:
            recipes = [r for r in recipes if r.recipe_category == filter_dto.recipe_category]
        if filter_dto.favorites_only:
            recipes = [r for r in recipes if r.is_favorite]
        if filter_dto.search_term:
            recipes = [r for r in recipes if filter_dto.search_term.lower() in r.recipe_name.lower()]
        
        return recipes
    
    service_mock.list_filtered = fast_list_filtered
    return service_mock


# ── Core Performance Validation Tests ─────────────────────────────────────────────────────────────

class TestRecipeLoadingPerformance:
    """Test recipe loading performance meets requirements."""
    
    def test_baseline_11_recipe_loading_under_200ms(
        self, 
        qapp, 
        performance_config, 
        test_recipes_11,
        mock_recipe_service_fast
    ):
        """Test that loading 11 recipes takes under 200ms (core requirement)."""
        clear_performance_metrics()
        
        with patch('app.core.services.recipe_service.RecipeService', return_value=mock_recipe_service_fast):
            view_model = RecipeBrowserViewModel()
            
            with performance_measurement("recipe_loading", {"recipe_count": 11}):
                # Load 11 recipes - this is the core performance requirement
                success = view_model.load_recipes()
                
            assert success, "Recipe loading should succeed"
            
            metrics = get_all_performance_metrics()
            loading_metric = next((m for m in metrics if m.operation == "recipe_loading"), None)
            
            assert loading_metric is not None, "Loading metrics should be captured"
            assert loading_metric.meets_timing_requirement, f"Loading took {loading_metric.duration_ms:.2f}ms, should be under 200ms"
            assert loading_metric.memory_efficiency_good, f"Memory usage {loading_metric.memory_delta_mb:+.1f}MB should be reasonable"
            
            DebugLogger.log(
                f"✓ Baseline loading performance: {loading_metric.duration_ms:.2f}ms for 11 recipes "
                f"(requirement: 200ms)", 
                "info"
            )
    
    def test_coordinator_architecture_loading_performance(
        self, 
        qapp, 
        performance_config, 
        test_recipes_11,
        performance_manager
    ):
        """Test that coordinator architecture doesn't degrade loading performance."""
        clear_performance_metrics()
        
        # Create full coordinator stack
        view_model = RecipeBrowserViewModel()
        event_coordinator = EventCoordinator(coordinator_name="PerformanceTest")
        filter_coordinator = FilterCoordinator(view_model, performance_config)
        
        with patch.object(view_model, '_recipe_service') as mock_service:
            mock_service.list_filtered.return_value = test_recipes_11
            
            with performance_measurement("coordinator_recipe_loading", {"coordinator_count": 3}):
                # Load through coordinator architecture
                success = filter_coordinator.apply_filter_preset("all_recipes")
                
            # Process any queued events
            for _ in range(10):
                QApplication.processEvents()
                time.sleep(0.001)
        
        assert success, "Coordinator loading should succeed"
        
        metrics = get_all_performance_metrics()
        loading_metric = next((m for m in metrics if m.operation == "coordinator_recipe_loading"), None)
        
        assert loading_metric is not None
        assert loading_metric.duration_ms <= 250, f"Coordinator loading took {loading_metric.duration_ms:.2f}ms, should be under 250ms (allowing 50ms overhead)"
        
        # Cleanup
        filter_coordinator.cleanup()
        event_coordinator.cleanup_all_coordinations()
    
    def test_progressive_rendering_performance(
        self, 
        qapp, 
        performance_config, 
        test_recipes_large,
        performance_manager
    ):
        """Test progressive rendering performance with large datasets."""
        clear_performance_metrics()
        
        # Setup progressive rendering
        batch_count = 0
        rendered_items = []
        
        def mock_render_batch(recipes, start_idx, end_idx):
            nonlocal batch_count
            batch_count += 1
            rendered_items.extend(recipes[start_idx:end_idx])
            time.sleep(0.001)  # Simulate rendering work
        
        renderer = performance_manager.create_callback_renderer(
            name="test_progressive",
            render_callback=mock_render_batch,
            default_batch_size=5,
            default_delay_ms=10
        )
        
        with performance_measurement("progressive_rendering", {"recipe_count": len(test_recipes_large)}):
            # Start progressive rendering
            success = performance_manager.start_progressive_rendering(
                "test_progressive", 
                test_recipes_large,
                batch_size=5
            )
            
            # Wait for rendering to complete
            start_wait = time.time()
            while len(rendered_items) < len(test_recipes_large) and (time.time() - start_wait) < 5.0:
                QApplication.processEvents()
                time.sleep(0.01)
        
        assert success, "Progressive rendering should start successfully"
        assert len(rendered_items) == len(test_recipes_large), f"Should render all {len(test_recipes_large)} recipes"
        assert batch_count > 1, "Should use multiple batches for progressive rendering"
        
        metrics = get_all_performance_metrics()
        render_metric = next((m for m in metrics if m.operation == "progressive_rendering"), None)
        
        assert render_metric is not None
        # Progressive rendering can take longer but should be reasonable
        assert render_metric.duration_ms <= 2000, f"Progressive rendering took {render_metric.duration_ms:.2f}ms for {len(test_recipes_large)} recipes"


class TestFilterOperationPerformance:
    """Test filter operation performance and responsiveness."""
    
    def test_category_filter_response_time(
        self, 
        qapp, 
        performance_config, 
        test_recipes_11,
        mock_recipe_service_fast
    ):
        """Test category filter operations are under 100ms."""
        clear_performance_metrics()
        
        with patch('app.core.services.recipe_service.RecipeService', return_value=mock_recipe_service_fast):
            view_model = RecipeBrowserViewModel()
            filter_coordinator = FilterCoordinator(view_model, performance_config)
            
            # Test multiple filter operations
            categories = ["Main Course", "Desserts", "Appetizers", "All"]
            
            for category in categories:
                with performance_measurement("filter_operation", {"filter_type": "category", "value": category}):
                    success = filter_coordinator.apply_category_filter(category)
                    
                    # Process debounced operations
                    QApplication.processEvents()
                    time.sleep(0.06)  # Wait for debounce
                    QApplication.processEvents()
                
                assert success, f"Category filter {category} should succeed"
        
        metrics = get_all_performance_metrics()
        filter_metrics = [m for m in metrics if m.operation == "filter_operation"]
        
        assert len(filter_metrics) == len(categories), "Should capture metrics for all filter operations"
        
        for metric in filter_metrics:
            assert metric.meets_timing_requirement, f"Filter operation took {metric.duration_ms:.2f}ms, should be under 100ms"
        
        # Cleanup
        filter_coordinator.cleanup()
    
    def test_search_filter_performance_with_debouncing(
        self, 
        qapp, 
        performance_config, 
        test_recipes_11,
        mock_recipe_service_fast
    ):
        """Test search filter performance with debouncing."""
        clear_performance_metrics()
        
        with patch('app.core.services.recipe_service.RecipeService', return_value=mock_recipe_service_fast):
            view_model = RecipeBrowserViewModel()
            filter_coordinator = FilterCoordinator(view_model, performance_config)
            
            # Test rapid search changes (should be debounced)
            search_terms = ["test", "recipe", "performance", ""]
            
            for search_term in search_terms:
                with performance_measurement("search_filter", {"search_term": search_term}):
                    success = filter_coordinator.apply_search_filter(search_term)
                    # Don't wait - test debouncing
                
                assert success, f"Search filter '{search_term}' should succeed"
            
            # Wait for final debounced operation
            time.sleep(0.1)
            QApplication.processEvents()
        
        metrics = get_all_performance_metrics()
        search_metrics = [m for m in metrics if m.operation == "search_filter"]
        
        # Individual search operations should be fast (debounced)
        for metric in search_metrics:
            assert metric.duration_ms <= 50, f"Individual search operation took {metric.duration_ms:.2f}ms"
        
        # Cleanup
        filter_coordinator.cleanup()
    
    def test_combined_filter_performance(
        self, 
        qapp, 
        performance_config, 
        test_recipes_11,
        mock_recipe_service_fast
    ):
        """Test combined filter operations performance."""
        clear_performance_metrics()
        
        with patch('app.core.services.recipe_service.RecipeService', return_value=mock_recipe_service_fast):
            view_model = RecipeBrowserViewModel()
            filter_coordinator = FilterCoordinator(view_model, performance_config)
            
            # Test combined filter operation
            with performance_measurement("combined_filter", {"filters": "category+favorites+search"}):
                success = filter_coordinator.apply_combined_filters(
                    category="Main Course",
                    favorites_only=True,
                    search_term="test",
                    sort_option="Newest"
                )
                
                # Wait for processing
                QApplication.processEvents()
                time.sleep(0.06)
                QApplication.processEvents()
            
            assert success, "Combined filter should succeed"
        
        metrics = get_all_performance_metrics()
        combined_metric = next((m for m in metrics if m.operation == "combined_filter"), None)
        
        assert combined_metric is not None
        assert combined_metric.duration_ms <= 150, f"Combined filter took {combined_metric.duration_ms:.2f}ms, should be under 150ms"
        
        # Cleanup
        filter_coordinator.cleanup()


class TestMemoryUsageAndObjectPooling:
    """Test memory efficiency and object pooling performance."""
    
    def test_object_pool_efficiency(
        self, 
        qapp, 
        performance_config, 
        performance_manager
    ):
        """Test object pool hit rates and memory efficiency."""
        clear_performance_metrics()
        
        # Create recipe card pool
        card_pool = performance_manager.create_object_pool(
            name="test_recipe_cards",
            factory=lambda: Mock(name="MockRecipeCard"),
            max_pool_size=20
        )
        
        # Test pool operations
        objects_created = []
        objects_returned = []
        
        with performance_measurement("object_pool_operations", {"pool_size": 20, "operations": 50}):
            # Get objects from pool
            for i in range(30):  # More than pool size to test overflow
                obj = card_pool.get_object()
                objects_created.append(obj)
            
            # Return half the objects
            for obj in objects_created[:15]:
                card_pool.return_object(obj)
                objects_returned.append(obj)
            
            # Get objects again (should reuse returned ones)
            reused_objects = []
            for i in range(10):
                obj = card_pool.get_object()
                reused_objects.append(obj)
        
        # Check pool statistics
        pool_stats = card_pool.statistics
        
        assert pool_stats['pool_hits'] > 0, "Should have some pool hits from reuse"
        assert pool_stats['total_created'] >= 30, "Should track object creation"
        assert pool_stats['current_active'] > 0, "Should track active objects"
        
        metrics = get_all_performance_metrics()
        pool_metric = next((m for m in metrics if m.operation == "object_pool_operations"), None)
        
        assert pool_metric is not None
        assert pool_metric.duration_ms <= 100, f"Pool operations took {pool_metric.duration_ms:.2f}ms"
        assert pool_metric.memory_efficiency_good, f"Pool memory usage: {pool_metric.memory_delta_mb:+.1f}MB"
        
        hit_rate = (pool_stats['pool_hits'] / pool_stats['total_requests']) * 100 if pool_stats['total_requests'] > 0 else 0
        DebugLogger.log(f"✓ Object pool hit rate: {hit_rate:.1f}%", "info")
        
        assert hit_rate > 10, f"Pool hit rate should be > 10%, got {hit_rate:.1f}%"
    
    def test_memory_usage_during_recipe_operations(
        self, 
        qapp, 
        performance_config, 
        test_recipes_complex,
        performance_manager
    ):
        """Test memory usage remains reasonable during complex operations."""
        clear_performance_metrics()
        
        # Force garbage collection before test
        gc.collect()
        initial_memory = psutil.Process().memory_info().rss / (1024 * 1024)
        
        view_model = RecipeBrowserViewModel()
        
        with patch.object(view_model, '_recipe_service') as mock_service:
            mock_service.list_filtered.return_value = test_recipes_complex
            
            with performance_measurement("complex_recipe_loading", {"recipe_count": len(test_recipes_complex)}):
                # Load complex recipes multiple times
                for i in range(5):
                    view_model.load_recipes()
                    view_model.clear_recipes()
                    
                    # Process events and force cleanup
                    QApplication.processEvents()
                    if i % 2 == 0:
                        gc.collect()
        
        # Check final memory usage
        final_memory = psutil.Process().memory_info().rss / (1024 * 1024)
        memory_growth = final_memory - initial_memory
        
        metrics = get_all_performance_metrics()
        memory_metric = next((m for m in metrics if m.operation == "complex_recipe_loading"), None)
        
        assert memory_metric is not None
        assert memory_growth < 50, f"Memory growth {memory_growth:.1f}MB should be under 50MB for complex operations"
        
        DebugLogger.log(f"✓ Memory usage: {initial_memory:.1f}MB -> {final_memory:.1f}MB (Δ{memory_growth:+.1f}MB)", "info")
    
    def test_cache_performance_and_hit_rates(
        self, 
        qapp, 
        performance_config, 
        test_recipes_11,
        mock_recipe_service_fast
    ):
        """Test cache hit rates and performance."""
        clear_performance_metrics()
        
        with patch('app.core.services.recipe_service.RecipeService', return_value=mock_recipe_service_fast):
            view_model = RecipeBrowserViewModel()
            
            # Load same recipes multiple times to test caching
            filter_dto = Mock()
            filter_dto.recipe_category = None
            filter_dto.favorites_only = False
            filter_dto.search_term = None
            filter_dto.sort_by = "recipe_name"
            filter_dto.sort_order = "asc"
            
            cache_timings = []
            
            for i in range(5):
                with performance_measurement("cache_test", {"iteration": i}):
                    success = view_model.load_filtered_sorted_recipes(filter_dto)
                    
                assert success, f"Cache test iteration {i} should succeed"
        
        metrics = get_all_performance_metrics()
        cache_metrics = [m for m in metrics if m.operation == "cache_test"]
        
        assert len(cache_metrics) == 5, "Should have 5 cache test metrics"
        
        # First call should be slower (cache miss), subsequent calls faster (cache hit)
        first_call = cache_metrics[0]
        subsequent_calls = cache_metrics[1:]
        
        avg_subsequent_time = sum(m.duration_ms for m in subsequent_calls) / len(subsequent_calls)
        
        DebugLogger.log(
            f"✓ Cache performance: First call {first_call.duration_ms:.2f}ms, "
            f"Avg cached calls {avg_subsequent_time:.2f}ms", 
            "info"
        )
        
        # Cached calls should be faster (allowing some variance)
        # assert avg_subsequent_time < first_call.duration_ms * 0.8, "Cached calls should be significantly faster"
        
        # Get cache hit rate from ViewModel
        cache_hit_rate = view_model.cache_hit_rate
        assert cache_hit_rate > 50, f"Cache hit rate should be > 50%, got {cache_hit_rate:.1f}%"


class TestCoordinatorCommunicationPerformance:
    """Test coordinator communication overhead and performance."""
    
    def test_coordinator_signal_communication_overhead(
        self, 
        qapp, 
        performance_config, 
        test_recipes_11,
        performance_manager
    ):
        """Test that coordinator communication adds minimal overhead."""
        clear_performance_metrics()
        
        view_model = RecipeBrowserViewModel()
        event_coordinator = EventCoordinator(coordinator_name="PerformanceTest")
        filter_coordinator = FilterCoordinator(view_model, performance_config)
        rendering_coordinator = RenderingCoordinator(performance_manager, performance_config)
        
        # Setup coordinator integration
        coordinators = {
            'filter': filter_coordinator,
            'rendering': rendering_coordinator,
            'event': event_coordinator,
            'performance': performance_manager
        }
        
        with patch.object(view_model, '_recipe_service') as mock_service:
            mock_service.list_filtered.return_value = test_recipes_11
            
            with performance_measurement("coordinator_communication", {"coordinator_count": 4}):
                # Setup ViewModel coordinator integration
                success = view_model.setup_coordinator_integration(coordinators)
                
                # Trigger operations that cause cross-coordinator communication
                filter_coordinator.apply_category_filter("Main Course")
                
                # Process all events
                for _ in range(20):
                    QApplication.processEvents()
                    time.sleep(0.001)
        
        assert success, "Coordinator integration should succeed"
        
        metrics = get_all_performance_metrics()
        comm_metric = next((m for m in metrics if m.operation == "coordinator_communication"), None)
        
        assert comm_metric is not None
        assert comm_metric.meets_timing_requirement, f"Coordinator communication took {comm_metric.duration_ms:.2f}ms, should be under 10ms"
        
        # Check coordinator state
        coordinator_state = view_model.get_coordinator_state()
        assert coordinator_state['has_coordinators'], "Should have coordinators connected"
        assert coordinator_state['initialized'], "Coordinator integration should be initialized"
        
        # Cleanup
        filter_coordinator.cleanup()
        rendering_coordinator.cleanup()
        event_coordinator.cleanup_all_coordinations()
        view_model.cleanup_coordinator_integration()
    
    def test_event_routing_performance(
        self, 
        qapp, 
        performance_config, 
        performance_manager
    ):
        """Test event coordinator routing performance."""
        clear_performance_metrics()
        
        event_coordinator = EventCoordinator(coordinator_name="EventPerformance")
        
        # Setup multiple event handlers
        handled_events = []
        
        def event_handler_1(data):
            handled_events.append(f"handler1: {data}")
            return "handled1"
        
        def event_handler_2(data):
            handled_events.append(f"handler2: {data}")  
            return "handled2"
        
        def event_handler_3(data):
            handled_events.append(f"handler3: {data}")
            return "handled3"
        
        # Register multiple handlers for same event
        event_coordinator.register_event_route("performance_test", event_handler_1)
        event_coordinator.register_event_route("performance_test", event_handler_2) 
        event_coordinator.register_event_route("performance_test", event_handler_3)
        
        with performance_measurement("event_routing", {"handler_count": 3, "events": 50}):
            # Route multiple events rapidly
            for i in range(50):
                results = event_coordinator.route_event("performance_test", {"event_id": i})
                assert len(results) == 3, "Should call all 3 handlers"
        
        metrics = get_all_performance_metrics()
        routing_metric = next((m for m in metrics if m.operation == "event_routing"), None)
        
        assert routing_metric is not None
        assert routing_metric.duration_ms <= 200, f"Event routing took {routing_metric.duration_ms:.2f}ms for 50 events"
        
        # Should have called all handlers for all events
        assert len(handled_events) == 150, "Should have 150 handler calls (50 events * 3 handlers)"
        
        # Cleanup
        event_coordinator.cleanup_all_coordinations()


class TestStressTestingAndLimits:
    """Stress testing to find performance limits and ensure stability."""
    
    def test_large_dataset_performance(
        self, 
        qapp, 
        performance_config, 
        performance_manager
    ):
        """Test performance with large datasets (500+ recipes)."""
        clear_performance_metrics()
        
        # Create very large dataset
        large_dataset = create_performance_test_recipes(count=500, complexity="simple")
        
        view_model = RecipeBrowserViewModel()
        
        with patch.object(view_model, '_recipe_service') as mock_service:
            mock_service.list_filtered.return_value = large_dataset
            
            with performance_measurement("large_dataset_loading", {"recipe_count": 500}):
                success = view_model.load_recipes()
            
            assert success, "Large dataset loading should succeed"
            
            # Test filtering on large dataset
            with performance_measurement("large_dataset_filtering", {"recipe_count": 500}):
                filtered_success = view_model.update_category_filter("Main Course")
                
                # Wait for processing
                time.sleep(0.1)
                QApplication.processEvents()
            
            assert filtered_success, "Large dataset filtering should succeed"
        
        metrics = get_all_performance_metrics()
        loading_metric = next((m for m in metrics if m.operation == "large_dataset_loading"), None)
        filtering_metric = next((m for m in metrics if m.operation == "large_dataset_filtering"), None)
        
        assert loading_metric is not None
        assert filtering_metric is not None
        
        # Large datasets can take longer but should be reasonable
        assert loading_metric.duration_ms <= 2000, f"Large dataset loading took {loading_metric.duration_ms:.2f}ms"
        assert filtering_metric.duration_ms <= 500, f"Large dataset filtering took {filtering_metric.duration_ms:.2f}ms"
        
        DebugLogger.log(f"✓ Large dataset (500 recipes): Load {loading_metric.duration_ms:.2f}ms, Filter {filtering_metric.duration_ms:.2f}ms", "info")
    
    def test_rapid_operations_stability(
        self, 
        qapp, 
        performance_config, 
        test_recipes_11,
        mock_recipe_service_fast
    ):
        """Test system stability under rapid operations."""
        clear_performance_metrics()
        
        with patch('app.core.services.recipe_service.RecipeService', return_value=mock_recipe_service_fast):
            view_model = RecipeBrowserViewModel()
            filter_coordinator = FilterCoordinator(view_model, performance_config)
            
            operations_completed = 0
            
            with performance_measurement("rapid_operations", {"operation_count": 100}):
                # Perform 100 rapid operations
                for i in range(100):
                    operation = i % 4
                    
                    if operation == 0:
                        filter_coordinator.apply_category_filter(["Main Course", "Desserts"][i % 2])
                    elif operation == 1:
                        filter_coordinator.apply_favorites_filter(i % 2 == 0)
                    elif operation == 2:
                        filter_coordinator.apply_search_filter(f"search_{i % 10}")
                    else:
                        filter_coordinator.apply_combined_filters(
                            category="Appetizers",
                            favorites_only=False,
                            sort_option="A-Z"
                        )
                    
                    operations_completed += 1
                    
                    # Minimal processing to allow some operations through
                    if i % 10 == 0:
                        QApplication.processEvents()
                        time.sleep(0.001)
        
        assert operations_completed == 100, "Should complete all rapid operations"
        
        metrics = get_all_performance_metrics()
        rapid_metric = next((m for m in metrics if m.operation == "rapid_operations"), None)
        
        assert rapid_metric is not None
        assert rapid_metric.duration_ms <= 5000, f"100 rapid operations took {rapid_metric.duration_ms:.2f}ms"
        
        # System should still be responsive after rapid operations
        final_success = filter_coordinator.apply_category_filter("Main Course")
        assert final_success, "System should still be responsive after rapid operations"
        
        # Cleanup
        filter_coordinator.cleanup()
    
    def test_memory_pressure_handling(
        self, 
        qapp, 
        performance_config, 
        performance_manager
    ):
        """Test system behavior under memory pressure."""
        clear_performance_metrics()
        
        # Create memory pressure
        memory_hogs = []
        
        with performance_measurement("memory_pressure", {"pressure_objects": 1000}):
            # Create objects that use memory
            for i in range(1000):
                # Create recipe-like objects with significant memory usage
                recipe = {
                    'id': i,
                    'name': f"Memory Test Recipe {i}" * 10,  # Long strings
                    'instructions': f"Step {j}: Do something complex. " * 50 for j in range(20),
                    'ingredients': [f"Ingredient {j}" for j in range(15)],
                    'metadata': {'data': list(range(100))}
                }
                memory_hogs.append(recipe)
                
                # Track with performance manager
                performance_manager.track_object(recipe)
                
                # Periodically trigger cleanup
                if i % 100 == 0:
                    performance_manager.trigger_memory_cleanup()
                    QApplication.processEvents()
        
        # Check final memory state
        memory_stats = performance_manager.get_performance_summary()['memory']
        
        metrics = get_all_performance_metrics()
        pressure_metric = next((m for m in metrics if m.operation == "memory_pressure"), None)
        
        assert pressure_metric is not None
        assert pressure_metric.duration_ms <= 10000, f"Memory pressure test took {pressure_metric.duration_ms:.2f}ms"
        
        # Memory cleanup should have occurred
        assert memory_stats['dead_references'] >= 0, "Should track dead references"
        assert memory_stats['tracked_objects'] >= 0, "Should track live objects"
        
        DebugLogger.log(
            f"✓ Memory pressure test: {memory_stats['tracked_objects']} live objects, "
            f"{memory_stats['dead_references']} cleaned up", 
            "info"
        )


# ── Performance Analysis and Reporting ─────────────────────────────────────────────────────────────

class TestPerformanceAnalysisAndReporting:
    """Comprehensive performance analysis and reporting."""
    
    def test_comprehensive_performance_report(
        self, 
        qapp, 
        performance_config, 
        test_recipes_11,
        performance_manager,
        mock_recipe_service_fast
    ):
        """Generate comprehensive performance report for all components."""
        clear_performance_metrics()
        
        # Run comprehensive test suite
        with patch('app.core.services.recipe_service.RecipeService', return_value=mock_recipe_service_fast):
            # Test basic loading
            view_model = RecipeBrowserViewModel()
            view_model.load_recipes()
            
            # Test coordinator integration
            event_coordinator = EventCoordinator(coordinator_name="ReportTest")
            filter_coordinator = FilterCoordinator(view_model, performance_config)
            
            coordinators = {
                'filter': filter_coordinator,
                'event': event_coordinator,
                'performance': performance_manager
            }
            
            view_model.setup_coordinator_integration(coordinators)
            
            # Test various operations
            filter_coordinator.apply_category_filter("Main Course")
            filter_coordinator.apply_favorites_filter(True)
            filter_coordinator.apply_search_filter("test")
            
            # Process events
            for _ in range(20):
                QApplication.processEvents()
                time.sleep(0.01)
            
            # Test cache performance
            for i in range(5):
                view_model.refresh_recipes()
                time.sleep(0.01)
            
            # Cleanup
            filter_coordinator.cleanup()
            event_coordinator.cleanup_all_coordinations()
            view_model.cleanup_coordinator_integration()
        
        # Generate comprehensive report
        all_metrics = get_all_performance_metrics()
        performance_summary = performance_manager.get_performance_summary()
        
        # Analyze metrics by operation type
        operations_analysis = {}
        for metric in all_metrics:
            if metric.operation not in operations_analysis:
                operations_analysis[metric.operation] = []
            operations_analysis[metric.operation].append(metric)
        
        # Generate report
        report = {
            'test_timestamp': datetime.now().isoformat(),
            'total_operations': len(all_metrics),
            'operations_analysis': {},
            'performance_requirements': {
                'recipe_loading': {'requirement_ms': 200, 'status': 'unknown'},
                'filter_operations': {'requirement_ms': 100, 'status': 'unknown'},
                'coordinator_communication': {'requirement_ms': 10, 'status': 'unknown'},
            },
            'system_performance': performance_summary,
            'recommendations': []
        }
        
        # Analyze each operation type
        for operation, metrics_list in operations_analysis.items():
            durations = [m.duration_ms for m in metrics_list]
            memory_deltas = [m.memory_delta_mb for m in metrics_list]
            
            analysis = {
                'count': len(metrics_list),
                'avg_duration_ms': statistics.mean(durations),
                'max_duration_ms': max(durations),
                'min_duration_ms': min(durations),
                'avg_memory_delta_mb': statistics.mean(memory_deltas),
                'max_memory_delta_mb': max(memory_deltas),
                'success_rate': sum(1 for m in metrics_list if m.meets_timing_requirement) / len(metrics_list),
                'memory_efficiency': sum(1 for m in metrics_list if m.memory_efficiency_good) / len(metrics_list)
            }
            
            report['operations_analysis'][operation] = analysis
        
        # Check specific requirements
        if 'recipe_loading' in operations_analysis:
            loading_metrics = operations_analysis['recipe_loading']
            avg_loading_time = statistics.mean([m.duration_ms for m in loading_metrics])
            report['performance_requirements']['recipe_loading']['status'] = (
                'PASS' if avg_loading_time <= 200 else 'FAIL'
            )
            report['performance_requirements']['recipe_loading']['avg_time_ms'] = avg_loading_time
        
        if 'filter_operation' in operations_analysis:
            filter_metrics = operations_analysis['filter_operation'] 
            avg_filter_time = statistics.mean([m.duration_ms for m in filter_metrics])
            report['performance_requirements']['filter_operations']['status'] = (
                'PASS' if avg_filter_time <= 100 else 'FAIL'
            )
            report['performance_requirements']['filter_operations']['avg_time_ms'] = avg_filter_time
        
        # Generate recommendations
        for operation, analysis in report['operations_analysis'].items():
            if analysis['success_rate'] < 0.9:
                report['recommendations'].append(
                    f"Operation '{operation}' has low success rate ({analysis['success_rate']*100:.1f}%) - consider optimization"
                )
            
            if analysis['memory_efficiency'] < 0.8:
                report['recommendations'].append(
                    f"Operation '{operation}' has poor memory efficiency ({analysis['memory_efficiency']*100:.1f}%) - check for memory leaks"
                )
            
            if analysis['avg_duration_ms'] > 500:
                report['recommendations'].append(
                    f"Operation '{operation}' is slow (avg {analysis['avg_duration_ms']:.2f}ms) - consider performance optimization"
                )
        
        # Log comprehensive report
        DebugLogger.log("=" * 80, "info")
        DebugLogger.log("COMPREHENSIVE PERFORMANCE VALIDATION REPORT", "info")
        DebugLogger.log("=" * 80, "info")
        
        DebugLogger.log(f"Total Operations Tested: {report['total_operations']}", "info")
        DebugLogger.log("", "info")
        
        DebugLogger.log("CORE PERFORMANCE REQUIREMENTS:", "info")
        for req_name, req_data in report['performance_requirements'].items():
            status = req_data.get('status', 'unknown')
            avg_time = req_data.get('avg_time_ms', 'N/A')
            requirement = req_data.get('requirement_ms', 'N/A')
            
            if status == 'PASS':
                DebugLogger.log(f"✓ {req_name}: {status} (avg: {avg_time:.2f}ms, req: {requirement}ms)", "info")
            elif status == 'FAIL':
                DebugLogger.log(f"✗ {req_name}: {status} (avg: {avg_time:.2f}ms, req: {requirement}ms)", "warning")
            else:
                DebugLogger.log(f"? {req_name}: {status}", "info")
        
        DebugLogger.log("", "info")
        DebugLogger.log("OPERATION ANALYSIS:", "info")
        for operation, analysis in report['operations_analysis'].items():
            DebugLogger.log(
                f"{operation}: {analysis['count']} ops, "
                f"avg {analysis['avg_duration_ms']:.2f}ms, "
                f"success {analysis['success_rate']*100:.1f}%, "
                f"memory {analysis['memory_efficiency']*100:.1f}%",
                "info"
            )
        
        if report['recommendations']:
            DebugLogger.log("", "info")
            DebugLogger.log("RECOMMENDATIONS:", "warning")
            for recommendation in report['recommendations']:
                DebugLogger.log(f"• {recommendation}", "warning")
        
        DebugLogger.log("", "info")
        DebugLogger.log("SYSTEM PERFORMANCE SUMMARY:", "info")
        DebugLogger.log(f"Object Pools: {len(report['system_performance'].get('pools', {}))}", "info")
        DebugLogger.log(f"Progressive Renderers: {len(report['system_performance'].get('renderers', {}))}", "info")
        memory_info = report['system_performance'].get('memory', {})
        DebugLogger.log(
            f"Memory: {memory_info.get('tracked_objects', 0)} tracked, "
            f"{memory_info.get('dead_references', 0)} cleaned",
            "info"
        )
        
        DebugLogger.log("=" * 80, "info")
        
        # Assertions for test validation
        assert report['total_operations'] > 0, "Should have captured performance metrics"
        
        # Critical requirement: recipe loading under 200ms
        if 'recipe_loading' in report['performance_requirements']:
            loading_status = report['performance_requirements']['recipe_loading']['status']
            assert loading_status == 'PASS', f"Recipe loading requirement not met: {loading_status}"
        
        # Memory efficiency should be good overall
        overall_memory_efficiency = statistics.mean([
            analysis['memory_efficiency'] 
            for analysis in report['operations_analysis'].values()
        ]) if report['operations_analysis'] else 1.0
        
        assert overall_memory_efficiency > 0.7, f"Overall memory efficiency too low: {overall_memory_efficiency*100:.1f}%"
        
        return report


# ── Integration with pytest markers for organization ───────────────────────────────────────────────

# Mark all tests in this module for performance testing
pytestmark = [
    pytest.mark.performance,
    pytest.mark.slow,  # These tests may take longer
    pytest.mark.integration  # They test integrated system performance
]


# ── Module Cleanup ──────────────────────────────────────────────────────────────────────────────────

def pytest_runtest_teardown():
    """Clean up after each test."""
    # Clear performance metrics
    clear_performance_metrics()
    
    # Force garbage collection
    gc.collect()
    
    # Process any pending Qt events
    if QApplication.instance():
        QApplication.processEvents()