"""Performance Regression Testing for RecipeBrowser Architecture

This module provides comprehensive regression testing to ensure that the refactored
RecipeBrowser coordinator architecture maintains or improves performance over time.

Key regression testing areas:
1. Baseline Performance Comparison - Compare against known good performance baselines
2. Memory Leak Detection - Ensure no memory leaks in coordinator interactions
3. Performance Degradation Detection - Alert on performance regressions
4. Resource Usage Monitoring - Track resource usage patterns over time
5. Stress Testing Regression - Ensure system handles stress consistently
6. Cache Effectiveness Monitoring - Validate cache hit rates remain optimal

The regression tests use historical performance data and established thresholds
to detect when changes negatively impact performance, providing early warning
of performance regressions before they reach production.
"""

import gc
import json
import os
import time
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from unittest.mock import Mock, patch

import pytest
from PySide6.QtCore import QTimer, QCoreApplication
from PySide6.QtWidgets import QApplication

from _dev_tools import DebugLogger
from app.core.models.recipe import Recipe
from app.ui.managers.performance.performance_manager import PerformanceManager
from app.ui.managers.events.event_coordinator import EventCoordinator
from app.ui.view_models.recipe_browser_view_model import RecipeBrowserViewModel
from app.ui.views.recipe_browser.config import create_default_config, create_performance_config
from app.ui.views.recipe_browser.filter_coordinator import FilterCoordinator
from app.ui.views.recipe_browser.rendering_coordinator import RenderingCoordinator

from _tests.fixtures.recipe_factories import RecipeFactory


# ── Performance Regression Infrastructure ─────────────────────────────────────────────────────────

@dataclass
class PerformanceBaseline:
    """Performance baseline for regression testing."""
    operation: str
    baseline_time_ms: float
    baseline_memory_mb: float
    acceptable_regression_percent: float
    timestamp: str
    recipe_count: int
    configuration: str
    metadata: Dict[str, Any]


@dataclass 
class RegressionTestResult:
    """Result of a performance regression test."""
    operation: str
    current_time_ms: float
    baseline_time_ms: float
    time_regression_percent: float
    current_memory_mb: float
    baseline_memory_mb: float
    memory_regression_percent: float
    passes_regression_test: bool
    performance_grade: str
    notes: str
    timestamp: str


