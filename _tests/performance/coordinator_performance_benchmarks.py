"""Specialized Performance Benchmarks for RecipeBrowser Coordinators

This module provides detailed performance benchmarks for each coordinator component
in the refactored RecipeBrowser architecture:

1. FilterCoordinator - Debouncing efficiency, filter operation performance
2. RenderingCoordinator - Progressive rendering, object pool utilization
3. EventCoordinator - Event routing performance, coordination overhead  
4. PerformanceManager - Object pool hit rates, memory management efficiency
5. ViewModel Integration - Business logic performance, coordinator integration overhead

Each benchmark includes:
- Baseline performance measurements
- Stress testing under load
- Resource usage analysis
- Optimization effectiveness validation
- Regression testing against performance targets

These benchmarks complement the main performance validation and provide
detailed insights into individual coordinator performance characteristics.
"""

import gc
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from unittest.mock import Mock, patch

import pytest
from PySide6.QtCore import QTimer, QCoreApplication, QThread, QObject
from PySide6.QtWidgets import QApplication

from _dev_tools import DebugLogger
from app.core.models.recipe import Recipe
from app.core.dtos.recipe_dtos import RecipeFilterDTO
from app.ui.managers.performance.performance_manager import PerformanceManager
from app.ui.managers.events.event_coordinator import EventCoordinator
from app.ui.view_models.recipe_browser_view_model import RecipeBrowserViewModel
from app.ui.views.recipe_browser.config import (
    RecipeBrowserConfig, create_default_config, create_performance_config
)
from app.ui.views.recipe_browser.filter_coordinator import FilterCoordinator, FilterState
from app.ui.views.recipe_browser.rendering_coordinator import RenderingCoordinator

from _tests.fixtures.recipe_factories import RecipeFactory


# ── Specialized Benchmark Infrastructure ───────────────────────────────────────────────────────────

@dataclass
class CoordinatorBenchmark:
    """Benchmark results for a specific coordinator."""
    coordinator_name: str
    operation: str
    iterations: int
    total_time_ms: float
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    std_dev_ms: float
    throughput_ops_per_sec: float
    memory_delta_mb: float
    success_rate: float
    metadata: Dict[str, Any]
    
    @property
    def performance_grade(self) -> str:
        """Get performance grade based on benchmarks."""
        if self.avg_time_ms <= 10 and self.success_rate >= 0.99:
            return "A"  # Excellent
        elif self.avg_time_ms <= 25 and self.success_rate >= 0.95:
            return "B"  # Good
        elif self.avg_time_ms <= 50 and self.success_rate >= 0.90:
            return "C"  # Acceptable
        elif self.avg_time_ms <= 100 and self.success_rate >= 0.80:
            return "D"  # Poor
        else:
            return "F"  # Failing


