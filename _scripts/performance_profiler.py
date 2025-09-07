"""Performance Profiler for RecipeBrowserView Architecture

This script provides comprehensive performance analysis for the RecipeBrowserView
and RecipeBrowserViewModel implementation, measuring loading times, memory usage,
and UI rendering performance.
"""

import gc
import time
import tracemalloc
from contextlib import contextmanager
from typing import Dict, List, Tuple

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from app.core.database.db import create_session
from app.core.services.recipe_service import RecipeService
from app.core.dtos.recipe_dtos import RecipeFilterDTO
from app.ui.view_models.recipe_browser_view_model import RecipeBrowserViewModel
from app.ui.views.recipe_browser.recipe_browser_view import RecipeBrowserView


class PerformanceProfiler:
    """Comprehensive performance profiler for recipe browser components."""

    def __init__(self):
        self.results = {}

    @contextmanager
    def profile_memory(self, operation_name: str):
        """Context manager to profile memory usage of an operation."""
        tracemalloc.start()
        gc.collect()  # Clean slate

        start_time = time.perf_counter()

        try:
            yield
        finally:
            end_time = time.perf_counter()

            # Memory measurements
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            # Store results
            self.results[operation_name] = {
                'duration': end_time - start_time,
                'peak_memory': peak / 1024 / 1024,  # MB
                'current_memory': current / 1024 / 1024,  # MB
            }

    def profile_database_queries(self) -> Dict[str, float]:
        """Profile database query performance."""
        session = create_session()
        service = RecipeService(session)

        # Test different query scenarios
        query_results = {}

        # Basic recipe loading
        with self.profile_memory("db_load_all_recipes"):
            filter_dto = RecipeFilterDTO()
            recipes = service.list_filtered(filter_dto)
            query_results['recipe_count'] = len(recipes)

        # Category filtering
        with self.profile_memory("db_filter_by_category"):
            filter_dto = RecipeFilterDTO(recipe_category="Breakfast")
            breakfast_recipes = service.list_filtered(filter_dto)
            query_results['breakfast_count'] = len(breakfast_recipes)

        # Search with filtering
        with self.profile_memory("db_search_with_filter"):
            filter_dto = RecipeFilterDTO(
                search_term="chicken",
                recipe_category="Dinner",
                sort_by="recipe_name",
                sort_order="asc"
            )
            search_results = service.list_filtered(filter_dto)
            query_results['search_results'] = len(search_results)

        # Favorites only
        with self.profile_memory("db_favorites_only"):
            filter_dto = RecipeFilterDTO(favorites_only=True)
            favorites = service.list_filtered(filter_dto)
            query_results['favorites_count'] = len(favorites)

        session.close()
        return query_results

    def profile_viewmodel_operations(self) -> Dict[str, float]:
        """Profile ViewModel operations."""
        vm_results = {}

        # ViewModel initialization
        with self.profile_memory("vm_initialization"):
            vm = RecipeBrowserViewModel()

        # Recipe loading
        with self.profile_memory("vm_load_recipes"):
            success = vm.load_recipes()
            vm_results['load_success'] = success
            vm_results['recipe_count'] = vm.recipe_count

        # Filter operations
        with self.profile_memory("vm_category_filter"):
            vm.update_category_filter("Breakfast")

        with self.profile_memory("vm_sort_change"):
            vm.update_sort_option("Newest")

        with self.profile_memory("vm_favorites_filter"):
            vm.update_favorites_filter(True)

        # Search operations
        with self.profile_memory("vm_search_operation"):
            vm.search_recipes("chicken soup")

        with self.profile_memory("vm_clear_search"):
            vm.clear_search()

        # Selection mode toggle
        with self.profile_memory("vm_selection_mode"):
            vm.set_selection_mode(True)
            vm.set_selection_mode(False)

        # Cleanup
        vm.reset_browser_state()
        del vm

        return vm_results

    def profile_ui_rendering(self, app: QApplication) -> Dict[str, float]:
        """Profile UI rendering performance."""
        ui_results = {}

        # View initialization
        with self.profile_memory("ui_view_init"):
            view = RecipeBrowserView(selection_mode=False)

        # Show and render
        with self.profile_memory("ui_show_view"):
            view.show()
            app.processEvents()  # Process paint events

        # Recipe loading and display
        with self.profile_memory("ui_load_display"):
            view.after_navigate_to("/recipes/browse", {})
            app.processEvents()
            ui_results['recipes_displayed'] = view.get_current_recipe_count()

        # Filter changes
        with self.profile_memory("ui_filter_change"):
            view._on_category_filter_changed("Breakfast")
            app.processEvents()

        with self.profile_memory("ui_sort_change"):
            view._on_sort_option_changed("Newest")
            app.processEvents()

        # Search operations
        with self.profile_memory("ui_search_operation"):
            view.search_recipes("chicken")
            app.processEvents()

        # Large dataset simulation (if we have enough recipes)
        recipe_count = view.get_current_recipe_count()
        if recipe_count > 50:
            with self.profile_memory("ui_large_dataset"):
                view.refresh_recipes()
                app.processEvents()

        # Cleanup
        view.hide()
        view.deleteLater()
        app.processEvents()

        return ui_results

    def run_stress_test(self, iterations: int = 5) -> Dict[str, List[float]]:
        """Run stress test with multiple iterations."""
        stress_results = {
            'load_times': [],
            'filter_times': [],
            'search_times': []
        }

        for i in range(iterations):
            print(f"Stress test iteration {i+1}/{iterations}")

            # Test ViewModel loading
            start_time = time.perf_counter()
            vm = RecipeBrowserViewModel()
            vm.load_recipes()
            load_time = time.perf_counter() - start_time
            stress_results['load_times'].append(load_time)

            # Filter performance
            start_time = time.perf_counter()
            vm.update_category_filter("Breakfast")
            vm.update_sort_option("Newest")
            filter_time = time.perf_counter() - start_time
            stress_results['filter_times'].append(filter_time)

            # Search performance
            start_time = time.perf_counter()
            vm.search_recipes("chicken soup")
            search_time = time.perf_counter() - start_time
            stress_results['search_times'].append(search_time)

            # Cleanup
            vm.reset_browser_state()
            del vm
            gc.collect()

        return stress_results

    def generate_report(self) -> str:
        """Generate comprehensive performance report."""
        report = []
        report.append("=" * 80)
        report.append("RECIPE BROWSER PERFORMANCE ANALYSIS REPORT")
        report.append("=" * 80)
        report.append("")

        # Database Performance
        report.append("DATABASE QUERY PERFORMANCE:")
        report.append("-" * 40)
        for operation, metrics in self.results.items():
            if operation.startswith('db_'):
                name = operation.replace('db_', '').replace('_', ' ').title()
                duration = metrics['duration'] * 1000  # Convert to ms
                memory = metrics['peak_memory']
                report.append(f"{name:25s}: {duration:8.2f}ms  Memory: {memory:6.2f}MB")
        report.append("")

        # ViewModel Performance
        report.append("VIEWMODEL OPERATION PERFORMANCE:")
        report.append("-" * 40)
        for operation, metrics in self.results.items():
            if operation.startswith('vm_'):
                name = operation.replace('vm_', '').replace('_', ' ').title()
                duration = metrics['duration'] * 1000
                memory = metrics['peak_memory']
                report.append(f"{name:25s}: {duration:8.2f}ms  Memory: {memory:6.2f}MB")
        report.append("")

        # UI Performance
        report.append("UI RENDERING PERFORMANCE:")
        report.append("-" * 40)
        for operation, metrics in self.results.items():
            if operation.startswith('ui_'):
                name = operation.replace('ui_', '').replace('_', ' ').title()
                duration = metrics['duration'] * 1000
                memory = metrics['peak_memory']
                report.append(f"{name:25s}: {duration:8.2f}ms  Memory: {memory:6.2f}MB")
        report.append("")

        # Performance Summary
        report.append("PERFORMANCE SUMMARY:")
        report.append("-" * 40)

        # Find critical operations
        db_operations = [(k, v) for k, v in self.results.items() if k.startswith('db_')]
        vm_operations = [(k, v) for k, v in self.results.items() if k.startswith('vm_')]
        ui_operations = [(k, v) for k, v in self.results.items() if k.startswith('ui_')]

        if db_operations:
            slowest_db = max(db_operations, key=lambda x: x[1]['duration'])
            report.append(f"Slowest DB operation    : {slowest_db[0]} ({slowest_db[1]['duration']*1000:.2f}ms)")

        if vm_operations:
            slowest_vm = max(vm_operations, key=lambda x: x[1]['duration'])
            report.append(f"Slowest ViewModel op    : {slowest_vm[0]} ({slowest_vm[1]['duration']*1000:.2f}ms)")

        if ui_operations:
            slowest_ui = max(ui_operations, key=lambda x: x[1]['duration'])
            report.append(f"Slowest UI operation    : {slowest_ui[0]} ({slowest_ui[1]['duration']*1000:.2f}ms)")

        # Peak memory usage
        max_memory = max((m['peak_memory'] for m in self.results.values()), default=0)
        report.append(f"Peak memory usage       : {max_memory:.2f}MB")

        report.append("")
        return "\n".join(report)

    def print_optimization_recommendations(self):
        """Print specific optimization recommendations based on results."""
        print("\n" + "=" * 80)
        print("OPTIMIZATION RECOMMENDATIONS")
        print("=" * 80)

        # Analyze results and provide specific recommendations
        slow_operations = [(k, v) for k, v in self.results.items()
                          if v['duration'] > 0.1]  # > 100ms

        high_memory_operations = [(k, v) for k, v in self.results.items()
                                 if v['peak_memory'] > 50]  # > 50MB

        if slow_operations:
            print("\n🐌 SLOW OPERATIONS (>100ms):")
            for op, metrics in slow_operations:
                duration = metrics['duration'] * 1000
                print(f"   • {op}: {duration:.2f}ms")

                # Specific recommendations
                if op.startswith('db_'):
                    print("     → Consider query optimization, indexing, or result caching")
                elif op.startswith('vm_'):
                    print("     → Consider data caching, lazy loading, or background processing")
                elif op.startswith('ui_'):
                    print("     → Consider widget recycling, virtual scrolling, or progressive rendering")

        if high_memory_operations:
            print("\n🧠 HIGH MEMORY OPERATIONS (>50MB):")
            for op, metrics in high_memory_operations:
                memory = metrics['peak_memory']
                print(f"   • {op}: {memory:.2f}MB")
                print("     → Consider object pooling, lazy loading, or data structure optimization")

        print("\n💡 GENERAL RECOMMENDATIONS:")
        print("   • Implement recipe card object pooling for large datasets")
        print("   • Add intelligent caching in ViewModel layer")
        print("   • Consider lazy loading for recipe images")
        print("   • Implement virtual scrolling for 1000+ recipes")
        print("   • Add progressive loading with pagination")
        print("   • Optimize database queries with proper indexing")
        print("   • Consider background data loading with loading indicators")