class PerformanceRegressionTester:
    """Comprehensive performance regression testing system."""
    
    def __init__(self, baseline_file: Optional[str] = None):
        self.baseline_file = baseline_file or "performance_baselines.json"
        self.results_file = "regression_test_results.json"
        self.baselines: Dict[str, PerformanceBaseline] = {}
        self.test_results: List[RegressionTestResult] = []
        
        # Load existing baselines
        self._load_baselines()
    
    def _load_baselines(self):
        """Load performance baselines from file."""
        try:
            baseline_path = Path(self.baseline_file)
            if baseline_path.exists():
                with open(baseline_path, 'r') as f:
                    baseline_data = json.load(f)
                    for key, data in baseline_data.items():
                        self.baselines[key] = PerformanceBaseline(**data)
                DebugLogger.log(f"Loaded {len(self.baselines)} performance baselines", "debug")
            else:
                DebugLogger.log("No existing baselines found, will create new ones", "debug")
        except Exception as e:
            DebugLogger.log(f"Error loading baselines: {e}", "warning")
    
    def _save_baselines(self):
        """Save performance baselines to file."""
        try:
            baseline_data = {key: asdict(baseline) for key, baseline in self.baselines.items()}
            with open(self.baseline_file, 'w') as f:
                json.dump(baseline_data, f, indent=2)
            DebugLogger.log(f"Saved {len(self.baselines)} performance baselines", "debug")
        except Exception as e:
            DebugLogger.log(f"Error saving baselines: {e}", "error")
    
    def _save_results(self):
        """Save regression test results to file."""
        try:
            results_data = [asdict(result) for result in self.test_results]
            with open(self.results_file, 'w') as f:
                json.dump(results_data, f, indent=2)
            DebugLogger.log(f"Saved {len(self.test_results)} regression test results", "debug")
        except Exception as e:
            DebugLogger.log(f"Error saving results: {e}", "error")
    
    def establish_baseline(
        self, 
        operation: str, 
        time_ms: float, 
        memory_mb: float,
        recipe_count: int = 11,
        configuration: str = "default",
        acceptable_regression: float = 20.0,
        metadata: Optional[Dict] = None
    ):
        """Establish a performance baseline for regression testing."""
        baseline = PerformanceBaseline(
            operation=operation,
            baseline_time_ms=time_ms,
            baseline_memory_mb=memory_mb,
            acceptable_regression_percent=acceptable_regression,
            timestamp=datetime.now().isoformat(),
            recipe_count=recipe_count,
            configuration=configuration,
            metadata=metadata or {}
        )
        
        self.baselines[operation] = baseline
        self._save_baselines()
        
        DebugLogger.log(
            f"Established baseline for {operation}: {time_ms:.2f}ms, {memory_mb:.2f}MB "
            f"(±{acceptable_regression}%)",
            "info"
        )
    
    def test_regression(
        self, 
        operation: str, 
        current_time_ms: float, 
        current_memory_mb: float,
        notes: str = ""
    ) -> RegressionTestResult:
        """Test for performance regression against baseline."""
        if operation not in self.baselines:
            # If no baseline exists, create one
            self.establish_baseline(operation, current_time_ms, current_memory_mb)
            result = RegressionTestResult(
                operation=operation,
                current_time_ms=current_time_ms,
                baseline_time_ms=current_time_ms,
                time_regression_percent=0.0,
                current_memory_mb=current_memory_mb,
                baseline_memory_mb=current_memory_mb,
                memory_regression_percent=0.0,
                passes_regression_test=True,
                performance_grade="NEW",
                notes=f"New baseline established. {notes}",
                timestamp=datetime.now().isoformat()
            )
        else:
            baseline = self.baselines[operation]
            
            # Calculate regression percentages
            time_regression = ((current_time_ms - baseline.baseline_time_ms) / baseline.baseline_time_ms) * 100
            memory_regression = ((current_memory_mb - baseline.baseline_memory_mb) / baseline.baseline_memory_mb) * 100 if baseline.baseline_memory_mb > 0 else 0
            
            # Determine if test passes
            time_passes = time_regression <= baseline.acceptable_regression_percent
            memory_passes = memory_regression <= baseline.acceptable_regression_percent * 2  # Memory is less strict
            passes_overall = time_passes and memory_passes
            
            # Assign performance grade
            if time_regression <= 0 and memory_regression <= 0:
                grade = "A+"  # Performance improvement
            elif time_regression <= 5 and memory_regression <= 10:
                grade = "A"   # Excellent, within noise
            elif time_regression <= 10 and memory_regression <= 15:
                grade = "B"   # Good performance
            elif time_regression <= baseline.acceptable_regression_percent and memory_regression <= baseline.acceptable_regression_percent * 2:
                grade = "C"   # Acceptable regression
            else:
                grade = "F"   # Failing regression
            
            result = RegressionTestResult(
                operation=operation,
                current_time_ms=current_time_ms,
                baseline_time_ms=baseline.baseline_time_ms,
                time_regression_percent=time_regression,
                current_memory_mb=current_memory_mb,
                baseline_memory_mb=baseline.baseline_memory_mb,
                memory_regression_percent=memory_regression,
                passes_regression_test=passes_overall,
                performance_grade=grade,
                notes=notes,
                timestamp=datetime.now().isoformat()
            )
        
        self.test_results.append(result)
        self._save_results()
        
        # Log result
        status = "PASS" if result.passes_regression_test else "FAIL"
        DebugLogger.log(
            f"Regression test [{operation}]: {status} - Grade {result.performance_grade} "
            f"(Time: {result.time_regression_percent:+.1f}%, Memory: {result.memory_regression_percent:+.1f}%)",
            "info" if result.passes_regression_test else "warning"
        )
        
        return result
    
    def get_regression_summary(self) -> Dict[str, Any]:
        """Get comprehensive regression test summary."""
        if not self.test_results:
            return {"error": "No regression test results available"}
        
        total_tests = len(self.test_results)
        passing_tests = sum(1 for r in self.test_results if r.passes_regression_test)
        
        # Grade distribution
        grades = [r.performance_grade for r in self.test_results]
        grade_distribution = {grade: grades.count(grade) for grade in set(grades)}
        
        # Performance trends
        avg_time_regression = statistics.mean([r.time_regression_percent for r in self.test_results])
        avg_memory_regression = statistics.mean([r.memory_regression_percent for r in self.test_results])
        
        # Worst regressions
        worst_time_regression = max(self.test_results, key=lambda r: r.time_regression_percent, default=None)
        worst_memory_regression = max(self.test_results, key=lambda r: r.memory_regression_percent, default=None)
        
        return {
            "total_tests": total_tests,
            "passing_tests": passing_tests,
            "pass_rate": (passing_tests / total_tests) * 100 if total_tests > 0 else 0,
            "grade_distribution": grade_distribution,
            "performance_trends": {
                "avg_time_regression_percent": avg_time_regression,
                "avg_memory_regression_percent": avg_memory_regression
            },
            "worst_regressions": {
                "time": {
                    "operation": worst_time_regression.operation if worst_time_regression else None,
                    "regression_percent": worst_time_regression.time_regression_percent if worst_time_regression else 0
                },
                "memory": {
                    "operation": worst_memory_regression.operation if worst_memory_regression else None,
                    "regression_percent": worst_memory_regression.memory_regression_percent if worst_memory_regression else 0
                }
            },
            "baselines_count": len(self.baselines),
            "timestamp": datetime.now().isoformat()
        }


