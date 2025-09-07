# PerformanceManager Migration Guide

This document outlines how to migrate from the existing RecipeCardPool and ProgressiveRenderer to the new generic PerformanceManager system.

## Overview

The new PerformanceManager provides:
- **Generic object pooling** - Works with any object type, not just recipe cards
- **Progressive rendering** - Configurable batch rendering with metrics
- **Memory management** - Automatic cleanup and garbage collection
- **Performance metrics** - Detailed timing and threshold monitoring

## Migration Steps

### 1. Replace RecipeCardPool

**Before (app/ui/views/recipe_browser/recipe_card_pool.py):**
```python
class RecipeBrowserView:
    def __init__(self):
        self.card_pool = RecipeCardPool(card_size, max_pool_size=50)
        self.card_pool.set_parent_widget(self)
        
    def get_card(self):
        return self.card_pool.get_card()
        
    def return_card(self, card):
        self.card_pool.return_card(card)
```

**After (using PerformanceManager):**
```python
from app.ui.managers.performance import PerformanceManager

class RecipeBrowserView:
    def __init__(self):
        self.performance_manager = PerformanceManager()
        
        # Create widget pool for recipe cards
        self.card_pool = self.performance_manager.create_widget_pool(
            name="recipe_cards",
            widget_factory=lambda parent: create_recipe_card(self.card_size, parent),
            parent_widget=self,
            max_pool_size=50
        )
        
    def get_card(self):
        return self.card_pool.get_object()
        
    def return_card(self, card):
        self.card_pool.return_object(card)
```

### 2. Replace ProgressiveRenderer

**Before (app/ui/views/recipe_browser/progressive_renderer.py):**
```python
class RecipeBrowserView:
    def __init__(self):
        self.progressive_renderer = ProgressiveRenderer(self)
        
    def load_recipes(self, recipes):
        self.progressive_renderer.start_progressive_render(recipes, batch_size=5)
        
    def _render_recipe_batch(self, recipes):
        # Custom rendering logic
        pass
        
    def _on_progressive_render_complete(self):
        # Completion logic
        pass
```

**After (using PerformanceManager):**
```python
from app.ui.managers.performance import ProgressiveRenderTarget

class RecipeBrowserView(ProgressiveRenderTarget):
    def __init__(self):
        self.performance_manager = PerformanceManager()
        
        # Create progressive renderer
        self.progressive_renderer = self.performance_manager.create_progressive_renderer(
            name="recipe_renderer", 
            target=self,
            default_batch_size=5,
            default_delay_ms=10
        )
        
    def load_recipes(self, recipes):
        self.progressive_renderer.start_rendering(recipes, batch_size=5)
    
    # Implement ProgressiveRenderTarget interface
    def render_batch(self, recipes, batch_index, total_batches):
        # Custom rendering logic (replaces _render_recipe_batch)
        pass
        
    def on_render_complete(self):
        # Completion logic (replaces _on_progressive_render_complete)
        pass
```

### 3. Add Performance Monitoring

**New capabilities with PerformanceManager:**
```python
class RecipeBrowserView:
    def __init__(self):
        # ... setup performance manager ...
        
        # Set performance thresholds
        self.performance_manager.set_performance_threshold("recipe_card_creation", 0.05)
        self.performance_manager.set_performance_threshold("recipe_batch_render", 0.1)
        
        # Enable memory management
        self.performance_manager.start_memory_management(interval_ms=60000)
    
    def expensive_operation(self):
        # Use performance timing
        with self.performance_manager.performance_context("expensive_operation"):
            # Your code here
            pass
    
    def get_performance_stats(self):
        return self.performance_manager.get_performance_summary()
```

## Benefits of Migration

### 1. Reusability
- The PerformanceManager can be used by other views (MealPlanner, AddRecipes, etc.)
- Generic object pooling works with any widget type
- Progressive rendering works with any data type

### 2. Better Performance Monitoring
- Automatic timing of operations
- Configurable performance thresholds
- Detailed statistics and reporting
- Memory usage tracking

### 3. Improved Memory Management
- Automatic garbage collection
- Weak reference tracking
- Periodic cleanup
- Better resource management

### 4. Enhanced Progressive Rendering
- Pausable/resumable rendering
- Progress reporting with signals
- Configurable batch sizes and delays
- Error handling and recovery

### 5. MVVM Compliance
- Follows MealGenie architectural patterns
- Clean separation of concerns
- Signal-based communication
- Proper dependency injection

## Example Integration

See `app/ui/managers/performance/example_usage.py` for complete examples of:
- Recipe browser integration
- Simple widget pooling  
- Callback-based progressive rendering
- Performance monitoring

## Migration Timeline

1. **Phase 1**: Create PerformanceManager instances in existing views
2. **Phase 2**: Replace RecipeCardPool with generic widget pools
3. **Phase 3**: Replace ProgressiveRenderer with new system
4. **Phase 4**: Add performance monitoring and thresholds
5. **Phase 5**: Remove old classes once migration is complete

## Testing

The new system maintains the same functionality while providing additional capabilities:
- All existing tests should continue to pass
- New tests can be added for performance monitoring
- Integration tests can verify the progressive rendering behavior

## Files Created

- `app/ui/managers/performance/__init__.py` - Package exports
- `app/ui/managers/performance/performance_manager.py` - Main manager class
- `app/ui/managers/performance/object_pool.py` - Generic object pooling
- `app/ui/managers/performance/progressive_renderer.py` - Progressive rendering system
- `app/ui/managers/performance/metrics_tracker.py` - Performance metrics tracking
- `app/ui/managers/performance/example_usage.py` - Usage examples
- `app/ui/managers/performance/migration_guide.md` - This guide

## Next Steps

1. Update RecipeBrowserView to use PerformanceManager
2. Test the integration thoroughly
3. Migrate other views to use the system
4. Remove deprecated RecipeCardPool and ProgressiveRenderer classes
5. Add performance monitoring to critical operations