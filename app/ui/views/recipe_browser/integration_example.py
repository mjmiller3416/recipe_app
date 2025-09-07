"""Integration Example: RenderingCoordinator with RecipeBrowser

This file demonstrates how to integrate the RenderingCoordinator with the RecipeBrowser view
to extract and centralize recipe-specific rendering logic while maintaining performance
optimizations and proper architecture separation.

This example shows the key integration points and can be used as a reference for
refactoring the existing RecipeBrowser implementation.
"""

# ── Example Integration ────────────────────────────────────────────────────────────────────────────────────
from typing import List, Optional

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWidget

from _dev_tools.debug_logger import DebugLogger
from app.core.models.recipe import Recipe
from app.ui.managers.performance.performance_manager import PerformanceManager
from app.ui.views.base import ScrollableNavView
from .config import RecipeBrowserConfig, create_default_config
from .rendering_coordinator import CardInteractionType, RenderingCoordinator

class RecipeBrowserIntegrationExample(ScrollableNavView):
    """
    Example showing RenderingCoordinator integration with RecipeBrowser.
    
    This demonstrates how to refactor the existing RecipeBrowser to use the
    RenderingCoordinator for all recipe-specific rendering operations while
    maintaining the existing API and functionality.
    
    Key Integration Points:
    1. RenderingCoordinator initialization with PerformanceManager
    2. Layout container setup delegation
    3. Recipe rendering delegation with performance optimization
    4. Selection mode coordination
    5. Interaction signal routing
    6. Cleanup coordination
    """
    
    def __init__(self, parent=None, selection_mode: bool = False, 
                 config: Optional[RecipeBrowserConfig] = None):
        """Initialize with RenderingCoordinator integration."""
        # Configuration
        self._config = config or create_default_config()
        self._config.validate()
        
        # State
        self._selection_mode = selection_mode
        self._recipes_loaded = False
        
        # Performance management
        self._performance_manager = PerformanceManager(self)
        
        # Recipe rendering coordination
        self._rendering_coordinator = RenderingCoordinator(
            performance_manager=self._performance_manager,
            config=self._config,
            parent=self
        )
        
        super().__init__(parent)
        
        # Setup rendering coordinator integration
        self._setup_rendering_integration()
        
        DebugLogger.log("RecipeBrowser with RenderingCoordinator integration initialized", "info")
    
    def _setup_rendering_integration(self):
        """Setup integration signals and connections with RenderingCoordinator."""
        # Connect rendering coordinator signals
        self._rendering_coordinator.rendering_started.connect(self._on_rendering_started)
        self._rendering_coordinator.rendering_completed.connect(self._on_rendering_completed)
        self._rendering_coordinator.card_interaction.connect(self._on_card_interaction)
        self._rendering_coordinator.error_occurred.connect(self._on_rendering_error)
        
        # Connect selection mode changes
        self._rendering_coordinator.selection_mode_changed.connect(self._on_selection_mode_changed)
    
    def _build_ui(self):
        """Build UI with RenderingCoordinator integration."""
        try:
            # Build filter controls (unchanged)
            self._build_filter_controls()
            
            # Setup layout container through rendering coordinator
            self._setup_recipe_grid_with_coordinator()
            
            DebugLogger.log("UI built with RenderingCoordinator integration", "debug")
            
        except Exception as e:
            DebugLogger.log(f"Error building UI with coordinator: {e}", "error")
            raise
    
    def _build_filter_controls(self):
        """Build filter controls (simplified example)."""
        # Filter controls implementation (unchanged from original)
        # This example focuses on the rendering coordination aspects
        pass
    
    def _setup_recipe_grid_with_coordinator(self):
        """Setup recipe grid using RenderingCoordinator."""
        # Create container widget for the layout
        self._grid_container = QWidget()
        
        # Let the rendering coordinator setup and manage the layout
        self._flow_layout = self._rendering_coordinator.setup_layout_container(self._grid_container)
        
        # Add container to scroll area
        self.scroll_layout.addWidget(self._grid_container)
        
        DebugLogger.log("Recipe grid setup with RenderingCoordinator", "debug")
    
    # ── Recipe Display Integration ─────────────────────────────────────────────────────────────────────────────
    def display_recipes(self, recipes: List[Recipe]):
        """Display recipes using RenderingCoordinator."""
        if not recipes:
            self.clear_recipes()
            return
        
        # Delegate to rendering coordinator
        success = self._rendering_coordinator.render_recipes(recipes, self._selection_mode)
        
        if success:
            self._recipes_loaded = True
            DebugLogger.log(f"Started rendering {len(recipes)} recipes via coordinator", "debug")
        else:
            DebugLogger.log("Failed to start recipe rendering via coordinator", "error")
    
    def clear_recipes(self):
        """Clear recipes using RenderingCoordinator."""
        self._rendering_coordinator.clear_rendering()
        self._recipes_loaded = False
        DebugLogger.log("Recipes cleared via coordinator", "debug")
    
    def set_selection_mode(self, enabled: bool):
        """Set selection mode via RenderingCoordinator."""
        if self._selection_mode != enabled:
            self._selection_mode = enabled
            self._rendering_coordinator.update_selection_mode(enabled)
    
    # ── Signal Handlers for Rendering Coordinator ─────────────────────────────────────────────────────────────
    def _on_rendering_started(self, recipe_count: int):
        """Handle rendering started from coordinator."""
        DebugLogger.log(f"Recipe rendering started for {recipe_count} recipes", "debug")
        # Could emit view-level signals, update UI status, etc.
    
    def _on_rendering_completed(self, recipe_count: int, duration_ms: float):
        """Handle rendering completed from coordinator."""
        self._recipes_loaded = True
        
        # Log performance information
        if duration_ms > self._config.performance.slow_render_threshold_ms:
            DebugLogger.log(
                f"SLOW RENDER WARNING: {duration_ms:.2f}ms for {recipe_count} recipes",
                "warning"
            )
        else:
            DebugLogger.log(
                f"Recipe rendering completed: {recipe_count} recipes in {duration_ms:.2f}ms",
                "debug"
            )
        
        # Could emit view-level completion signals
    
    def _on_card_interaction(self, recipe: Recipe, interaction_type: str):
        """Handle recipe card interactions from coordinator."""
        DebugLogger.log(f"Recipe card interaction: {interaction_type} for {recipe.recipe_name}", "debug")
        
        # Route interactions to appropriate handlers
        if interaction_type == CardInteractionType.RECIPE_OPENED.value:
            self._handle_recipe_opened(recipe)
        elif interaction_type == CardInteractionType.SELECTION_CHANGED.value:
            self._handle_recipe_selected(recipe)
        elif interaction_type == CardInteractionType.FAVORITE_TOGGLED.value:
            self._handle_favorite_toggled(recipe)
    
    def _on_selection_mode_changed(self, selection_mode: bool):
        """Handle selection mode changes from coordinator."""
        self._selection_mode = selection_mode
        DebugLogger.log(f"Selection mode changed to: {selection_mode}", "debug")
    
    def _on_rendering_error(self, error_type: str, error_message: str):
        """Handle rendering errors from coordinator."""
        DebugLogger.log(f"Rendering error ({error_type}): {error_message}", "error")
        # Could show user-friendly error messages, retry logic, etc.
    
    # ── Recipe Interaction Handlers ────────────────────────────────────────────────────────────────────────────
    def _handle_recipe_opened(self, recipe: Recipe):
        """Handle recipe opened interaction."""
        DebugLogger.log(f"Recipe opened: {recipe.recipe_name}", "debug")
        # Emit view-level signal for navigation
        # self.recipe_opened.emit(recipe)
    
    def _handle_recipe_selected(self, recipe: Recipe):
        """Handle recipe selected interaction."""
        DebugLogger.log(f"Recipe selected: {recipe.recipe_name}", "debug")
        # Emit view-level signal for meal planning
        # self.recipe_selected.emit(recipe.id, recipe)
    
    def _handle_favorite_toggled(self, recipe: Recipe):
        """Handle favorite toggled interaction."""
        DebugLogger.log(f"Favorite toggled for: {recipe.recipe_name}", "debug")
        # Update recipe state, refresh display, etc.
    
    # ── Performance and Diagnostics ────────────────────────────────────────────────────────────────────────────
    def get_rendering_metrics(self):
        """Get comprehensive rendering performance metrics."""
        coordinator_metrics = self._rendering_coordinator.get_render_metrics()
        performance_metrics = self._performance_manager.get_performance_summary()
        
        return {
            'rendering_coordinator': coordinator_metrics,
            'performance_manager': performance_metrics,
            'view_state': {
                'recipes_loaded': self._recipes_loaded,
                'selection_mode': self._selection_mode,
            }
        }
    
    def log_performance_summary(self):
        """Log performance summary for debugging."""
        metrics = self.get_rendering_metrics()
        
        DebugLogger.log("=== Recipe Browser Performance Summary ===", "info")
        DebugLogger.log(f"Rendered cards: {metrics['rendering_coordinator']['rendered_cards']}", "info")
        DebugLogger.log(f"Render state: {metrics['rendering_coordinator']['render_state']}", "info")
        DebugLogger.log(f"Selection mode: {metrics['rendering_coordinator']['selection_mode']}", "info")
        
        # Performance manager metrics
        perf_metrics = metrics['performance_manager']['metrics']
        DebugLogger.log(f"Total operations: {perf_metrics.get('total_operations', 0)}", "info")
        DebugLogger.log(f"Pool usage: {len(metrics['performance_manager']['pools'])} pools active", "info")
    
    # ── Lifecycle and Cleanup ──────────────────────────────────────────────────────────────────────────────────
    def refresh_recipes(self):
        """Refresh recipes with current filter settings."""
        # In real implementation, would get recipes from ViewModel
        # For this example, just clear and reload
        current_recipes = self._get_current_recipes()  # Placeholder
        if current_recipes:
            self.display_recipes(current_recipes)
    
    def _get_current_recipes(self) -> List[Recipe]:
        """Get current recipes (placeholder for ViewModel integration)."""
        # In real implementation, would delegate to ViewModel
        # This is just a placeholder for the integration example
        return []
    
    def cleanup(self):
        """Cleanup view and rendering coordinator."""
        try:
            # Cleanup rendering coordinator
            if hasattr(self, '_rendering_coordinator'):
                self._rendering_coordinator.cleanup()
            
            # Cleanup performance manager
            if hasattr(self, '_performance_manager'):
                self._performance_manager.cleanup()
            
            DebugLogger.log("RecipeBrowser cleanup completed with coordinator integration", "debug")
            
        except Exception as e:
            DebugLogger.log(f"Error during cleanup: {e}", "error")