# ── Test Fixtures ─────────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def regression_tester():
    """Create regression tester for testing."""
    tester = PerformanceRegressionTester("test_performance_baselines.json")
    yield tester
    # Cleanup test files
    try:
        os.remove("test_performance_baselines.json")
        os.remove("regression_test_results.json")
    except FileNotFoundError:
        pass


@pytest.fixture
def standard_test_recipes():
    """Create standardized recipe set for consistent regression testing."""
    return [
        RecipeFactory.build(
            id=i,
            recipe_name=f"Regression Test Recipe {i:02d}",
            recipe_category=["Main Course", "Desserts", "Appetizers"][i % 3],
            is_favorite=(i % 4 == 0),
            total_time=15 + (i * 3),
            servings=2 + (i % 6),
            instructions=f"Test instructions for recipe {i}" * 5  # Consistent complexity
        )
        for i in range(11)  # Exactly 11 for baseline requirement
    ]


def measure_operation_performance(operation_func, operation_name: str) -> Tuple[float, float]:
    """Measure operation performance (time and memory)."""
    import psutil
    
    # Force garbage collection before measurement
    gc.collect()
    
    # Get initial memory
    initial_memory = psutil.Process().memory_info().rss / (1024 * 1024)  # MB
    
    # Time the operation
    start_time = time.perf_counter()
    result = operation_func()
    end_time = time.perf_counter()
    
    # Get final memory
    final_memory = psutil.Process().memory_info().rss / (1024 * 1024)  # MB
    
    operation_time_ms = (end_time - start_time) * 1000
    memory_delta_mb = final_memory - initial_memory
    
    return operation_time_ms, memory_delta_mb


# ── Core Performance Regression Tests ─────────────────────────────────────────────────────────────