class BenchmarkRunner:
    """Specialized benchmark runner for coordinator performance testing."""
    
    def __init__(self):
        self.results: List[CoordinatorBenchmark] = []
        self.current_operation_times: List[float] = []
    
    @contextmanager
    def benchmark_operation(self, coordinator_name: str, operation: str, iterations: int = 1):
        """Context manager for benchmarking coordinator operations."""
        self.current_operation_times.clear()
        operation_start = time.perf_counter()
        memory_before = self._get_memory_usage()
        
        yield self
        
        operation_end = time.perf_counter()
        memory_after = self._get_memory_usage()
        
        # Calculate statistics
        total_time_ms = (operation_end - operation_start) * 1000
        if self.current_operation_times:
            times_ms = [t * 1000 for t in self.current_operation_times]
            avg_time_ms = sum(times_ms) / len(times_ms)
            min_time_ms = min(times_ms)
            max_time_ms = max(times_ms)
            std_dev_ms = (sum((t - avg_time_ms) ** 2 for t in times_ms) / len(times_ms)) ** 0.5
            success_rate = len(times_ms) / iterations  # Assumes all recorded times were successful
        else:
            avg_time_ms = total_time_ms / iterations if iterations > 0 else total_time_ms
            min_time_ms = max_time_ms = avg_time_ms
            std_dev_ms = 0.0
            success_rate = 1.0 if iterations > 0 else 0.0
        
        throughput = (iterations / total_time_ms * 1000) if total_time_ms > 0 else 0
        memory_delta = memory_after - memory_before
        
        benchmark = CoordinatorBenchmark(
            coordinator_name=coordinator_name,
            operation=operation,
            iterations=iterations,
            total_time_ms=total_time_ms,
            avg_time_ms=avg_time_ms,
            min_time_ms=min_time_ms,
            max_time_ms=max_time_ms,
            std_dev_ms=std_dev_ms,
            throughput_ops_per_sec=throughput,
            memory_delta_mb=memory_delta,
            success_rate=success_rate,
            metadata={}
        )
        
        self.results.append(benchmark)
        
        DebugLogger.log(
            f"Benchmark [{coordinator_name}::{operation}]: "
            f"{avg_time_ms:.2f}ms avg ({iterations} ops), "
            f"Grade: {benchmark.performance_grade}",
            "info"
        )
    
    def time_operation(self, operation_func: Callable):
        """Time a single operation and record it."""
        start = time.perf_counter()
        try:
            result = operation_func()
            end = time.perf_counter()
            self.current_operation_times.append(end - start)
            return result
        except Exception as e:
            end = time.perf_counter()
            # Record failed operations too, but don't add to times
            DebugLogger.log(f"Operation failed: {e}", "warning")
            return None
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            return psutil.Process().memory_info().rss / (1024 * 1024)
        except ImportError:
            return 0.0
    
    def get_benchmark_summary(self) -> Dict[str, Any]:
        """Get comprehensive benchmark summary."""
        if not self.results:
            return {"error": "No benchmarks recorded"}
        
        # Group by coordinator
        by_coordinator = {}
        for result in self.results:
            if result.coordinator_name not in by_coordinator:
                by_coordinator[result.coordinator_name] = []
            by_coordinator[result.coordinator_name].append(result)
        
        summary = {
            "total_benchmarks": len(self.results),
            "coordinators": {},
            "overall_performance": {
                "avg_time_ms": sum(r.avg_time_ms for r in self.results) / len(self.results),
                "avg_throughput": sum(r.throughput_ops_per_sec for r in self.results) / len(self.results),
                "avg_success_rate": sum(r.success_rate for r in self.results) / len(self.results),
                "grade_distribution": {}
            }
        }
        
        # Analyze each coordinator
        for coordinator_name, results in by_coordinator.items():
            coordinator_summary = {
                "operations": len(results),
                "avg_time_ms": sum(r.avg_time_ms for r in results) / len(results),
                "avg_throughput": sum(r.throughput_ops_per_sec for r in results) / len(results),
                "success_rate": sum(r.success_rate for r in results) / len(results),
                "total_memory_delta_mb": sum(r.memory_delta_mb for r in results),
                "operations_detail": [
                    {
                        "operation": r.operation,
                        "avg_time_ms": r.avg_time_ms,
                        "throughput": r.throughput_ops_per_sec,
                        "grade": r.performance_grade
                    }
                    for r in results
                ]
            }
            summary["coordinators"][coordinator_name] = coordinator_summary
        
        # Grade distribution
        grades = [r.performance_grade for r in self.results]
        for grade in ["A", "B", "C", "D", "F"]:
            summary["overall_performance"]["grade_distribution"][grade] = grades.count(grade)
        
        return summary


# ── Test Fixtures ─────────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def benchmark_runner():
    """Create benchmark runner for coordinator testing."""
    return BenchmarkRunner()


@pytest.fixture
def benchmark_config():
    """Create configuration optimized for benchmarking."""
    config = create_default_config()
    config.performance.batch_size = 5
    config.performance.render_delay_ms = 1  # Minimal delay for benchmarking
    config.interaction.filter_debounce_delay_ms = 10  # Shorter debounce for benchmarking
    config.features.enable_performance_monitoring = True
    return config


@pytest.fixture
def benchmark_recipes():
    """Create standardized recipe set for benchmarking."""
    return [
        RecipeFactory.build(
            id=i,
            recipe_name=f"Benchmark Recipe {i:03d}",
            recipe_category=["Main Course", "Desserts", "Appetizers"][i % 3],
            is_favorite=(i % 4 == 0),
            total_time=10 + i,
            servings=1 + (i % 6)
        )
        for i in range(20)
    ]


