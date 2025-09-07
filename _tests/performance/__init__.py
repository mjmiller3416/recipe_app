"""Performance Testing Package for RecipeBrowser Architecture

This package provides comprehensive performance validation tools for the refactored
RecipeBrowser coordinator architecture, ensuring that performance requirements are
met and maintained over time.

Key Components:
- recipe_browser_performance_validation: Core performance validation tests
- coordinator_performance_benchmarks: Detailed coordinator-specific benchmarks  
- performance_regression_tests: Regression testing against baselines
- run_performance_validation: Unified test runner and reporting

Performance Requirements Validated:
- Recipe loading under 200ms for 11 recipes
- Filter operations under 100ms response time
- Memory efficiency through object pooling
- Coordinator communication overhead < 10ms
- Cache hit rates > 30% for repeated operations
- Object pool hit rates > 20% for recipe cards
- No memory leaks during stress testing
- Smooth progressive rendering for large datasets

Usage:
    # Quick validation
    python _tests/performance/run_performance_validation.py --quick
    
    # Comprehensive validation
    python _tests/performance/run_performance_validation.py --comprehensive --report
    
    # Regression testing
    python _tests/performance/run_performance_validation.py --regression --compare
"""

# Version information
__version__ = "1.0.0"
__author__ = "RecipeBrowser Performance Team"

# Performance validation constants
PERFORMANCE_REQUIREMENTS = {
    "recipe_loading_ms": 200,           # Core requirement: under 200ms
    "filter_operation_ms": 100,         # Filter response under 100ms
    "coordinator_communication_ms": 10,  # Coordinator overhead under 10ms
    "min_cache_hit_rate": 30.0,         # Minimum cache effectiveness
    "min_pool_hit_rate": 20.0,          # Minimum object pool efficiency
    "max_memory_growth_mb": 20.0,       # Maximum acceptable memory growth
}

# Test configuration
TEST_CONFIG = {
    "standard_recipe_count": 11,        # Standard test dataset size
    "stress_test_recipe_count": 200,    # Stress test dataset size
    "performance_timeout_seconds": 30,  # Test timeout
    "regression_threshold_percent": 20, # Acceptable regression threshold
}

# Export key classes and functions for external use
from .run_performance_validation import PerformanceValidationRunner

__all__ = [
    "PerformanceValidationRunner",
    "PERFORMANCE_REQUIREMENTS", 
    "TEST_CONFIG"
]