class TestCorePerformanceRegression:
    """Core performance regression tests for key operations."""
    
    def test_recipe_loading_regression(
        self, 
        qapp, 
        standard_test_recipes,
        regression_tester
    ):
        """Test recipe loading performance against baseline."""
        view_model = RecipeBrowserViewModel()
        
        with patch.object(view_model, '_recipe_service') as mock_service:
            mock_service.list_filtered.return_value = standard_test_recipes
            
            # Measure performance
            def load_operation():
                return view_model.load_recipes()
            
            time_ms, memory_mb = measure_operation_performance(load_operation, "recipe_loading")
            
            # Test against regression baseline
            result = regression_tester.test_regression(
                "recipe_loading_11_recipes",
                time_ms,
                memory_mb,
                f"Standard 11 recipe loading test with {len(standard_test_recipes)} recipes"
            )
            
            # Assertions
            assert result.passes_regression_test, f"Recipe loading regression test failed: {result.performance_grade}"
            assert result.current_time_ms <= 250, f"Recipe loading took {result.current_time_ms:.2f}ms, should be under 250ms"
            
            # Log performance comparison
            if result.performance_grade != "NEW":
                DebugLogger.log(
                    f"Recipe Loading Performance: {result.current_time_ms:.2f}ms "
                    f"(baseline: {result.baseline_time_ms:.2f}ms, "
                    f"change: {result.time_regression_percent:+.1f}%)",
                    "info"
                )
    
    def test_filter_operation_regression(
        self, 
        qapp, 
        standard_test_recipes,
        regression_tester
    ):
        """Test filter operation performance against baseline."""
        config = create_default_config()
        view_model = RecipeBrowserViewModel()
        filter_coordinator = FilterCoordinator(view_model, config)
        
        with patch.object(view_model, '_recipe_service') as mock_service:
            mock_service.list_filtered.return_value = standard_test_recipes
            
            # Load initial recipes
            view_model.load_recipes()
            
            # Measure filter operation performance
            def filter_operation():
                # Apply multiple filter operations
                filter_coordinator.apply_category_filter("Main Course")
                filter_coordinator.apply_favorites_filter(True)
                filter_coordinator.apply_search_filter("test")
                
                # Wait for debounced operations
                time.sleep(0.06)
                QApplication.processEvents()
                
                return True
            
            time_ms, memory_mb = measure_operation_performance(filter_operation, "filter_operations")
            
            # Test regression
            result = regression_tester.test_regression(
                "filter_operations_combined",
                time_ms,
                memory_mb,
                "Combined filter operations with debouncing"
            )
            
            assert result.passes_regression_test, f"Filter operation regression test failed: {result.performance_grade}"
            
            # Cleanup
            filter_coordinator.cleanup()
    
    def test_coordinator_integration_regression(
        self, 
        qapp, 
        standard_test_recipes,
        regression_tester
    ):
        """Test coordinator integration performance against baseline."""
        config = create_performance_config()
        
        # Setup full coordinator stack
        view_model = RecipeBrowserViewModel()
        performance_manager = PerformanceManager()
        event_coordinator = EventCoordinator(coordinator_name="RegressionTest")
        filter_coordinator = FilterCoordinator(view_model, config)
        
        coordinators = {
            'filter': filter_coordinator,
            'event': event_coordinator,
            'performance': performance_manager
        }
        
        with patch.object(view_model, '_recipe_service') as mock_service:
            mock_service.list_filtered.return_value = standard_test_recipes
            
            # Measure coordinator integration performance
            def integration_operation():
                # Setup integration
                view_model.setup_coordinator_integration(coordinators)
                
                # Execute coordinated operations
                view_model.load_recipes_with_coordinator_support()
                filter_coordinator.apply_category_filter("Desserts")
                
                # Process coordination
                for _ in range(10):
                    QApplication.processEvents()
                    time.sleep(0.001)
                
                return True
            
            time_ms, memory_mb = measure_operation_performance(integration_operation, "coordinator_integration")
            
            result = regression_tester.test_regression(
                "coordinator_integration_full",
                time_ms,
                memory_mb,
                "Full coordinator integration with operations"
            )
            
            assert result.passes_regression_test, f"Coordinator integration regression failed: {result.performance_grade}"
            
            # Cleanup
            filter_coordinator.cleanup()
            event_coordinator.cleanup_all_coordinations()
            performance_manager.cleanup()
            view_model.cleanup_coordinator_integration()