# ── FilterCoordinator Benchmarks ──────────────────────────────────────────────────────────────────

class TestFilterCoordinatorBenchmarks:
    """Detailed benchmarks for FilterCoordinator performance."""
    
    def test_filter_application_throughput(
        self, 
        qapp, 
        benchmark_config, 
        benchmark_recipes,
        benchmark_runner
    ):
        """Benchmark filter application throughput."""
        view_model = Mock(spec=RecipeBrowserViewModel)
        view_model.load_filtered_sorted_recipes.return_value = True
        
        filter_coordinator = FilterCoordinator(view_model, benchmark_config)
        
        # Benchmark category filter operations
        categories = ["Main Course", "Desserts", "Appetizers", "All"] * 10  # 40 operations
        
        with benchmark_runner.benchmark_operation("FilterCoordinator", "category_filters", len(categories)):
            for category in categories:
                benchmark_runner.time_operation(
                    lambda cat=category: filter_coordinator.apply_category_filter(cat)
                )
        
        # Benchmark search filter operations
        search_terms = [f"search_{i}" for i in range(25)]
        
        with benchmark_runner.benchmark_operation("FilterCoordinator", "search_filters", len(search_terms)):
            for term in search_terms:
                benchmark_runner.time_operation(
                    lambda t=term: filter_coordinator.apply_search_filter(t)
                )
        
        # Benchmark combined filter operations
        combined_operations = [
            {"category": "Main Course", "favorites_only": True},
            {"category": "Desserts", "search_term": "chocolate"},
            {"favorites_only": True, "sort_option": "Newest"},
        ] * 8  # 24 operations
        
        with benchmark_runner.benchmark_operation("FilterCoordinator", "combined_filters", len(combined_operations)):
            for operation in combined_operations:
                benchmark_runner.time_operation(
                    lambda op=operation: filter_coordinator.apply_combined_filters(**op)
                )
        
        # Cleanup
        filter_coordinator.cleanup()
        
        # Analyze results
        summary = benchmark_runner.get_benchmark_summary()
        filter_summary = summary["coordinators"]["FilterCoordinator"]
        
        # Assertions
        assert filter_summary["success_rate"] >= 0.95, "Filter coordinator should have high success rate"
        assert filter_summary["avg_time_ms"] <= 50, f"Average filter time {filter_summary['avg_time_ms']:.2f}ms should be under 50ms"
        
        # Log detailed results
        DebugLogger.log("FilterCoordinator Benchmark Results:", "info")
        for op_detail in filter_summary["operations_detail"]:
            DebugLogger.log(
                f"  {op_detail['operation']}: {op_detail['avg_time_ms']:.2f}ms "
                f"({op_detail['throughput']:.1f} ops/sec) - Grade {op_detail['grade']}",
                "info"
            )
    
    def test_debouncing_efficiency_benchmark(
        self, 
        qapp, 
        benchmark_config, 
        benchmark_runner
    ):
        """Benchmark debouncing efficiency under rapid changes."""
        view_model = Mock(spec=RecipeBrowserViewModel)
        view_model.load_filtered_sorted_recipes.return_value = True
        
        filter_coordinator = FilterCoordinator(view_model, benchmark_config)
        
        # Rapid filter changes that should be debounced
        rapid_changes = 100
        
        with benchmark_runner.benchmark_operation("FilterCoordinator", "debounced_operations", rapid_changes):
            start_time = time.perf_counter()
            
            # Apply rapid changes
            for i in range(rapid_changes):
                filter_coordinator.apply_category_filter(["Main Course", "Desserts"][i % 2])
                if i % 10 == 0:
                    QApplication.processEvents()
            
            # Wait for debounce to settle
            time.sleep(0.05)  # Slightly longer than debounce delay
            QApplication.processEvents()
            
            end_time = time.perf_counter()
            benchmark_runner.current_operation_times.append(end_time - start_time)
        
        # Check that debouncing actually reduced ViewModel calls
        actual_calls = view_model.load_filtered_sorted_recipes.call_count
        
        DebugLogger.log(f"Debouncing efficiency: {rapid_changes} operations -> {actual_calls} ViewModel calls", "info")
        
        # Debouncing should significantly reduce calls
        assert actual_calls < rapid_changes / 2, f"Debouncing should reduce calls significantly: {actual_calls} vs {rapid_changes}"
        
        # Cleanup
        filter_coordinator.cleanup()
    
    def test_filter_state_management_performance(
        self, 
        qapp, 
        benchmark_config, 
        benchmark_runner
    ):
        """Benchmark filter state management and history operations."""
        view_model = Mock(spec=RecipeBrowserViewModel)
        view_model.load_filtered_sorted_recipes.return_value = True
        
        filter_coordinator = FilterCoordinator(view_model, benchmark_config)
        
        # Benchmark state transitions
        state_operations = 50
        
        with benchmark_runner.benchmark_operation("FilterCoordinator", "state_management", state_operations):
            for i in range(state_operations):
                # Apply filter to create state
                benchmark_runner.time_operation(
                    lambda: filter_coordinator.apply_combined_filters(
                        category=["Main Course", "Desserts", "Appetizers"][i % 3],
                        favorites_only=(i % 2 == 0),
                        sort_option=["A-Z", "Newest", "Shortest Time"][i % 3]
                    )
                )
                
                # Test state queries every few operations
                if i % 10 == 0:
                    current_state = filter_coordinator.current_state
                    assert isinstance(current_state, FilterState)
        
        # Test history operations
        history_operations = 20
        
        with benchmark_runner.benchmark_operation("FilterCoordinator", "history_operations", history_operations):
            for i in range(history_operations):
                # Get history
                benchmark_runner.time_operation(
                    lambda: filter_coordinator.get_filter_history()
                )
                
                # Test restore if possible
                if i % 5 == 0:
                    benchmark_runner.time_operation(
                        lambda: filter_coordinator.restore_previous_state()
                    )
        
        # Cleanup
        filter_coordinator.cleanup()


