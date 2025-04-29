# recipe_app/meal_planner/planner_layout.py

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QToolTip
from PySide6.QtCore import Qt

from core.modules.recipe_module import Recipe
from database import DB_INSTANCE
from dev_sandbox.recipe_widget.recipe_slot import RecipeSlot
from dev_sandbox.recipe_widget.constants   import LayoutSize

# ── Class Definition ────────────────────────────────────────────────────────────
class PlannerLayout(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.meal_slots = {}
        self.current_meal = {"main": None, "side1": None, "side2": None, "side3": None}

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """
        Setup the UI layout for the PlannerLayout.

        This method initializes the layout and adds MealWidgets for main and side dishes.
        """
        self.setObjectName("PlannerLayout")
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        #🔹Main Dish Widget
        self.main_slot = RecipeSlot(size=LayoutSize.MEDIUM)
        self.meal_slots["main"] = self.main_slot
        self.main_layout.addWidget(self.main_slot)

        #🔹Side Dishes (vertical stack)
        self.side_layout = QVBoxLayout()
        self.side_layout.setSpacing(10)

        for i in range(1, 4):
            side_slot = RecipeSlot(size=LayoutSize.SMALL) # create side dish slot

            # set tooltip for disabled side slots
            side_slot.setEnabled(False)
            side_slot.setToolTip("Select a main dish first")

            # add to layout
            self.side_layout.addWidget(side_slot)
            self.meal_slots[f"side{i}"] = side_slot

        self.main_layout.addLayout(self.side_layout)

    def _connect_signals(self):
        """
        Connect signals from each MealWidget to the update_meal method.

        This method connects the recipe_selected signal from each MealWidget to the update_meal
        method, allowing the PlannerLayout to update its internal state when a recipe is selected.
        """
        for key, slot in self.meal_slots.items():
            # k=key closes over current loop variable
            slot.recipe_selected.connect(lambda rid, k=key: self.update_meal(k, rid))

    def update_meal(self, key, recipe_id):
        """
        Update the meal selection for the given key (main or side).

        This method updates the internal state of the current meal based on the selected recipe ID
        for the given meal type key.

        Args:
            key (str): The meal type key (e.g., "main", "side1", "side2", "side3").
            recipe_id (str): The ID of the selected recipe.
        """
        self.current_meal[key] = recipe_id

        if key == "main":
            for side in ["side1", "side2", "side3"]:
                self.meal_slots[side].setEnabled(True)
        elif key.startswith("side") and self.current_meal["main"] is None:
            # Failsafe (should never trigger)
            return

    def get_meal_data(self):
        """Returns the internal meal selection state."""
        return self.current_meal.copy()

    def set_meal_data(self, meal_dict):
        """Pre-populates the layout with given recipe IDs."""
        for key, slot in self.meal_slots.items():
            rid = meal_dict.get(key)
            if rid:
                recipe = DB_INSTANCE.get_recipe(rid)
                slot.set_recipe(recipe)

                if key == "main": # ensure main dish is enabled
                    for side in ["side1", "side2", "side3"]:
                        self.meal_slots[side].setEnabled(True)
                        self.meal_slots[side].setToolTip("")

    def eventFilter(self, obj, event):
        """
        Custom event filter to handle tooltips for disabled MealWidgets.

        This method intercepts events for the MealWidgets to show a tooltip when they are disabled.

        Args:
            obj: The object that received the event.
            event: The event being processed.
        """
        if event.type() == QEvent.ToolTip and not obj.isEnabled():
            QToolTip.showText(event.globalPos(), obj.toolTip(), obj)
            return True
        return super().eventFilter(obj, event)