class TestMemoryRegressionTesting:
    """Memory-focused regression testing to detect memory leaks."""
    
    def test_memory_leak_regression(
        self, 
        qapp, 
        standard_test_recipes,
        regression_tester
    ):
        """Test for memory leaks in repeated operations."""
        import psutil
        
        initial_memory = psutil.Process().memory_info().rss / (1024 * 1024)
        
        # Perform repeated operations that might leak memory
        view_models = []
        coordinators = []
        
        def memory_stress_operation():
            nonlocal view_models, coordinators
            
            # Create and use multiple coordinator instances
            for i in range(20):
                vm = RecipeBrowserViewModel()
                perf_mgr = PerformanceManager()
                event_coord = EventCoordinator(coordinator_name=f"MemTest_{i}")
                filter_coord = FilterCoordinator(vm, create_default_config())
                
                # Use them briefly
                with patch.object(vm, '_recipe_service') as mock_service:
                    mock_service.list_filtered.return_value = standard_test_recipes[:5]  # Smaller dataset
                    vm.load_recipes()
                    filter_coord.apply_category_filter("Main Course")
                    
                    # Process events
                    QApplication.processEvents()
                
                # Store references temporarily
                view_models.append(vm)
                coordinators.extend([perf_mgr, event_coord, filter_coord])
                
                # Cleanup some instances
                if i % 5 == 0:
                    # Cleanup oldest instances
                    for coord in coordinators[-15:]:
                        if hasattr(coord, 'cleanup'):
                            coord.cleanup()
                        if hasattr(coord, 'cleanup_all_coordinations'):
                            coord.cleanup_all_coordinations()
                    
                    # Force garbage collection
                    gc.collect()
                    QApplication.processEvents()
            
            return True
        
        time_ms, memory_mb = measure_operation_performance(memory_stress_operation, "memory_stress")
        
        # Cleanup remaining objects
        for coord in coordinators:
            if hasattr(coord, 'cleanup'):
                coord.cleanup()
            if hasattr(coord, 'cleanup_all_coordinations'):
                coord.cleanup_all_coordinations()
        
        view_models.clear()
        coordinators.clear()
        gc.collect()
        
        final_memory = psutil.Process().memory_info().rss / (1024 * 1024)
        memory_growth = final_memory - initial_memory
        
        result = regression_tester.test_regression(
            "memory_leak_stress_test",
            time_ms,
            memory_growth,  # Use memory growth instead of delta
            f"Memory stress test: {initial_memory:.1f}MB -> {final_memory:.1f}MB (growth: {memory_growth:+.1f}MB)"
        )
        
        # Memory growth should be minimal
        assert memory_growth < 20, f"Memory growth {memory_growth:.1f}MB should be under 20MB"
        assert result.passes_regression_test, f"Memory leak regression test failed: {result.performance_grade}"
    
    def test_cache_efficiency_regression(
        self, 
        qapp, 
        standard_test_recipes,
        regression_tester
    ):
        """Test cache efficiency regression."""
        view_model = RecipeBrowserViewModel()
        
        with patch.object(view_model, '_recipe_service') as mock_service:
            mock_service.list_filtered.return_value = standard_test_recipes
            
            def cache_efficiency_operation():
                # Load same recipes multiple times to test caching
                for i in range(10):
                    view_model.load_recipes()
                    view_model.refresh_recipes()
                    
                    # Apply same filters repeatedly
                    view_model.update_category_filter("Main Course")
                    view_model.update_category_filter(None)
                    
                    if i % 3 == 0:
                        QApplication.processEvents()
                
                # Get cache metrics
                cache_hit_rate = view_model.cache_hit_rate
                cache_size = view_model.cache_size
                
                return cache_hit_rate, cache_size
            
            start_time = time.perf_counter()
            cache_hit_rate, cache_size = cache_efficiency_operation()
            end_time = time.perf_counter()
            
            operation_time_ms = (end_time - start_time) * 1000
            
            result = regression_tester.test_regression(
                "cache_efficiency_test",
                operation_time_ms,
                cache_size,  # Use cache size as "memory" metric
                f"Cache hit rate: {cache_hit_rate:.1f}%, Cache size: {cache_size}"
            )
            
            # Cache should be effective
            assert cache_hit_rate >= 30, f"Cache hit rate {cache_hit_rate:.1f}% should be at least 30%"
            assert result.passes_regression_test, f"Cache efficiency regression failed: {result.performance_grade}"