# ── RenderingCoordinator Benchmarks ───────────────────────────────────────────────────────────────

class TestRenderingCoordinatorBenchmarks:
    """Detailed benchmarks for RenderingCoordinator performance."""
    
    def test_progressive_rendering_performance(
        self, 
        qapp, 
        benchmark_config, 
        benchmark_recipes,
        benchmark_runner
    ):
        """Benchmark progressive rendering performance and efficiency."""
        performance_manager = PerformanceManager()
        rendering_coordinator = RenderingCoordinator(performance_manager, benchmark_config)
        
        # Mock recipe card creation for consistent timing
        cards_created = []
        def mock_create_card(recipe):
            # Simulate card creation time
            time.sleep(0.001)
            card = Mock()
            card.recipe = recipe
            cards_created.append(card)
            return card
        
        with patch.object(rendering_coordinator, '_create_recipe_card', side_effect=mock_create_card):
            # Benchmark single batch rendering
            batch_size = 5
            batch_recipes = benchmark_recipes[:batch_size]
            
            with benchmark_runner.benchmark_operation("RenderingCoordinator", "batch_rendering", 1):
                benchmark_runner.time_operation(
                    lambda: rendering_coordinator.render_recipes(batch_recipes, selection_mode=False)
                )
            
            # Benchmark progressive rendering with larger dataset
            large_dataset = benchmark_recipes * 3  # 60 recipes
            cards_created.clear()
            
            with benchmark_runner.benchmark_operation("RenderingCoordinator", "progressive_rendering", 1):
                start = time.perf_counter()
                rendering_coordinator.render_recipes(large_dataset, selection_mode=False)
                
                # Wait for progressive rendering to complete
                while len(cards_created) < len(large_dataset):
                    QApplication.processEvents()
                    time.sleep(0.01)
                    if time.perf_counter() - start > 5.0:  # Timeout
                        break
                
                end = time.perf_counter()
                benchmark_runner.current_operation_times.append(end - start)
            
            assert len(cards_created) == len(large_dataset), f"Should create {len(large_dataset)} cards, got {len(cards_created)}"
        
        # Test clearing performance
        with benchmark_runner.benchmark_operation("RenderingCoordinator", "clear_rendering", 1):
            benchmark_runner.time_operation(
                lambda: rendering_coordinator.clear_rendering()
            )
        
        # Cleanup
        rendering_coordinator.cleanup()
        performance_manager.cleanup()
    
    def test_object_pool_utilization_benchmark(
        self, 
        qapp, 
        benchmark_config, 
        benchmark_recipes,
        benchmark_runner
    ):
        """Benchmark object pool utilization in rendering operations."""
        performance_manager = PerformanceManager()
        
        # Create recipe card pool
        card_pool = performance_manager.create_object_pool(
            name="benchmark_recipe_cards",
            factory=lambda: Mock(name="MockRecipeCard"),
            max_pool_size=15
        )
        
        rendering_coordinator = RenderingCoordinator(performance_manager, benchmark_config)
        
        # Benchmark pool operations under rendering load
        pool_operations = 100
        
        with benchmark_runner.benchmark_operation("PerformanceManager", "pool_operations", pool_operations):
            for i in range(pool_operations):
                # Get object from pool
                obj = benchmark_runner.time_operation(lambda: card_pool.get_object())
                
                # Simulate usage
                if obj:
                    obj.recipe_id = i
                    obj.selected = (i % 3 == 0)
                
                # Return to pool (every other iteration)
                if i % 2 == 0 and obj:
                    benchmark_runner.time_operation(lambda o=obj: card_pool.return_object(o))
        
        # Analyze pool performance
        pool_stats = card_pool.statistics
        hit_rate = (pool_stats['pool_hits'] / pool_stats['total_requests']) * 100 if pool_stats['total_requests'] > 0 else 0
        
        DebugLogger.log(f"Object Pool Performance: {hit_rate:.1f}% hit rate, {pool_stats['total_created']} objects created", "info")
        
        # Benchmark memory management
        with benchmark_runner.benchmark_operation("PerformanceManager", "memory_cleanup", 5):
            for i in range(5):
                benchmark_runner.time_operation(lambda: performance_manager.trigger_memory_cleanup())
                QApplication.processEvents()
        
        # Assertions
        assert hit_rate > 20, f"Pool hit rate should be > 20%, got {hit_rate:.1f}%"
        assert pool_stats['total_created'] <= pool_operations, "Should not create excessive objects"
        
        # Cleanup
        rendering_coordinator.cleanup()
        performance_manager.cleanup()


