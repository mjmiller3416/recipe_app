"""services/navigation_service.py

Connects signals to their respective slots for handling sidebar and page navigation.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtWidgets import QStackedWidget

from _dev_tools import DebugLogger
from app.core.services import PlannerService, ShoppingService
from app.ui.views import AddRecipes, Dashboard, MealPlanner, RecipeBrowser, Settings, ShoppingList, ViewRecipe



# ── Navigation Service ──────────────────────────────────────────────────────────────────────────────────────
class NavigationService:
    def __init__(self, stacked_widget: QStackedWidget):
        self.sw_pages = stacked_widget
        self.page_instances = {}

    @classmethod
    def create(cls, stacked_widget: QStackedWidget) -> 'NavigationService':
        """
        A class method factory to create an instance of the NavigationService.
        'cls' refers to the NavigationService class itself.
        """
        return cls(stacked_widget)

    def build_and_register_pages(self):
        """Instantiate and register all page instances."""
        page_map = {
            "dashboard": Dashboard,
            "meal_planner": MealPlanner,
            "browse_recipes": RecipeBrowser,
            "shopping_list": ShoppingList,
            "add_recipe": AddRecipes,
            "settings": Settings,
        }
        for name, page_class in page_map.items():
            # Pass navigation service to views that need it
            if name == "meal_planner":
                instance = page_class(navigation_service=self)
            elif name == "browse_recipes":
                instance = page_class(navigation_service=self)
            else:
                instance = page_class()
            self.page_instances[name] = instance
            self.sw_pages.addWidget(instance)

    def switch_to(self, page_name: str):
        """Switch stacked widget to the given page."""
        DebugLogger.log(f"NavigationService.switch_to called with: {page_name}", "info")
        # this is the core logic from app.py's _switch_page
        if page_name not in self.page_instances:
            DebugLogger.log(f"Page {page_name} not found in page_instances: {list(self.page_instances.keys())}", "error")
            return

        next_widget = self.page_instances[page_name]
        current_widget = self.sw_pages.currentWidget()

        # Ensure any changes in the MealPlanner are saved before loading shopping list
        planner_widget = self.page_instances.get("meal_planner")
        if isinstance(planner_widget, MealPlanner):
            planner_widget.saveMealPlan()

        # refresh ShoppingList if navigating to it
        if page_name == "shopping_list" and isinstance(next_widget, ShoppingList):
            # Use context manager to ensure proper session cleanup
            from app.core.database.db import DatabaseSession
            try:
                with DatabaseSession() as session:
                    planner_svc = PlannerService(session)
                    meal_ids = planner_svc.load_saved_meal_ids()
                    shopping_svc = ShoppingService(session)
                    recipe_ids = shopping_svc.get_recipe_ids_from_meals(meal_ids)
                    next_widget.loadShoppingList(recipe_ids)
            except Exception as e:
                DebugLogger.log(f"Error refreshing shopping list: {e}", "error")

        if current_widget != next_widget:
            self.sw_pages.setCurrentWidget(next_widget)

        # ⚠️ Temporarily disabled until multi-effects solution is stable
        """ if current_widget != next_widget:
            Animator.transition_stack(current_widget, next_widget, self.sw_pages)
        else:
            self.sw_pages.setCurrentWidget(next_widget) """

    def show_full_recipe(self, recipe):
        """Navigate to ViewRecipe view with the specified recipe."""
        DebugLogger.log(f"NavigationService.show_full_recipe called for: {recipe.recipe_name}", "info")

        # Remove existing view_recipe widget if it exists
        if "view_recipe" in self.page_instances:
            old_widget = self.page_instances["view_recipe"]
            self.sw_pages.removeWidget(old_widget)
            old_widget.deleteLater()

        # Create new ViewRecipe widget with the specific recipe
        full_recipe_widget = ViewRecipe(recipe, navigation_service=self)

        # Connect the back button to return to recipes
        full_recipe_widget.back_clicked.connect(lambda: self.switch_to("browse_recipes"))

        # Add to navigation
        self.page_instances["view_recipe"] = full_recipe_widget
        self.sw_pages.addWidget(full_recipe_widget)

        # Navigate to the full recipe view
        self.sw_pages.setCurrentWidget(full_recipe_widget)
