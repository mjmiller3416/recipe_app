"""
Example usage of EventCoordinator for RecipeBrowser refactoring.

This example shows how the existing debouncing logic in RecipeBrowser 
can be refactored using the generic EventCoordinator system.
"""

from typing import Any, Dict

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QCheckBox

from app.ui.components.widgets import ComboBox
from app.ui.managers.events import (
    ConnectionScope, DebouncingStrategy, EventCoordinator, EventPriority,
)

class RefactoredRecipeBrowserExample:
    """
    Example showing how to refactor RecipeBrowser using EventCoordinator.
    
    This replaces the manual debouncing logic in the original RecipeBrowser
    with a cleaner, more maintainable approach using the EventCoordinator.
    """
    
    def __init__(self, parent: QObject = None):
        self.parent = parent
        
        # Initialize EventCoordinator
        self.event_coordinator = EventCoordinator(parent, "RecipeBrowser")
        
        # Simulated UI components (would be real widgets in actual implementation)
        self._cb_filter = ComboBox(list_items=["All", "Main Dish", "Dessert"], placeholder="Filter")
        self._cb_sort = ComboBox(list_items=["A-Z", "Z-A", "Rating"], placeholder="Sort")
        self._chk_favorites = QCheckBox("Show Favorites Only")
        
        # Setup coordinated event handling
        self._setup_filter_coordination()
        self._setup_individual_handlers()
    
    def _setup_filter_coordination(self):
        """Setup coordinated filtering with automatic debouncing and batching."""
        
        # Define filter controls
        filter_controls = {
            'category': self._cb_filter,
            'sort': self._cb_sort,
            'favorites': self._chk_favorites
        }
        
        # Setup coordinated filtering (replaces manual debouncing in original)
        self.filter_coordination_id = self.event_coordinator.setup_filter_coordination(
            filter_controls=filter_controls,
            filter_handler=self._apply_combined_filters,
            delay_ms=250,  # Same as original FILTER_UPDATE_DELAY
            batch_updates=True
        )
        
        print(f"Filter coordination setup: {self.filter_coordination_id}")
    
    def _setup_individual_handlers(self):
        """Setup individual debounced handlers (alternative approach)."""
        
        # Category filter with trailing edge debouncing (original behavior)
        self.event_coordinator.setup_debounced_handler(
            "category_filter",
            self._handle_category_change,
            delay_ms=250,
            strategy=DebouncingStrategy.TRAILING
        )
        
        # Sort option with immediate feedback (leading edge)
        self.event_coordinator.setup_debounced_handler(
            "sort_option", 
            self._handle_sort_change,
            delay_ms=100,
            strategy=DebouncingStrategy.LEADING
        )
        
        # Favorites toggle with throttling
        self.event_coordinator.setup_debounced_handler(
            "favorites_toggle",
            self._handle_favorites_change, 
            delay_ms=500,
            strategy=DebouncingStrategy.THROTTLE
        )
        
        # Manual signal connections (if not using coordination)
        # self.event_coordinator.connect_signal(
        #     self._cb_filter, "currentTextChanged",
        #     self, lambda text: self.event_coordinator.trigger_debounced("category_filter", text),
        #     ConnectionScope.VIEW_LIFECYCLE
        # )
    
    def _apply_combined_filters(self, filters: Dict[str, Any]) -> None:
        """
        Apply combined filters (replaces _execute_delayed_filter_update in original).
        
        This method receives all filter changes batched together, 
        replacing the manual pending changes tracking in the original.
        """
        print(f"Applying combined filters: {filters}")
        
        # Extract filter values
        category = filters.get('category', '')
        sort_option = filters.get('sort', '')
        favorites_only = filters.get('favorites', False)
        
        # Apply filters (would call ViewModel in real implementation)
        if category:
            print(f"  - Category filter: {category}")
        
        if sort_option:
            print(f"  - Sort option: {sort_option}")
        
        if favorites_only:
            print(f"  - Favorites only: {favorites_only}")
        
        # In real implementation, this would call:
        # if self._view_model:
        #     self._view_model.update_category_filter(category)
        #     self._view_model.update_sort_option(sort_option)
        #     self._view_model.update_favorites_filter(favorites_only)
    
    def _handle_category_change(self, category: str) -> None:
        """Handle individual category changes."""
        print(f"Category changed: {category}")
        # Would update ViewModel in real implementation
    
    def _handle_sort_change(self, sort_option: str) -> None:
        """Handle individual sort changes."""  
        print(f"Sort option changed: {sort_option}")
        # Would update ViewModel in real implementation
    
    def _handle_favorites_change(self, favorites_only: bool) -> None:
        """Handle favorites toggle changes."""
        print(f"Favorites only: {favorites_only}")
        # Would update ViewModel in real implementation
    
    def demonstrate_usage(self):
        """Demonstrate the EventCoordinator functionality."""
        print("\n=== EventCoordinator Usage Example ===")
        
        # Simulate rapid filter changes (would be debounced automatically)
        print("\nSimulating rapid filter changes...")
        self.event_coordinator.trigger_debounced("category_filter", "Main Dish")
        self.event_coordinator.trigger_debounced("category_filter", "Dessert")  # This would override the first
        
        # Demonstrate coordination info
        print(f"\nActive coordinations: {len(self.event_coordinator._active_coordinations)}")
        
        # Get performance metrics
        metrics = self.event_coordinator.get_performance_metrics()
        print(f"\nPerformance metrics:")
        print(f"  - Active debounced functions: {metrics['debouncer_metrics']['active_functions']}")
        print(f"  - Total signal connections: {metrics['signal_manager_metrics']['total_connections']}")
        print(f"  - Event routes: {metrics['event_router_metrics']['total_routes']}")
        
        # Demonstrate manual event routing
        print(f"\nRouting custom event...")
        results = self.event_coordinator.route_event("custom_event", {
            "data": "test_data",
            "timestamp": "2025-09-07"
        })
        print(f"Event routing results: {len(results)} handlers executed")
        
        return True
    
    def cleanup(self):
        """Cleanup all coordinations and connections."""
        cleaned_count = self.event_coordinator.cleanup_all_coordinations()
        print(f"Cleaned up {cleaned_count} coordinations")