# ── EventCoordinator Benchmarks ───────────────────────────────────────────────────────────────────

class TestEventCoordinatorBenchmarks:
    """Detailed benchmarks for EventCoordinator performance."""
    
    def test_event_routing_throughput(
        self, 
        qapp, 
        benchmark_runner
    ):
        """Benchmark event routing throughput and latency."""
        event_coordinator = EventCoordinator(coordinator_name="BenchmarkTest")
        
        # Setup event handlers with different complexities
        handled_events = []
        
        def simple_handler(data):
            handled_events.append(f"simple:{data.get('id', 0)}")
            return "simple_handled"
        
        def complex_handler(data):
            # Simulate more complex processing
            time.sleep(0.001)
            handled_events.append(f"complex:{data.get('id', 0)}")
            return "complex_handled"
        
        def async_handler(data):
            # Simulate async-style processing
            handled_events.append(f"async:{data.get('id', 0)}")
            return "async_handled"
        
        # Register handlers
        event_coordinator.register_event_route("benchmark_simple", simple_handler)
        event_coordinator.register_event_route("benchmark_complex", complex_handler)  
        event_coordinator.register_event_route("benchmark_async", async_handler)
        
        # Benchmark simple event routing
        simple_events = 100
        
        with benchmark_runner.benchmark_operation("EventCoordinator", "simple_events", simple_events):
            for i in range(simple_events):
                benchmark_runner.time_operation(
                    lambda idx=i: event_coordinator.route_event("benchmark_simple", {"id": idx})
                )
        
        # Benchmark complex event routing  
        complex_events = 50
        
        with benchmark_runner.benchmark_operation("EventCoordinator", "complex_events", complex_events):
            for i in range(complex_events):
                benchmark_runner.time_operation(
                    lambda idx=i: event_coordinator.route_event("benchmark_complex", {"id": idx})
                )
        
        # Benchmark multi-handler events (register multiple handlers for same event)
        event_coordinator.register_event_route("benchmark_multi", simple_handler)
        event_coordinator.register_event_route("benchmark_multi", async_handler)
        
        multi_events = 25
        
        with benchmark_runner.benchmark_operation("EventCoordinator", "multi_handler_events", multi_events):
            for i in range(multi_events):
                benchmark_runner.time_operation(
                    lambda idx=i: event_coordinator.route_event("benchmark_multi", {"id": idx})
                )
        
        # Verify event handling
        total_expected = simple_events + complex_events + (multi_events * 2)  # multi has 2 handlers
        assert len(handled_events) >= total_expected * 0.95, f"Should handle most events: {len(handled_events)}/{total_expected}"
        
        # Cleanup
        event_coordinator.cleanup_all_coordinations()
    
    def test_coordination_overhead_benchmark(
        self, 
        qapp, 
        benchmark_runner
    ):
        """Benchmark coordination overhead in multi-coordinator scenarios."""
        # Setup multiple coordinators
        event_coordinator = EventCoordinator(coordinator_name="PrimaryBench")
        secondary_coordinator = EventCoordinator(coordinator_name="SecondaryBench")
        
        # Create coordination between coordinators
        cross_events = []
        
        def cross_coordinator_handler(data):
            cross_events.append(data)
            # Forward to secondary coordinator
            secondary_coordinator.route_event("forwarded_event", data)
            return "forwarded"
        
        def secondary_handler(data):
            cross_events.append(f"secondary:{data}")
            return "secondary_handled"
        
        event_coordinator.register_event_route("cross_coordination", cross_coordinator_handler)
        secondary_coordinator.register_event_route("forwarded_event", secondary_handler)
        
        # Benchmark cross-coordinator communication
        coordination_ops = 50
        
        with benchmark_runner.benchmark_operation("EventCoordinator", "cross_coordination", coordination_ops):
            for i in range(coordination_ops):
                benchmark_runner.time_operation(
                    lambda idx=i: event_coordinator.route_event("cross_coordination", {"coord_id": idx})
                )
        
        # Should have twice as many events due to forwarding
        expected_events = coordination_ops * 2
        assert len(cross_events) >= expected_events * 0.9, f"Cross-coordination should generate {expected_events} events, got {len(cross_events)}"
        
        # Benchmark concurrent event processing
        concurrent_ops = 30
        
        with benchmark_runner.benchmark_operation("EventCoordinator", "concurrent_events", concurrent_ops):
            # Simulate concurrent event processing
            start_time = time.perf_counter()
            
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = []
                for i in range(concurrent_ops):
                    future = executor.submit(
                        event_coordinator.route_event, 
                        "cross_coordination", 
                        {"concurrent_id": i}
                    )
                    futures.append(future)
                
                # Wait for all to complete
                for future in futures:
                    future.result()
            
            end_time = time.perf_counter()
            benchmark_runner.current_operation_times.append(end_time - start_time)
        
        # Cleanup
        event_coordinator.cleanup_all_coordinations()
        secondary_coordinator.cleanup_all_coordinations()


