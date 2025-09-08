
from PySide6.QtWidgets import QStackedWidget, QWidget, QLabel
from typing import Dict, Optional
from _dev_tools import DebugLogger

class Navigator:
    """Dead-simple navigation for your recipe app."""

    def __init__(self, container: QStackedWidget):
        self.container = container
        self.views: Dict[str, QWidget] = {}
        self.current_view: Optional[str] = None
        self.header_label = None

    def set_header_label(self, label):
        """Set reference to the header label."""
        self.header_label = label

    def register(self, name: str, view_class):
        """Register a view class with a name."""
        self.views[name] = view_class

    def show(self, name: str, **kwargs):
        """Show a view by name."""
        if name not in self.views:
            DebugLogger.log(f"Unknown view: {name}", "warning")
            return None

        # Get or create the view
        view = self.views[name]

        # If it's a class, instantiate it
        if isinstance(view, type):
            view = view()
            self.views[name] = view
            self.container.addWidget(view)

        # ALWAYS pass data if the view accepts it (not just on creation)
        if hasattr(view, 'load_data'):
            view.load_data(**kwargs)

        # Update header
        if self.header_label:
            headers = {
                "dashboard": "Dashboard",
                "meal_planner": "Meal Planner",
                "recipes": "Browse Recipes",
                "view_recipe": "Recipe Details",
                "shopping": "Shopping List",
                "add_recipes": "Add Recipes",
                "settings": "Settings"
            }
            self.header_label.setText(headers.get(name, name.title()))

        # Show it
        self.container.setCurrentWidget(view)
        self.current_view = name
        DebugLogger.log(f"Navigated to: {name}", "info")

        return view  # Return the view so caller can connect signals