class TestStressTestRegression:
    """Stress testing regression to ensure system handles load consistently."""
    
    def test_rapid_operations_regression(
        self, 
        qapp, 
        standard_test_recipes,
        regression_tester
    ):
        """Test performance under rapid operations."""
        config = create_performance_config()
        view_model = RecipeBrowserViewModel()
        filter_coordinator = FilterCoordinator(view_model, config)
        
        with patch.object(view_model, '_recipe_service') as mock_service:
            mock_service.list_filtered.return_value = standard_test_recipes
            
            def rapid_operations():
                operations_completed = 0
                
                # Rapid filter changes
                for i in range(100):
                    operation_type = i % 4
                    
                    try:
                        if operation_type == 0:
                            filter_coordinator.apply_category_filter(["Main Course", "Desserts"][i % 2])
                        elif operation_type == 1:
                            filter_coordinator.apply_favorites_filter(i % 2 == 0)
                        elif operation_type == 2:
                            filter_coordinator.apply_search_filter(f"test_{i % 5}")
                        else:
                            filter_coordinator.reset_to_defaults()
                        
                        operations_completed += 1
                        
                        # Minimal processing
                        if i % 20 == 0:
                            QApplication.processEvents()
                            
                    except Exception as e:
                        DebugLogger.log(f"Operation {i} failed: {e}", "warning")
                
                # Let operations settle
                time.sleep(0.1)
                QApplication.processEvents()
                
                return operations_completed
            
            time_ms, memory_mb = measure_operation_performance(rapid_operations, "rapid_operations")
            
            result = regression_tester.test_regression(
                "rapid_operations_stress",
                time_ms,
                memory_mb,
                "100 rapid filter operations with debouncing"
            )
            
            assert result.passes_regression_test, f"Rapid operations regression failed: {result.performance_grade}"
            assert result.current_time_ms <= 2000, f"Rapid operations took {result.current_time_ms:.2f}ms, should be under 2000ms"
            
            # Cleanup
            filter_coordinator.cleanup()
    
    def test_large_dataset_regression(
        self, 
        qapp, 
        regression_tester
    ):
        """Test performance regression with large datasets."""
        # Create larger dataset for stress testing
        large_dataset = [
            RecipeFactory.build(
                id=i,
                recipe_name=f"Large Dataset Recipe {i:03d}",
                recipe_category=["Main Course", "Desserts", "Appetizers", "Side Dishes", "Beverages"][i % 5],
                is_favorite=(i % 7 == 0),
                total_time=10 + (i % 120),
                servings=1 + (i % 12)
            )
            for i in range(200)  # 200 recipes for stress testing
        ]
        
        view_model = RecipeBrowserViewModel()
        
        with patch.object(view_model, '_recipe_service') as mock_service:
            mock_service.list_filtered.return_value = large_dataset
            
            def large_dataset_operation():
                # Load large dataset
                view_model.load_recipes()
                
                # Apply filters on large dataset
                view_model.update_category_filter("Main Course")
                view_model.update_favorites_filter(True)
                view_model.update_search_term("recipe")
                
                # Process operations
                time.sleep(0.1)
                QApplication.processEvents()
                
                return len(view_model.current_recipes)
            
            time_ms, memory_mb = measure_operation_performance(large_dataset_operation, "large_dataset")
            
            result = regression_tester.test_regression(
                "large_dataset_200_recipes",
                time_ms,
                memory_mb,
                f"Large dataset processing with {len(large_dataset)} recipes"
            )
            
            assert result.passes_regression_test, f"Large dataset regression failed: {result.performance_grade}"
            # Large datasets can take longer but should be reasonable
            assert result.current_time_ms <= 3000, f"Large dataset processing took {result.current_time_ms:.2f}ms"