# ── ViewModel Integration Benchmarks ──────────────────────────────────────────────────────────────

class TestViewModelIntegrationBenchmarks:
    """Benchmarks for ViewModel coordinator integration performance."""
    
    def test_coordinator_integration_overhead(
        self, 
        qapp, 
        benchmark_config,
        benchmark_recipes,
        benchmark_runner
    ):
        """Benchmark coordinator integration overhead in ViewModel."""
        # Test ViewModel without coordinators (baseline)
        baseline_view_model = RecipeBrowserViewModel()
        
        with patch.object(baseline_view_model, '_recipe_service') as mock_service:
            mock_service.list_filtered.return_value = benchmark_recipes
            
            with benchmark_runner.benchmark_operation("ViewModel", "baseline_operations", 20):
                for i in range(20):
                    benchmark_runner.time_operation(
                        lambda: baseline_view_model.load_recipes()
                    )
        
        # Test ViewModel with full coordinator integration
        integrated_view_model = RecipeBrowserViewModel()
        performance_manager = PerformanceManager()
        event_coordinator = EventCoordinator(coordinator_name="IntegrationBench")
        filter_coordinator = FilterCoordinator(integrated_view_model, benchmark_config)
        
        coordinators = {
            'filter': filter_coordinator,
            'event': event_coordinator,
            'performance': performance_manager
        }
        
        integrated_view_model.setup_coordinator_integration(coordinators)
        
        with patch.object(integrated_view_model, '_recipe_service') as mock_service:
            mock_service.list_filtered.return_value = benchmark_recipes
            
            with benchmark_runner.benchmark_operation("ViewModel", "integrated_operations", 20):
                for i in range(20):
                    benchmark_runner.time_operation(
                        lambda: integrated_view_model.load_recipes_with_coordinator_support()
                    )
        
        # Benchmark business logic validation overhead
        with benchmark_runner.benchmark_operation("ViewModel", "business_logic_validation", 30):
            for recipe in benchmark_recipes[:30]:
                benchmark_runner.time_operation(
                    lambda r=recipe: integrated_view_model.validate_recipe_business_rules(r)
                )
        
        # Analyze coordinator integration overhead
        summary = benchmark_runner.get_benchmark_summary()
        vm_summary = summary["coordinators"]["ViewModel"]
        
        baseline_ops = next(op for op in vm_summary["operations_detail"] if op["operation"] == "baseline_operations")
        integrated_ops = next(op for op in vm_summary["operations_detail"] if op["operation"] == "integrated_operations")
        
        overhead_percent = ((integrated_ops["avg_time_ms"] - baseline_ops["avg_time_ms"]) / baseline_ops["avg_time_ms"]) * 100
        
        DebugLogger.log(
            f"Coordinator Integration Overhead: {overhead_percent:.1f}% "
            f"({baseline_ops['avg_time_ms']:.2f}ms -> {integrated_ops['avg_time_ms']:.2f}ms)",
            "info"
        )
        
        # Overhead should be reasonable
        assert overhead_percent <= 50, f"Coordinator integration overhead should be <= 50%, got {overhead_percent:.1f}%"
        
        # Cleanup
        filter_coordinator.cleanup()
        event_coordinator.cleanup_all_coordinations()
        performance_manager.cleanup()
        integrated_view_model.cleanup_coordinator_integration()


