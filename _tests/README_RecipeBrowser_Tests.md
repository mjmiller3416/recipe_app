# Comprehensive RecipeBrowser Integration Tests

This directory contains comprehensive integration tests for the refactored RecipeBrowser system, validating all coordinator interactions and recipe domain functionality.

## Test Architecture Overview

The RecipeBrowser system has been refactored from 774 lines to 344 lines using a coordinator architecture. These tests validate that all components work together correctly while maintaining full functionality.

## New Architecture Components Tested

### Core Coordinators
- **PerformanceManager**: Object pooling and progressive rendering
- **EventCoordinator**: Debounced interactions and signal management
- **FilterCoordinator**: Recipe-specific filtering logic
- **RenderingCoordinator**: Recipe card creation and layout management
- **RecipeBrowserConfig**: Configuration management
- **Enhanced ViewModel**: Business logic and coordinator integration
- **Refactored View**: Coordinator orchestration and UI assembly

## Test Files Structure

### Integration Tests
- **`test_recipe_browser_integration.py`**: Main integration tests covering complete workflows
  - Complete recipe browsing workflows end-to-end
  - Coordinator communication and coordination
  - Recipe filtering with multiple coordinators
  - Selection mode and navigation workflows
  - Performance optimization integration
  - Error handling across coordinators
  - Memory management and cleanup

### Unit Tests for Coordinators
- **`test_performance_manager.py`**: PerformanceManager unit tests
  - Object pool creation and management
  - Widget pool creation and management
  - Progressive rendering coordination
  - Memory management and cleanup
  - Performance metrics tracking
  - Signal emissions and coordination

- **`test_event_coordinator.py`**: EventCoordinator unit tests
  - Debounced event handling with various strategies
  - Managed signal connection lifecycle
  - Priority-based event routing with filtering
  - Coordination patterns (search, filter, validation)
  - Multi-component event handling
  - Performance monitoring and metrics

- **`test_filter_coordinator.py`**: FilterCoordinator unit tests
  - Recipe category filtering with domain validation
  - Recipe sort option mapping and validation
  - Favorites-only filtering with state persistence
  - Search functionality with recipe-specific patterns
  - Combined filter operations with dependency management
  - Filter preset management for common use cases

- **`test_rendering_coordinator.py`**: RenderingCoordinator unit tests
  - Recipe card creation and configuration
  - Progressive rendering coordination
  - Selection mode handling for recipe cards
  - Layout management with FlowLayout integration
  - Recipe-specific performance optimizations
  - Card pool management and object recycling

- **`test_recipe_browser_coordinators.py`**: Cross-coordinator integration tests
  - Cross-coordinator communication patterns
  - Coordinator state synchronization
  - Event propagation between coordinators
  - Error handling across coordinator boundaries
  - Resource sharing and lifecycle management

### Configuration Tests
- **`test_config.py`**: RecipeBrowser configuration tests (already existing)
  - Configuration validation and defaults
  - Environment variable overrides
  - Factory methods for different configurations
  - Performance and quality presets

## Test Categories

### Recipe Domain Focus
All tests ensure recipe-specific scenarios are covered:
- **Recipe Card Creation**: Recipe data validation, card state management
- **Recipe Filtering**: Category, favorites, search, sort options
- **Recipe Selection**: Meal planning integration, selection workflows
- **Recipe Data Validation**: Business rules and constraints
- **Recipe Performance**: Optimizations for large recipe datasets

### Integration Workflows
- **Complete Recipe Loading**: Through all coordinator layers
- **Recipe Filtering Coordination**: Multiple coordinators working together
- **Recipe Search Integration**: Debounced search across system
- **Recipe Selection Workflow**: Normal and selection modes
- **Combined Filtering**: Multiple filters applied simultaneously

### Performance Testing
- **Object Pooling Integration**: Recipe card pool management
- **Progressive Rendering**: Large dataset handling
- **Memory Management**: Coordinator lifecycle cleanup
- **Performance Metrics**: Operation timing and optimization
- **Large Dataset Performance**: 50+ recipe handling
- **Rapid Filter Changes**: Debouncing effectiveness

### Error Handling
- **Service Error Handling**: Graceful degradation
- **Rendering Error Recovery**: Partial failure handling
- **Coordinator Communication Errors**: Isolation and recovery
- **Edge Cases**: Empty data, invalid data, rapid operations

## Test Patterns Used

### MealGenie Testing Infrastructure
- **pytest markers**: `@pytest.mark.integration`, `@pytest.mark.ui`, `@pytest.mark.slow`
- **factory-boy integration**: Recipe test data generation
- **pytest-qt fixtures**: `qtbot`, `qapp` for UI component testing
- **Database session fixtures**: Automatic rollback for isolated tests
- **Mock services and repositories**: Unit testing isolation

