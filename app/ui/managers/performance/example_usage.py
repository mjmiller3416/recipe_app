"""app/ui/managers/performance/example_usage.py

Example usage of the PerformanceManager for recipe browser refactoring.
This demonstrates how to replace RecipeCardPool with the generic system.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from typing import List

from PySide6.QtWidgets import QWidget

from app.core.models.recipe import Recipe
from app.ui.components.composite.recipe_card import LayoutSize, create_recipe_card
from .performance_manager import PerformanceManager
from .progressive_renderer import ProgressiveRenderTarget

# ── Recipe Browser Performance Integration ─────────────────────────────────────────────────────────────────
class RecipeBrowserPerformanceDemo:
    """
    Example integration of PerformanceManager for RecipeBrowser view.
    
    This replaces the old RecipeCardPool and ProgressiveRenderer with
    the new generic performance management system.
    """
    
    def __init__(self, parent_widget: QWidget, card_size: LayoutSize):
        """Initialize performance-optimized recipe browser."""
        
        # Create performance manager
        self.performance_manager = PerformanceManager()
        
        # Create widget pool for recipe cards
        self.card_pool = self.performance_manager.create_widget_pool(
            name="recipe_cards",
            widget_factory=lambda parent: create_recipe_card(card_size, parent),
            parent_widget=parent_widget,
            max_pool_size=50
        )
        
        # Create progressive renderer
        self.progressive_renderer = self.performance_manager.create_progressive_renderer(
            name="recipe_renderer",
            target=self,  # This class implements ProgressiveRenderTarget
            default_batch_size=5,
            default_delay_ms=10
        )
        
        # Setup performance thresholds
        self.performance_manager.set_performance_threshold("recipe_card_creation", 0.05)
        self.performance_manager.set_performance_threshold("recipe_batch_render", 0.1)
        
        # Enable memory management
        self.performance_manager.start_memory_management(interval_ms=60000)
    
    def load_recipes(self, recipes: List[Recipe]):
        """Load recipes using progressive rendering."""
        
        # Start performance measurement
        with self.performance_manager.performance_context("recipe_loading"):
            # Clear existing cards
            self.card_pool.return_all_objects()
            
            # Start progressive rendering
            self.progressive_renderer.start_rendering(
                items=recipes,
                batch_size=5,
                delay_ms=10
            )
    
    def get_recipe_card(self):
        """Get a recipe card from the pool."""
        with self.performance_manager.performance_context("recipe_card_creation"):
            return self.card_pool.get_object()
    
    def return_recipe_card(self, card):
        """Return a recipe card to the pool."""
        self.card_pool.return_object(card)
    
    # ── ProgressiveRenderTarget Implementation ─────────────────────────────────────────────────────────────
    def render_batch(self, recipes: List[Recipe], batch_index: int, total_batches: int):
        """Render a batch of recipe cards."""
        
        with self.performance_manager.performance_context("recipe_batch_render"):
            for recipe in recipes:
                # Get card from pool
                card = self.get_recipe_card()
                
                # Setup card with recipe data
                card.set_recipe(recipe)
                card.setVisible(True)
                
                # Track the card for memory management
                self.performance_manager.track_object(card)
    
    def on_render_complete(self):
        """Called when progressive rendering completes."""
        print("Recipe rendering completed!")
        
        # Log performance summary
        self.performance_manager.log_performance_summary()
    
    def on_render_started(self, total_items: int, total_batches: int):
        """Called when progressive rendering starts."""
        print(f"Starting to render {total_items} recipes in {total_batches} batches")
    
    def on_batch_complete(self, batch_index: int, total_batches: int):
        """Called when a batch completes."""
        progress = ((batch_index + 1) / total_batches) * 100
        print(f"Batch {batch_index + 1}/{total_batches} complete ({progress:.1f}%)")
    
    def cleanup(self):
        """Clean up performance resources."""
        self.performance_manager.cleanup()


# ── Simple Widget Pool Example ─────────────────────────────────────────────────────────────────────────────
def create_simple_widget_pool_example():
    """Example of creating a simple widget pool."""
    
    performance_manager = PerformanceManager()
    
    # Create a widget pool for buttons
    button_pool = performance_manager.create_widget_pool(
        name="buttons",
        widget_factory=lambda parent: QWidget(parent),  # Simple widget factory
        max_pool_size=20
    )
    
    # Use the pool
    widget1 = button_pool.get_object()
    widget2 = button_pool.get_object() 
    
    # Return to pool
    button_pool.return_object(widget1)
    button_pool.return_object(widget2)
    
    # Get statistics
    stats = performance_manager.get_performance_summary()
    print(f"Pool statistics: {stats}")
    
    # Clean up
    performance_manager.cleanup()


# ── Callback-based Progressive Rendering ──────────────────────────────────────────────────────────────────
def create_callback_renderer_example():
    """Example of using callback-based progressive rendering."""
    
    performance_manager = PerformanceManager()
    
    def render_batch(items, batch_index, total_batches):
        print(f"Rendering batch {batch_index + 1}/{total_batches}: {len(items)} items")
        # Simulate rendering work
        for item in items:
            print(f"  - Rendering item: {item}")
    
    def on_complete():
        print("Rendering completed!")
    
    # Create callback renderer
    renderer = performance_manager.create_callback_renderer(
        name="demo_renderer",
        render_callback=render_batch,
        completion_callback=on_complete,
        default_batch_size=3,
        default_delay_ms=50
    )
    
    # Start rendering some dummy data
    dummy_items = [f"Item_{i}" for i in range(10)]
    renderer.start_rendering(dummy_items)
    
    # In a real application, you would let the Qt event loop handle the progressive rendering
    # Here we just demonstrate the setup


if __name__ == "__main__":
    # This file is meant to be imported and used as examples
    # Run simple demonstrations
    print("=== Simple Widget Pool Example ===")
    create_simple_widget_pool_example()
    
    print("\n=== Callback Renderer Example ===")
    create_callback_renderer_example()
    
    print("\nPerformance manager examples completed!")