# Example usage demonstrating the key differences from original approach:

def compare_original_vs_refactored():
    """
    Compare original RecipeBrowser debouncing vs EventCoordinator approach.
    """
    
    print("\n=== Comparison: Original vs Refactored Approach ===")
    
    print("\nORIGINAL APPROACH (RecipeBrowser):")
    print("  - Manual QTimer management for each debounced operation")
    print("  - Manual pending changes tracking (_pending_filter_changes)")
    print("  - Separate methods for each filter type change")
    print("  - Manual signal/slot connection management")
    print("  - Custom debouncing logic scattered throughout the class")
    print("  - Difficult to reuse debouncing patterns in other views")
    
    print("\nREFACTORED APPROACH (EventCoordinator):")
    print("  - Generic debouncing system with configurable strategies")
    print("  - Automatic batching and coordination of related events")
    print("  - Centralized event routing with priority and filtering")
    print("  - Managed signal connections with automatic cleanup")
    print("  - Reusable coordination patterns (search, filter, validation)")
    print("  - Easy to extend and maintain across multiple views")
    
    print("\nKEY BENEFITS:")
    print("  + Reduced code duplication across views")
    print("  + Automatic memory leak prevention")  
    print("  + Consistent debouncing behavior application-wide")
    print("  + Better separation of concerns")
    print("  + Easier testing and debugging")
    print("  + Performance monitoring built-in")


if __name__ == "__main__":
    # Run the example
    example = RefactoredRecipeBrowserExample()
    example.demonstrate_usage()
    compare_original_vs_refactored()
    example.cleanup()