### Recipe Domain Test Utilities
- **Recipe validation helpers**: Common assertion patterns
- **Test recipe factories**: Realistic recipe data generation
- **Filter state validation**: Recipe domain constraints
- **Card interaction testing**: Recipe-specific UI patterns
- **Performance benchmarking**: Recipe browsing optimization

### Coordinator Testing Patterns
- **Mock coordination**: Isolated coordinator testing
- **Signal/slot testing**: Qt signal interaction validation
- **Debounce testing**: Time-sensitive operation validation
- **Memory leak detection**: Weak references and cleanup verification
- **Progressive rendering testing**: Batch processing validation

## Test Data Management

### Realistic Recipe Test Data
- **Varied Complexity**: Simple to gourmet recipes
- **Multiple Categories**: All supported recipe categories
- **Nutritional Data**: Realistic cooking times and serving sizes
- **Recipe History**: Versioning and modification tracking
- **Image Paths**: Proper image handling and fallbacks

### Meal Planning Test Scenarios
- **Dietary Restrictions**: Complex constraint combinations
- **Time Constraints**: Quick weeknight vs. weekend cooking
- **Seasonal Availability**: Ingredient freshness considerations
- **Budget Considerations**: Cost-conscious meal planning

## Performance Benchmarks

### Expected Performance Targets
- **Large Dataset Loading**: <5 seconds for 50+ recipes
- **Filter Changes**: <3 seconds for rapid filter combinations
- **Memory Stability**: Stable memory usage over multiple operations
- **Progressive Rendering**: Responsive UI during large dataset rendering
- **Debounce Effectiveness**: Fewer service calls than user actions

### Memory Management
- **Object Pool Efficiency**: Recipe card reuse validation
- **Weak Reference Tracking**: Memory leak prevention
- **Cleanup Verification**: Complete resource cleanup
- **Garbage Collection**: Forced cleanup testing

## Test Execution

### Running All RecipeBrowser Tests
```bash
# All RecipeBrowser integration tests
pytest _tests/integration/ui/views/test_recipe_browser_integration.py -v

# All coordinator unit tests
pytest _tests/unit/ui/managers/test_performance_manager.py -v
pytest _tests/unit/ui/managers/test_event_coordinator.py -v
pytest _tests/unit/ui/views/recipe_browser/test_filter_coordinator.py -v
pytest _tests/unit/ui/views/recipe_browser/test_rendering_coordinator.py -v
pytest _tests/unit/ui/views/recipe_browser/test_recipe_browser_coordinators.py -v

# Configuration tests
pytest _tests/unit/ui/views/recipe_browser/test_config.py -v

# Run with specific markers
pytest -m integration _tests/integration/ui/views/ -v
pytest -m ui _tests/unit/ui/ -v
pytest -m slow _tests/ -v  # Performance tests
```

### Test Categories by Marker
```bash
pytest -m integration  # Integration workflow tests
pytest -m unit         # Unit tests for individual coordinators
pytest -m ui           # UI component and interaction tests
pytest -m slow         # Performance and stress tests
```

## Success Metrics

### Architectural Validation
- **Coordinator Independence**: Each coordinator can be tested in isolation
- **Communication Patterns**: Proper event flow between coordinators
- **Resource Management**: No memory leaks or resource conflicts
- **Configuration Consistency**: Settings propagate correctly
- **Error Isolation**: Coordinator failures don't cascade

### Recipe Domain Validation
- **Business Rule Compliance**: All recipe constraints enforced
- **Data Integrity**: Recipe data validation and consistency
- **User Workflow Reliability**: Complete recipe management workflows
- **Performance Requirements**: Recipe browsing performance targets met
- **UI Responsiveness**: Smooth interaction under all conditions

### Quality Assurance
- **Test Coverage**: All coordinator interactions covered
- **Edge Case Handling**: Robust error handling validated
- **Performance Regression**: Performance benchmarks maintained
- **Memory Efficiency**: No memory leaks or excessive usage
- **User Experience**: Consistent behavior across all scenarios

## Debugging and Troubleshooting

### Common Issues
- **Qt Event Processing**: Ensure `QApplication.processEvents()` for UI tests
- **Timing Dependencies**: Use appropriate sleep/wait for debounced operations
- **Mock Configuration**: Proper mock setup for complex coordinator interactions
- **Memory Management**: Clean up Qt objects with `deleteLater()`
- **Signal Connections**: Verify signal/slot connections in coordinator tests

### Debug Utilities
- **PerformanceManager Metrics**: Real-time performance monitoring
- **EventCoordinator Logging**: Event flow debugging
- **FilterCoordinator State**: Filter state inspection
- **RenderingCoordinator Status**: Rendering progress tracking
- **Memory Usage Tracking**: Resource usage monitoring

This comprehensive test suite ensures the refactored RecipeBrowser maintains all functionality while providing improved performance, maintainability, and reliability through the coordinator architecture.