# ── Migration Guide ────────────────────────────────────────────────────────────────────────────────────────
"""
MIGRATION GUIDE: Refactoring RecipeBrowser to use RenderingCoordinator

1. INITIALIZATION CHANGES:
   OLD: Direct card pool and progressive renderer creation
   NEW: Create PerformanceManager and RenderingCoordinator

2. LAYOUT SETUP CHANGES:
   OLD: Manual FlowLayout creation and card pool assignment
   NEW: Delegate to rendering_coordinator.setup_layout_container()

3. RECIPE RENDERING CHANGES:
   OLD: _display_recipes_optimized() with manual card pool management
   NEW: rendering_coordinator.render_recipes() with automatic optimization

4. CARD CONFIGURATION CHANGES:
   OLD: Manual card configuration in _render_recipe_batch()
   NEW: Automatic via rendering_coordinator.configure_recipe_card()

5. INTERACTION HANDLING CHANGES:
   OLD: Direct signal connections in card configuration
   NEW: Centralized via rendering_coordinator.card_interaction signal

6. SELECTION MODE CHANGES:
   OLD: Manual card updates in _on_selection_mode_changed()
   NEW: rendering_coordinator.update_selection_mode()

7. CLEANUP CHANGES:
   OLD: Manual card pool clearing and timer cleanup
   NEW: rendering_coordinator.cleanup() and performance_manager.cleanup()

8. PERFORMANCE MONITORING CHANGES:
   OLD: Manual timing and metrics tracking
   NEW: Automatic via PerformanceManager integration

KEY BENEFITS OF REFACTORING:
- Separation of concerns: Recipe domain logic separated from general UI logic
- Performance optimization: Centralized object pooling and progressive rendering
- Maintainability: Single place for recipe rendering logic
- Testability: RenderingCoordinator can be tested independently
- Extensibility: Easy to add new recipe-specific rendering features
- Configuration: Centralized configuration through RecipeBrowserConfig

INTEGRATION STEPS:
1. Add PerformanceManager and RenderingCoordinator to RecipeBrowser.__init__()
2. Replace _build_recipe_grid_optimized() with coordinator.setup_layout_container()
3. Replace _display_recipes_optimized() with coordinator.render_recipes()
4. Replace manual card configuration with coordinator signal handling
5. Replace _clear_recipe_cards_optimized() with coordinator.clear_rendering()
6. Update selection mode handling to use coordinator.update_selection_mode()
7. Remove manual card pool management code
8. Update cleanup() to use coordinator and performance manager cleanup
"""