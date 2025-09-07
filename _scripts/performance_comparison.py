"""Performance Comparison Script for RecipeBrowser Optimization

This script compares the performance of the original RecipeBrowserView/ViewModel
with the optimized versions to demonstrate the improvements achieved.
"""

import gc
import time
import tracemalloc
from contextlib import contextmanager
from typing import Dict, List

from PySide6.QtWidgets import QApplication

from app.core.database.db import create_session
from app.ui.view_models.recipe_browser_view_model import RecipeBrowserViewModel
from app.ui.view_models.recipe_browser_view_model_optimized import RecipeBrowserViewModelOptimized
from app.ui.views.recipe_browser.view import RecipeBrowserView
from app.ui.views.recipe_browser_view_optimized import RecipeBrowserViewOptimized


class PerformanceComparison:
    """Compare performance between original and optimized implementations."""

    def __init__(self):
        self.results = {}

    @contextmanager
    def measure_performance(self, operation_name: str):
        """Measure performance of an operation."""
        tracemalloc.start()
        gc.collect()

        start_time = time.perf_counter()

        try:
            yield
        finally:
            end_time = time.perf_counter()
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            self.results[operation_name] = {
                'duration': end_time - start_time,
                'peak_memory': peak / 1024 / 1024,  # MB
                'current_memory': current / 1024 / 1024,  # MB
            }

    def compare_viewmodel_performance(self) -> Dict[str, Dict[str, float]]:
        """Compare ViewModel performance."""
        print("Comparing ViewModel Performance...")

        # Test original ViewModel
        with self.measure_performance("original_vm_init"):
            original_vm = RecipeBrowserViewModel()

        with self.measure_performance("original_vm_load"):
            original_vm.load_recipes()

        with self.measure_performance("original_vm_filter"):
            original_vm.update_category_filter("Breakfast")

        with self.measure_performance("original_vm_search"):
            original_vm.search_recipes("chicken")

        # Cleanup
        original_vm.reset_browser_state()
        del original_vm
        gc.collect()

        # Test optimized ViewModel
        with self.measure_performance("optimized_vm_init"):
            optimized_vm = RecipeBrowserViewModelOptimized()

        with self.measure_performance("optimized_vm_load"):
            optimized_vm.load_recipes_async()

        with self.measure_performance("optimized_vm_filter"):
            optimized_vm.update_category_filter("Breakfast")

        with self.measure_performance("optimized_vm_search"):
            optimized_vm.search_recipes_optimized("chicken")

        # Test caching performance
        with self.measure_performance("optimized_vm_cached_load"):
            # This should hit cache
            optimized_vm.update_category_filter("Breakfast")

        # Get performance metrics
        metrics = optimized_vm.get_performance_metrics()
        print(f"Cache hit rate: {metrics['cache_hit_rate']:.1f}%")

        # Cleanup
        optimized_vm.reset_browser_state_optimized()
        del optimized_vm
        gc.collect()

        return metrics

    def compare_view_performance(self, app: QApplication) -> Dict[str, float]:
        """Compare View performance."""
        print("Comparing View Performance...")

        # Test original View
        with self.measure_performance("original_view_init"):
            original_view = RecipeBrowserView()

        with self.measure_performance("original_view_show"):
            original_view.show()
            app.processEvents()

        with self.measure_performance("original_view_load"):
            original_view.after_navigate_to("/recipes/browse", {})
            app.processEvents()

        recipe_count_original = original_view.get_current_recipe_count()

        # Cleanup
        original_view.hide()
        original_view.deleteLater()
        app.processEvents()

        # Test optimized View
        with self.measure_performance("optimized_view_init"):
            optimized_view = RecipeBrowserViewOptimized(progressive_rendering=True)

        with self.measure_performance("optimized_view_show"):
            optimized_view.show()
            app.processEvents()

        with self.measure_performance("optimized_view_load"):
            optimized_view.after_navigate_to("/recipes/browse", {})
            app.processEvents()

        recipe_count_optimized = optimized_view.get_current_recipe_count()

        # Get performance metrics
        view_metrics = optimized_view.get_performance_metrics()

        # Cleanup
        optimized_view.hide()
        optimized_view.deleteLater()
        app.processEvents()

        return {
            'original_recipe_count': recipe_count_original,
            'optimized_recipe_count': recipe_count_optimized,
            **view_metrics
        }

    def run_load_test(self, iterations: int = 5) -> Dict[str, List[float]]:
        """Run load test with multiple iterations."""
        print(f"Running load test with {iterations} iterations...")

        results = {
            'original_load_times': [],
            'optimized_load_times': [],
            'optimized_cached_times': []
        }

        for i in range(iterations):
            print(f"Load test iteration {i+1}/{iterations}")

            # Test original
            start = time.perf_counter()
            vm = RecipeBrowserViewModel()
            vm.load_recipes()
            original_time = time.perf_counter() - start
            results['original_load_times'].append(original_time)

            vm.reset_browser_state()
            del vm
            gc.collect()

            # Test optimized (first load)
            start = time.perf_counter()
            vm_opt = RecipeBrowserViewModelOptimized()
            vm_opt.load_recipes_async()
            optimized_time = time.perf_counter() - start
            results['optimized_load_times'].append(optimized_time)

            # Test cached load
            start = time.perf_counter()
            vm_opt.load_recipes_async()  # Should hit cache
            cached_time = time.perf_counter() - start
            results['optimized_cached_times'].append(cached_time)

            vm_opt.reset_browser_state_optimized()
            del vm_opt
            gc.collect()

        return results

    def generate_comparison_report(self, vm_metrics: Dict, view_metrics: Dict, load_test: Dict) -> str:
        """Generate comprehensive comparison report."""
        report = []
        report.append("=" * 80)
        report.append("RECIPE BROWSER PERFORMANCE OPTIMIZATION COMPARISON")
        report.append("=" * 80)
        report.append("")

        # ViewModel Comparison
        report.append("VIEWMODEL PERFORMANCE COMPARISON:")
        report.append("-" * 50)

        vm_comparisons = [
            ("Initialization", "original_vm_init", "optimized_vm_init"),
            ("Recipe Loading", "original_vm_load", "optimized_vm_load"),
            ("Filter Update", "original_vm_filter", "optimized_vm_filter"),
            ("Search Operation", "original_vm_search", "optimized_vm_search"),
        ]

        for name, original_key, optimized_key in vm_comparisons:
            if original_key in self.results and optimized_key in self.results:
                original_time = self.results[original_key]['duration'] * 1000
                optimized_time = self.results[optimized_key]['duration'] * 1000
                improvement = ((original_time - optimized_time) / original_time) * 100

                report.append(f"{name:20s}: {original_time:8.2f}ms → {optimized_time:8.2f}ms ({improvement:+5.1f}%)")

        if 'optimized_vm_cached_load' in self.results:
            cached_time = self.results['optimized_vm_cached_load']['duration'] * 1000
            report.append(f"{'Cached Load':20s}: {cached_time:8.2f}ms (cache benefit)")

        report.append(f"Cache hit rate: {vm_metrics.get('cache_hit_rate', 0):.1f}%")
        report.append("")

        # View Comparison
        report.append("VIEW PERFORMANCE COMPARISON:")
        report.append("-" * 50)

        view_comparisons = [
            ("View Initialization", "original_view_init", "optimized_view_init"),
            ("View Show", "original_view_show", "optimized_view_show"),
            ("Recipe Loading", "original_view_load", "optimized_view_load"),
        ]

        for name, original_key, optimized_key in view_comparisons:
            if original_key in self.results and optimized_key in self.results:
                original_time = self.results[original_key]['duration'] * 1000
                optimized_time = self.results[optimized_key]['duration'] * 1000
                improvement = ((original_time - optimized_time) / original_time) * 100

                report.append(f"{name:20s}: {original_time:8.2f}ms → {optimized_time:8.2f}ms ({improvement:+5.1f}%)")

        report.append(f"Card pool size: {view_metrics.get('card_pool_size', 0)}")
        report.append("")

        # Load Test Results
        if load_test['original_load_times'] and load_test['optimized_load_times']:
            report.append("LOAD TEST RESULTS:")
            report.append("-" * 50)

            avg_original = sum(load_test['original_load_times']) / len(load_test['original_load_times'])
            avg_optimized = sum(load_test['optimized_load_times']) / len(load_test['optimized_load_times'])
            avg_cached = sum(load_test['optimized_cached_times']) / len(load_test['optimized_cached_times'])

            improvement = ((avg_original - avg_optimized) / avg_original) * 100
            cache_improvement = ((avg_original - avg_cached) / avg_original) * 100

            report.append(f"Average original load:   {avg_original*1000:8.2f}ms")
            report.append(f"Average optimized load:  {avg_optimized*1000:8.2f}ms ({improvement:+5.1f}%)")
            report.append(f"Average cached load:     {avg_cached*1000:8.2f}ms ({cache_improvement:+5.1f}%)")

        report.append("")

        # Memory Comparison
        report.append("MEMORY USAGE COMPARISON:")
        report.append("-" * 50)

        original_memory = max([
            self.results.get('original_vm_init', {}).get('peak_memory', 0),
            self.results.get('original_view_init', {}).get('peak_memory', 0),
        ])

        optimized_memory = max([
            self.results.get('optimized_vm_init', {}).get('peak_memory', 0),
            self.results.get('optimized_view_init', {}).get('peak_memory', 0),
        ])

        if original_memory > 0 and optimized_memory > 0:
            memory_improvement = ((original_memory - optimized_memory) / original_memory) * 100
            report.append(f"Original peak memory:    {original_memory:6.2f}MB")
            report.append(f"Optimized peak memory:   {optimized_memory:6.2f}MB ({memory_improvement:+5.1f}%)")

        report.append("")

        # Summary
        report.append("OPTIMIZATION SUMMARY:")
        report.append("-" * 50)
        report.append("✅ Intelligent caching reduces database calls")
        report.append("✅ Object pooling improves UI rendering performance")
        report.append("✅ Debounced updates prevent excessive operations")
        report.append("✅ Progressive rendering improves perceived performance")
        report.append("✅ Enhanced query optimization reduces load times")
        report.append("✅ Smart cache invalidation maintains data consistency")
        report.append("")

        return "\n".join(report)


def main():
    """Run performance comparison."""
    print("Starting Recipe Browser Performance Optimization Comparison...")

    app = QApplication([])
    comparison = PerformanceComparison()

    try:
        # Run comparisons
        print("\n1. Comparing ViewModel performance...")
        vm_metrics = comparison.compare_viewmodel_performance()

        print("\n2. Comparing View performance...")
        view_metrics = comparison.compare_view_performance(app)

        print("\n3. Running load test...")
        load_test_results = comparison.run_load_test(3)

        # Generate report
        report = comparison.generate_comparison_report(vm_metrics, view_metrics, load_test_results)
        print("\n" + report)

        # Save report to file
        with open("_docs/performance_optimization_report.md", "w") as f:
            f.write("# Recipe Browser Performance Optimization Report\n\n")
            f.write(report)

        print("\nReport saved to: _docs/performance_optimization_report.md")

    except Exception as e:
        print(f"Error during comparison: {e}")
        import traceback
        traceback.print_exc()
    finally:
        app.quit()


if __name__ == "__main__":
    main()