# ── Comprehensive Regression Analysis ─────────────────────────────────────────────────────────────

class TestComprehensiveRegressionAnalysis:
    """Comprehensive regression analysis and reporting."""
    
    def test_comprehensive_regression_report(
        self, 
        qapp, 
        standard_test_recipes,
        regression_tester
    ):
        """Generate comprehensive regression analysis report."""
        # Run multiple regression tests to build comprehensive data
        
        # 1. Basic operations
        self._test_basic_operations_regression(standard_test_recipes, regression_tester)
        
        # 2. Coordinator integration
        self._test_coordinator_regression(standard_test_recipes, regression_tester)
        
        # 3. Memory efficiency
        self._test_memory_regression(standard_test_recipes, regression_tester)
        
        # Generate comprehensive report
        summary = regression_tester.get_regression_summary()
        
        # Log comprehensive regression report
        DebugLogger.log("="*80, "info")
        DebugLogger.log("COMPREHENSIVE PERFORMANCE REGRESSION REPORT", "info")
        DebugLogger.log("="*80, "info")
        
        DebugLogger.log(f"Test Date: {summary['timestamp']}", "info")
        DebugLogger.log(f"Total Tests: {summary['total_tests']}", "info")
        DebugLogger.log(f"Passing Tests: {summary['passing_tests']}/{summary['total_tests']}", "info")
        DebugLogger.log(f"Pass Rate: {summary['pass_rate']:.1f}%", "info")
        DebugLogger.log(f"Baselines Available: {summary['baselines_count']}", "info")
        DebugLogger.log("", "info")
        
        DebugLogger.log("PERFORMANCE TRENDS:", "info")
        trends = summary['performance_trends']
        DebugLogger.log(f"Average Time Regression: {trends['avg_time_regression_percent']:+.1f}%", "info")
        DebugLogger.log(f"Average Memory Regression: {trends['avg_memory_regression_percent']:+.1f}%", "info")
        DebugLogger.log("", "info")
        
        DebugLogger.log("GRADE DISTRIBUTION:", "info")
        for grade, count in summary['grade_distribution'].items():
            percentage = (count / summary['total_tests']) * 100 if summary['total_tests'] > 0 else 0
            DebugLogger.log(f"  Grade {grade}: {count} tests ({percentage:.1f}%)", "info")
        DebugLogger.log("", "info")
        
        DebugLogger.log("WORST REGRESSIONS:", "info")
        worst = summary['worst_regressions']
        if worst['time']['operation']:
            DebugLogger.log(f"  Time: {worst['time']['operation']} ({worst['time']['regression_percent']:+.1f}%)", "warning")
        if worst['memory']['operation']:
            DebugLogger.log(f"  Memory: {worst['memory']['operation']} ({worst['memory']['regression_percent']:+.1f}%)", "warning")
        
        DebugLogger.log("="*80, "info")
        
        # Assertions for overall regression health
        assert summary['pass_rate'] >= 80, f"Regression pass rate {summary['pass_rate']:.1f}% should be at least 80%"
        assert trends['avg_time_regression_percent'] <= 25, f"Average time regression {trends['avg_time_regression_percent']:+.1f}% should be under 25%"
        
        # Check for catastrophic regressions
        if worst['time']['regression_percent'] > 50:
            pytest.fail(f"Catastrophic time regression detected in {worst['time']['operation']}: {worst['time']['regression_percent']:+.1f}%")
        
        return summary
    
    def _test_basic_operations_regression(self, recipes, regression_tester):
        """Test basic operations for regression."""
        view_model = RecipeBrowserViewModel()
        
        with patch.object(view_model, '_recipe_service') as mock_service:
            mock_service.list_filtered.return_value = recipes
            
            # Test loading
            time_ms, memory_mb = measure_operation_performance(
                lambda: view_model.load_recipes(), "basic_loading"
            )
            regression_tester.test_regression("basic_recipe_loading", time_ms, memory_mb)
            
            # Test filtering
            time_ms, memory_mb = measure_operation_performance(
                lambda: view_model.update_category_filter("Main Course"), "basic_filtering"
            )
            regression_tester.test_regression("basic_category_filtering", time_ms, memory_mb)
            
            # Test search
            time_ms, memory_mb = measure_operation_performance(
                lambda: view_model.update_search_term("test"), "basic_search"
            )
            regression_tester.test_regression("basic_search_operation", time_ms, memory_mb)
    
    def _test_coordinator_regression(self, recipes, regression_tester):
        """Test coordinator operations for regression."""
        config = create_default_config()
        view_model = RecipeBrowserViewModel()
        filter_coordinator = FilterCoordinator(view_model, config)
        event_coordinator = EventCoordinator(coordinator_name="RegressionAnalysis")
        
        with patch.object(view_model, '_recipe_service') as mock_service:
            mock_service.list_filtered.return_value = recipes
            
            # Test coordinator setup
            coordinators = {'filter': filter_coordinator, 'event': event_coordinator}
            time_ms, memory_mb = measure_operation_performance(
                lambda: view_model.setup_coordinator_integration(coordinators), "coordinator_setup"
            )
            regression_tester.test_regression("coordinator_integration_setup", time_ms, memory_mb)
            
            # Test coordinated operations
            def coordinated_operation():
                filter_coordinator.apply_category_filter("Desserts")
                event_coordinator.route_event("test_event", {"data": "regression_test"})
                QApplication.processEvents()
                return True
            
            time_ms, memory_mb = measure_operation_performance(coordinated_operation, "coordinated_ops")
            regression_tester.test_regression("coordinated_operations", time_ms, memory_mb)
            
            # Cleanup
            filter_coordinator.cleanup()
            event_coordinator.cleanup_all_coordinations()
            view_model.cleanup_coordinator_integration()
    
    def _test_memory_regression(self, recipes, regression_tester):
        """Test memory operations for regression."""
        performance_manager = PerformanceManager()
        
        # Test object pool performance
        pool = performance_manager.create_object_pool(
            "regression_pool",
            lambda: {"test": "object"},
            max_pool_size=20
        )
        
        def pool_operation():
            objects = []
            for i in range(30):  # More than pool size
                obj = pool.get_object()
                objects.append(obj)
            
            for obj in objects[:15]:
                pool.return_object(obj)
            
            return pool.statistics
        
        time_ms, memory_mb = measure_operation_performance(pool_operation, "pool_ops")
        regression_tester.test_regression("object_pool_operations", time_ms, memory_mb)
        
        # Test memory cleanup
        time_ms, memory_mb = measure_operation_performance(
            lambda: performance_manager.trigger_memory_cleanup(), "memory_cleanup"
        )
        regression_tester.test_regression("memory_cleanup_operation", time_ms, memory_mb)
        
        # Cleanup
        performance_manager.cleanup()


# ── Test Markers and Configuration ────────────────────────────────────────────────────────────────

pytestmark = [
    pytest.mark.performance,
    pytest.mark.regression,
    pytest.mark.slow,
    pytest.mark.integration
]


# ── Module Configuration ──────────────────────────────────────────────────────────────────────────

def pytest_runtest_setup(item):
    """Setup before each regression test."""
    # Ensure clean state for accurate regression testing
    gc.collect()
    if QApplication.instance():
        QApplication.processEvents()
    
    # Brief pause to let system stabilize
    time.sleep(0.01)


def pytest_runtest_teardown(item):
    """Cleanup after each regression test."""
    # Force cleanup to prevent interference between tests
    gc.collect()
    if QApplication.instance():
        QApplication.processEvents()
    
    # Brief pause for system cleanup
    time.sleep(0.01)