def main():
    """Main function to run performance analysis."""
    print("Starting Recipe Browser Performance Analysis...")

    # Initialize Qt Application
    app = QApplication([])

    # Create profiler
    profiler = PerformanceProfiler()

    try:
        # Run performance tests
        print("\n1. Profiling database operations...")
        db_results = profiler.profile_database_queries()
        print(f"   Loaded {db_results.get('recipe_count', 0)} total recipes")

        print("\n2. Profiling ViewModel operations...")
        vm_results = profiler.profile_viewmodel_operations()
        print(f"   ViewModel loaded {vm_results.get('recipe_count', 0)} recipes")

        print("\n3. Profiling UI rendering...")
        ui_results = profiler.profile_ui_rendering(app)
        print(f"   UI displayed {ui_results.get('recipes_displayed', 0)} recipes")

        print("\n4. Running stress test...")
        stress_results = profiler.run_stress_test(5)  # 5 iterations

        # Generate and print report
        print("\n" + profiler.generate_report())

        # Print stress test results
        if stress_results['load_times']:
            avg_load = sum(stress_results['load_times']) / len(stress_results['load_times'])
            max_load = max(stress_results['load_times'])
            print("STRESS TEST RESULTS:")
            print("-" * 40)
            print(f"Average load time       : {avg_load*1000:.2f}ms")
            print(f"Maximum load time       : {max_load*1000:.2f}ms")

            avg_filter = sum(stress_results['filter_times']) / len(stress_results['filter_times'])
            avg_search = sum(stress_results['search_times']) / len(stress_results['search_times'])
            print(f"Average filter time     : {avg_filter*1000:.2f}ms")
            print(f"Average search time     : {avg_search*1000:.2f}ms")

        # Print recommendations
        profiler.print_optimization_recommendations()

    except Exception as e:
        print(f"Error during profiling: {e}")
        import traceback
        traceback.print_exc()
    finally:
        app.quit()


if __name__ == "__main__":
    main()