# ── Comprehensive Coordinator Benchmark Suite ─────────────────────────────────────────────────────

class TestComprehensiveCoordinatorBenchmarks:
    """Comprehensive benchmark suite testing all coordinators together."""
    
    def test_end_to_end_coordinator_performance(
        self, 
        qapp, 
        benchmark_config,
        benchmark_recipes,
        benchmark_runner
    ):
        """Comprehensive end-to-end performance test of coordinator architecture."""
        # Setup full coordinator stack
        view_model = RecipeBrowserViewModel()
        performance_manager = PerformanceManager()
        event_coordinator = EventCoordinator(coordinator_name="E2EBench")
        filter_coordinator = FilterCoordinator(view_model, benchmark_config)
        rendering_coordinator = RenderingCoordinator(performance_manager, benchmark_config)
        
        coordinators = {
            'filter': filter_coordinator,
            'rendering': rendering_coordinator,
            'event': event_coordinator,
            'performance': performance_manager
        }
        
        view_model.setup_coordinator_integration(coordinators)
        
        # Mock recipe service
        with patch.object(view_model, '_recipe_service') as mock_service:
            mock_service.list_filtered.return_value = benchmark_recipes
            
            # Benchmark complete workflow
            complete_workflows = 10
            
            with benchmark_runner.benchmark_operation("CoordinatorStack", "complete_workflow", complete_workflows):
                for i in range(complete_workflows):
                    workflow_start = time.perf_counter()
                    
                    # Load recipes
                    view_model.load_recipes_with_coordinator_support()
                    
                    # Apply filters
                    filter_coordinator.apply_category_filter("Main Course")
                    filter_coordinator.apply_favorites_filter(True)
                    
                    # Simulate rendering
                    rendering_coordinator.render_recipes(benchmark_recipes[:10], selection_mode=False)
                    
                    # Process events
                    QApplication.processEvents()
                    
                    # Route coordination events
                    event_coordinator.route_event("workflow_step", {"step": i})
                    
                    workflow_end = time.perf_counter()
                    benchmark_runner.current_operation_times.append(workflow_end - workflow_start)
            
            # Test stress scenario
            stress_operations = 50
            
            with benchmark_runner.benchmark_operation("CoordinatorStack", "stress_operations", stress_operations):
                stress_start = time.perf_counter()
                
                for i in range(stress_operations):
                    # Rapid filter changes
                    filter_coordinator.apply_category_filter(["Main Course", "Desserts", "Appetizers"][i % 3])
                    
                    # Event routing
                    event_coordinator.route_event("stress_test", {"iteration": i})
                    
                    # Memory pressure
                    if i % 10 == 0:
                        performance_manager.trigger_memory_cleanup()
                    
                    # Periodic event processing
                    if i % 5 == 0:
                        QApplication.processEvents()
                
                # Wait for all operations to settle
                time.sleep(0.1)
                QApplication.processEvents()
                
                stress_end = time.perf_counter()
                benchmark_runner.current_operation_times.append(stress_end - stress_start)
        
        # Generate comprehensive performance report
        summary = benchmark_runner.get_benchmark_summary()
        
        # Log detailed results
        DebugLogger.log("="*60, "info")
        DebugLogger.log("COMPREHENSIVE COORDINATOR BENCHMARK RESULTS", "info")
        DebugLogger.log("="*60, "info")
        
        for coordinator_name, coordinator_data in summary["coordinators"].items():
            DebugLogger.log(f"\n{coordinator_name}:", "info")
            DebugLogger.log(f"  Operations: {coordinator_data['operations']}", "info")
            DebugLogger.log(f"  Avg Time: {coordinator_data['avg_time_ms']:.2f}ms", "info")
            DebugLogger.log(f"  Throughput: {coordinator_data['avg_throughput']:.1f} ops/sec", "info")
            DebugLogger.log(f"  Success Rate: {coordinator_data['success_rate']*100:.1f}%", "info")
            DebugLogger.log(f"  Memory Delta: {coordinator_data['total_memory_delta_mb']:+.2f}MB", "info")
        
        overall = summary["overall_performance"]
        DebugLogger.log(f"\nOVERALL PERFORMANCE:", "info")
        DebugLogger.log(f"  Average Time: {overall['avg_time_ms']:.2f}ms", "info")
        DebugLogger.log(f"  Average Throughput: {overall['avg_throughput']:.1f} ops/sec", "info")
        DebugLogger.log(f"  Success Rate: {overall['avg_success_rate']*100:.1f}%", "info")
        
        DebugLogger.log(f"\nGRADE DISTRIBUTION:", "info")
        for grade, count in overall["grade_distribution"].items():
            if count > 0:
                DebugLogger.log(f"  Grade {grade}: {count} operations", "info")
        
        DebugLogger.log("="*60, "info")
        
        # Assertions for performance requirements
        assert overall["avg_success_rate"] >= 0.90, f"Overall success rate should be >= 90%, got {overall['avg_success_rate']*100:.1f}%"
        assert overall["avg_time_ms"] <= 100, f"Overall average time should be <= 100ms, got {overall['avg_time_ms']:.2f}ms"
        
        # Coordinator stack should maintain performance
        stack_summary = summary["coordinators"]["CoordinatorStack"]
        assert stack_summary["success_rate"] >= 0.95, "Coordinator stack should have high success rate"
        
        # Cleanup
        filter_coordinator.cleanup()
        rendering_coordinator.cleanup()
        event_coordinator.cleanup_all_coordinations()
        performance_manager.cleanup()
        view_model.cleanup_coordinator_integration()
        
        return summary


# ── Test Markers and Configuration ────────────────────────────────────────────────────────────────

pytestmark = [
    pytest.mark.performance,
    pytest.mark.benchmarks,
    pytest.mark.slow,
    pytest.mark.integration
]


# ── Module Setup and Teardown ─────────────────────────────────────────────────────────────────────

def pytest_runtest_setup(item):
    """Setup before each benchmark test."""
    # Ensure clean state
    gc.collect()
    if QApplication.instance():
        QApplication.processEvents()


def pytest_runtest_teardown(item):
    """Cleanup after each benchmark test."""
    # Force cleanup
    gc.collect()
    if QApplication.instance():
        QApplication.processEvents()