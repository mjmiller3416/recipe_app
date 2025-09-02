"""example_multiple_inheritance.py

Example of using multiple inheritance with existing base classes.
"""

from app.ui.views.base import ScrollableView
from app.ui.services.navigation_views import MainView
from app.ui.services.navigation_registry import NavigationRegistry, ViewType, RouteConstants


# Option 2A: Multiple inheritance approach
class ScrollableNavigableView(ScrollableView, MainView):
    """
    Combines ScrollableView functionality with navigation capabilities.
    
    Note: Method Resolution Order (MRO) will prioritize ScrollableView methods.
    """
    
    def __init__(self, parent=None):
        # Call both parent constructors
        ScrollableView.__init__(self, parent)
        MainView.__init__(self, parent)
        
        # Set navigation view type
        self._view_type = ViewType.MAIN


# Example usage with multiple inheritance
@NavigationRegistry.register(
    path="/shopping-list-v2",
    view_type=ViewType.MAIN,
    title="Shopping List v2"
)
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
    def after_navigate_to(self, path: str, params: dict):
        """Load shopping list when navigated to."""
        # Load shopping list data
        print(f"Loading shopping list for route: {path}")
        
    def before_navigate_from(self, next_path: str, next_params: dict) -> bool:
        """Save any pending changes."""
        # Save shopping list state
        return True