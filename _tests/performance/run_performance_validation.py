"""Performance Validation Test Runner

Comprehensive test runner for RecipeBrowser performance validation and benchmarking.
This script provides a unified interface to run all performance tests and generate
comprehensive performance reports.

Usage:
    python run_performance_validation.py [options]

Options:
    --quick         Run quick validation tests only (skip stress tests)
    --comprehensive Run all performance tests including stress tests
    --benchmarks    Run detailed coordinator benchmarks
    --regression    Run regression tests against baselines
    --report        Generate detailed performance report
    --baseline      Establish new performance baselines
    --compare       Compare with previous test results

The runner executes tests in logical groups and provides consolidated reporting
to help identify performance issues and track improvements over time.
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

import pytest
from PySide6.QtWidgets import QApplication

from _dev_tools import DebugLogger


class PerformanceValidationRunner:
    """Comprehensive performance validation test runner."""
    
    def __init__(self, args):
        self.args = args
        self.results = {}
        self.start_time = datetime.now()
        
    def run_validation(self) -> Dict[str, Any]:
        """Run performance validation based on arguments."""
        DebugLogger.log("="*80, "info")
        DebugLogger.log("RECIPEBROWSER PERFORMANCE VALIDATION", "info")
        DebugLogger.log(f"Started: {self.start_time.isoformat()}", "info")
        DebugLogger.log("="*80, "info")
        
        # Ensure Qt application exists
        if not QApplication.instance():
            app = QApplication([])
        
        try:
            # Run selected test suites
            if self.args.quick or not any([self.args.comprehensive, self.args.benchmarks, self.args.regression]):
                self._run_quick_validation()
            
            if self.args.comprehensive:
                self._run_comprehensive_validation()
            
            if self.args.benchmarks:
                self._run_benchmark_tests()
            
            if self.args.regression:
                self._run_regression_tests()
            
            # Generate reports
            if self.args.report:
                self._generate_performance_report()
            
            if self.args.baseline:
                self._establish_baselines()
            
            if self.args.compare:
                self._compare_with_previous()
            
        except Exception as e:
            DebugLogger.log(f"Performance validation failed: {e}", "error")
            self.results['error'] = str(e)
            return self.results
        
        # Calculate total runtime
        end_time = datetime.now()
        total_runtime = (end_time - self.start_time).total_seconds()
        
        self.results['summary'] = {
            'start_time': self.start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'total_runtime_seconds': total_runtime,
            'tests_run': self._count_tests_run(),
            'overall_status': self._determine_overall_status()
        }
        
        # Log final summary
        self._log_final_summary()
        
        return self.results
    
    def _run_quick_validation(self):
        """Run quick performance validation tests."""
        DebugLogger.log("Running quick performance validation...", "info")
        
        # Core performance requirements (200ms recipe loading)
        result = pytest.main([
            "-xvs",
            "_tests/performance/recipe_browser_performance_validation.py::TestRecipeLoadingPerformance::test_baseline_11_recipe_loading_under_200ms",
            "--tb=short"
        ])
        
        self.results['quick_validation'] = {
            'exit_code': result,
            'status': 'PASS' if result == 0 else 'FAIL',
            'description': 'Core 200ms recipe loading requirement'
        }
        
        # Filter operation performance
        result = pytest.main([
            "-xvs",
            "_tests/performance/recipe_browser_performance_validation.py::TestFilterOperationPerformance::test_category_filter_response_time",
            "--tb=short"
        ])
        
        self.results['filter_performance'] = {
            'exit_code': result,
            'status': 'PASS' if result == 0 else 'FAIL',
            'description': 'Filter operation response time under 100ms'
        }
    
    def _run_comprehensive_validation(self):
        """Run comprehensive performance validation."""
        DebugLogger.log("Running comprehensive performance validation...", "info")
        
        # Run all performance validation tests
        result = pytest.main([
            "-v",
            "_tests/performance/recipe_browser_performance_validation.py",
            "--tb=short",
            "-m", "performance"
        ])
        
        self.results['comprehensive_validation'] = {
            'exit_code': result,
            'status': 'PASS' if result == 0 else 'FAIL',
            'description': 'All performance validation tests',
            'includes': [
                'Recipe loading performance',
                'Filter operation performance', 
                'Memory usage validation',
                'Coordinator communication overhead',
                'Stress testing',
                'Cache effectiveness'
            ]
        }
    
    def _run_benchmark_tests(self):
        """Run detailed coordinator benchmarks."""
        DebugLogger.log("Running coordinator performance benchmarks...", "info")
        
        result = pytest.main([
            "-v",
            "_tests/performance/coordinator_performance_benchmarks.py",
            "--tb=short",
            "-m", "benchmarks"
        ])
        
        self.results['benchmarks'] = {
            'exit_code': result,
            'status': 'PASS' if result == 0 else 'FAIL',
            'description': 'Detailed coordinator benchmarks',
            'includes': [
                'FilterCoordinator throughput',
                'RenderingCoordinator efficiency',
                'EventCoordinator routing performance',
                'PerformanceManager pool utilization',
                'ViewModel integration overhead'
            ]
        }
    
    def _run_regression_tests(self):
        """Run performance regression tests."""
        DebugLogger.log("Running performance regression tests...", "info")
        
        result = pytest.main([
            "-v",
            "_tests/performance/performance_regression_tests.py",
            "--tb=short",
            "-m", "regression"
        ])
        
        self.results['regression_tests'] = {
            'exit_code': result,
            'status': 'PASS' if result == 0 else 'FAIL',
            'description': 'Performance regression testing against baselines',
            'includes': [
                'Recipe loading regression',
                'Filter operation regression',
                'Memory leak detection',
                'Cache efficiency regression',
                'Stress testing regression'
            ]
        }
    
    def _generate_performance_report(self):
        """Generate comprehensive performance report."""
        DebugLogger.log("Generating comprehensive performance report...", "info")
        
        # Run the comprehensive report test
        result = pytest.main([
            "-xvs",
            "_tests/performance/recipe_browser_performance_validation.py::TestPerformanceAnalysisAndReporting::test_comprehensive_performance_report",
            "--tb=short"
        ])
        
        self.results['performance_report'] = {
            'exit_code': result,
            'status': 'PASS' if result == 0 else 'FAIL',
            'description': 'Comprehensive performance analysis and reporting'
        }
        
        # Try to load and include performance metrics if available
        try:
            # Look for performance metrics files
            metrics_files = list(Path(".").glob("*performance_metrics*.json"))
            if metrics_files:
                latest_metrics = max(metrics_files, key=lambda p: p.stat().st_mtime)
                with open(latest_metrics) as f:
                    metrics_data = json.load(f)
                self.results['detailed_metrics'] = metrics_data
        except Exception as e:
            DebugLogger.log(f"Could not load detailed metrics: {e}", "debug")
    
    def _establish_baselines(self):
        """Establish new performance baselines."""
        DebugLogger.log("Establishing new performance baselines...", "info")
        
        # Run baseline establishment tests
        result = pytest.main([
            "-v",
            "_tests/performance/performance_regression_tests.py::TestCorePerformanceRegression",
            "--tb=short"
        ])
        
        self.results['baseline_establishment'] = {
            'exit_code': result,
            'status': 'PASS' if result == 0 else 'FAIL',
            'description': 'Establishment of new performance baselines'
        }
    
    def _compare_with_previous(self):
        """Compare with previous test results."""
        DebugLogger.log("Comparing with previous results...", "info")
        
        try:
            # Look for previous results
            results_files = list(Path(".").glob("performance_validation_results_*.json"))
            if len(results_files) < 2:
                self.results['comparison'] = {
                    'status': 'SKIP',
                    'description': 'Not enough historical data for comparison'
                }
                return
            
            # Get the two most recent results
            sorted_files = sorted(results_files, key=lambda p: p.stat().st_mtime, reverse=True)
            previous_file = sorted_files[1]  # Second most recent
            
            with open(previous_file) as f:
                previous_results = json.load(f)
            
            # Compare key metrics
            comparison = self._compare_results(previous_results, self.results)
            
            self.results['comparison'] = {
                'status': 'COMPLETE',
                'description': f'Comparison with results from {previous_file.name}',
                'comparison_data': comparison
            }
            
        except Exception as e:
            self.results['comparison'] = {
                'status': 'ERROR',
                'description': f'Error comparing results: {e}'
            }
    
    def _compare_results(self, previous: Dict, current: Dict) -> Dict:
        """Compare current results with previous results."""
        comparison = {
            'improvements': [],
            'regressions': [],
            'new_tests': [],
            'removed_tests': []
        }
        
        # Compare test outcomes
        prev_tests = set(previous.keys()) if previous else set()
        curr_tests = set(current.keys())
        
        comparison['new_tests'] = list(curr_tests - prev_tests)
        comparison['removed_tests'] = list(prev_tests - curr_tests)
        
        # Compare common tests
        for test_name in (prev_tests & curr_tests):
            if isinstance(previous.get(test_name), dict) and isinstance(current.get(test_name), dict):
                prev_status = previous[test_name].get('status')
                curr_status = current[test_name].get('status')
                
                if prev_status != curr_status:
                    if curr_status == 'PASS' and prev_status != 'PASS':
                        comparison['improvements'].append(test_name)
                    elif prev_status == 'PASS' and curr_status != 'PASS':
                        comparison['regressions'].append(test_name)
        
        return comparison
    
    def _count_tests_run(self) -> int:
        """Count total number of tests run."""
        count = 0
        for result in self.results.values():
            if isinstance(result, dict) and 'exit_code' in result:
                count += 1
        return count
    
    def _determine_overall_status(self) -> str:
        """Determine overall validation status."""
        statuses = []
        for result in self.results.values():
            if isinstance(result, dict) and 'status' in result:
                statuses.append(result['status'])
        
        if not statuses:
            return 'NO_TESTS'
        elif all(s == 'PASS' for s in statuses):
            return 'ALL_PASS'
        elif any(s == 'FAIL' for s in statuses):
            return 'SOME_FAILURES'
        else:
            return 'MIXED'
    
    def _log_final_summary(self):
        """Log final validation summary."""
        summary = self.results.get('summary', {})
        
        DebugLogger.log("="*80, "info")
        DebugLogger.log("PERFORMANCE VALIDATION SUMMARY", "info")
        DebugLogger.log("="*80, "info")
        DebugLogger.log(f"Runtime: {summary.get('total_runtime_seconds', 0):.1f} seconds", "info")
        DebugLogger.log(f"Tests Run: {summary.get('tests_run', 0)}", "info")
        DebugLogger.log(f"Overall Status: {summary.get('overall_status', 'UNKNOWN')}", "info")
        DebugLogger.log("", "info")
        
        # Log individual test results
        for test_name, result in self.results.items():
            if isinstance(result, dict) and 'status' in result and test_name != 'summary':
                status = result['status']
                description = result.get('description', test_name)
                
                status_symbol = "✓" if status == "PASS" else "✗" if status == "FAIL" else "○"
                DebugLogger.log(f"{status_symbol} {description}: {status}", "info")
        
        # Log comparison if available
        if 'comparison' in self.results:
            comp = self.results['comparison']
            if comp['status'] == 'COMPLETE' and 'comparison_data' in comp:
                data = comp['comparison_data']
                DebugLogger.log("", "info")
                DebugLogger.log("COMPARISON WITH PREVIOUS RESULTS:", "info")
                if data['improvements']:
                    DebugLogger.log(f"Improvements: {', '.join(data['improvements'])}", "info")
                if data['regressions']:
                    DebugLogger.log(f"Regressions: {', '.join(data['regressions'])}", "warning")
                if data['new_tests']:
                    DebugLogger.log(f"New Tests: {', '.join(data['new_tests'])}", "info")
        
        DebugLogger.log("="*80, "info")
        
        # Save results to file
        self._save_results()
    
    def _save_results(self):
        """Save validation results to file."""
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        filename = f"performance_validation_results_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            DebugLogger.log(f"Results saved to: {filename}", "info")
        except Exception as e:
            DebugLogger.log(f"Error saving results: {e}", "error")


def main():
    """Main entry point for performance validation runner."""
    parser = argparse.ArgumentParser(
        description="RecipeBrowser Performance Validation Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_performance_validation.py --quick
      Run quick validation tests only
      
  python run_performance_validation.py --comprehensive --report
      Run all tests and generate detailed report
      
  python run_performance_validation.py --regression --compare
      Run regression tests and compare with previous results
      
  python run_performance_validation.py --benchmarks --baseline
      Run benchmarks and establish new baselines
        """
    )
    
    parser.add_argument(
        '--quick', 
        action='store_true',
        help='Run quick validation tests only (core requirements)'
    )
    
    parser.add_argument(
        '--comprehensive',
        action='store_true', 
        help='Run comprehensive performance validation tests'
    )
    
    parser.add_argument(
        '--benchmarks',
        action='store_true',
        help='Run detailed coordinator performance benchmarks'
    )
    
    parser.add_argument(
        '--regression',
        action='store_true',
        help='Run performance regression tests against baselines'
    )
    
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate comprehensive performance report'
    )
    
    parser.add_argument(
        '--baseline',
        action='store_true',
        help='Establish new performance baselines'
    )
    
    parser.add_argument(
        '--compare',
        action='store_true',
        help='Compare results with previous test runs'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output file for results (default: auto-generated)'
    )
    
    args = parser.parse_args()
    
    # If no specific options given, run quick validation
    if not any([args.quick, args.comprehensive, args.benchmarks, args.regression, args.report, args.baseline, args.compare]):
        args.quick = True
    
    # Create and run validator
    runner = PerformanceValidationRunner(args)
    results = runner.run_validation()
    
    # Exit with appropriate code
    overall_status = results.get('summary', {}).get('overall_status', 'UNKNOWN')
    if overall_status == 'ALL_PASS':
        sys.exit(0)
    elif overall_status in ['SOME_FAILURES', 'MIXED']:
        sys.exit(1)
    else:
        sys.exit(2)  # Unknown or error state


if __name__ == "__main__":
    main()