"""services/navigation_service.py

Connects signals to their respective slots for handling sidebar and page navigation.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtWidgets import QStackedWidget

from app.core.services import PlannerService, ShoppingService
from app.ui.animations import Animator
from app.ui.views import (AddRecipes, Dashboard, MealPlanner, ShoppingList,
                          ViewRecipes)


# ── Class Definition ────────────────────────────────────────────────────────────
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
            "view_recipes": ViewRecipes,
            "shopping_list": ShoppingList,
            "add_recipe": AddRecipes,
        }
        for name, page_class in page_map.items():
            instance = page_class()
            self.page_instances[name] = instance
            self.sw_pages.addWidget(instance)

    def switch_to(self, page_name: str):
        """Switch stacked widget to the given page."""
        # this is the core logic from app.py's _switch_page
        if page_name not in self.page_instances:
            return

        next_widget = self.page_instances[page_name]
        current_widget = self.sw_pages.currentWidget()

        if isinstance(current_widget, MealPlanner):
            current_widget.save_meal_plan()

        # refresh ShoppingList if navigating to it
        if page_name == "shopping_list" and isinstance(next_widget, ShoppingList):
            # load saved meals and derive recipe IDs via services
            planner_svc = PlannerService()
            meal_ids = planner_svc.load_saved_meal_ids()
            shopping_svc = ShoppingService()
            recipe_ids = shopping_svc.get_recipe_ids_from_meals(meal_ids)
            next_widget.load_shopping_list(recipe_ids)
        
        if current_widget != next_widget:
            Animator.transition_stack(current_widget, next_widget, self.sw_pages)
        else:
            self.sw_pages.setCurrentWidget(next_widget)