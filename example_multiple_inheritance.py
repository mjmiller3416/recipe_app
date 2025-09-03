"""example_multiple_inheritance.py

Example of using multiple inheritance with existing base classes.
"""

from app.ui.views.base import ScrollableView
from app.ui.services.navigation_service import NavigableView, RouteRegistry, ViewType


# Option 2A: Multiple inheritance approach
class ScrollableNavigableView(ScrollableView, NavigableView):
    """
    Combines ScrollableView functionality with navigation capabilities.
    
    Note: Method Resolution Order (MRO) will prioritize ScrollableView methods.
    """
    
    def __init__(self, navigation_service=None, parent=None):
        # Call both parent constructors
        ScrollableView.__init__(self, parent)
        NavigableView.__init__(self, navigation_service, parent)


# Example usage with multiple inheritance
@RouteRegistry.register("shopping_list_v2", ViewType.MAIN, sidebar_visible=True)
class ShoppingListV2(ScrollableNavigableView):
    """Shopping list using multiple inheritance approach."""
    
    def _build_ui(self):
        """Build the shopping list UI using the scroll layout."""
        # Access the scroll layout from ScrollableView
        self.list_container = self._create_list_container()
        self.entry_card = self._create_entry_card()
        
        # Add to scroll content layout
        self.content_layout.addWidget(self.list_container)
        self.content_layout.addWidget(self.entry_card)
        
    def _create_list_container(self):
        """Create list container (simplified example)."""
        from PySide6.QtWidgets import QLabel
        return QLabel("Shopping List Content")
        
    def _create_entry_card(self):
        """Create entry card (simplified example)."""
        from PySide6.QtWidgets import QLabel
        return QLabel("Add Item Form")
    
    # Navigation lifecycle hooks
    def on_enter(self, params: dict):
        """Load shopping list when navigated to."""
        # Load shopping list data
        print(f"Loading shopping list with params: {params}")
        
    def on_before_leave(self) -> bool:
        """Save any pending changes."""
        # Save shopping list state
        return True