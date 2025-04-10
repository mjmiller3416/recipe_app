# recipe_app/meal_planner/planner_layout.py
"""
Module: meal_planner.planner_layout

This module defines the PlannerLayout class, which is a custom QWidget that organizes MealWidgets for meal planning.
It includes a main dish and up to three side dishes, enabling users to select recipes for each meal type.
"""

# 🔸Third-party Imports
from core.helpers.qt_imports import QWidget, QHBoxLayout, QVBoxLayout, QEvent, QToolTip

# 🔸 Local Imports
from meal_planner.meal_widget import MealWidget

class PlannerLayout(QWidget):
    """
    PlannerLayout is a custom QWidget that organizes MealWidgets for meal planning.

    This layout includes a main dish and up to three side dishes, enabling users to select recipes for each meal type.

    Attributes:
        meal_widgets (dict): A dictionary mapping meal type keys to their respective MealWidget instances.
        current_meal (dict): A dictionary tracking the currently selected recipe IDs for main and side dishes.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.meal_widgets = {}
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

        # Main Dish Widget
        self.main_recipe = MealWidget(meal_type="main")
        self.meal_widgets["main"] = self.main_recipe
        self.main_layout.addWidget(self.main_recipe)

        # Side Dishes (vertical stack)
        self.side_layout = QVBoxLayout()
        self.side_layout.setSpacing(10)

        for i in range(1, 4):
            key = f"side{i}"
            widget = MealWidget(meal_type="side")
            widget.setEnabled(False)
            widget.setToolTip("Please select a main recipe first.")
            widget.installEventFilter(self)
            self.meal_widgets[key] = widget
            self.side_layout.addWidget(widget)

        self.main_layout.addLayout(self.side_layout)

    def _connect_signals(self):
        """
        Connect signals from each MealWidget to the update_meal method.

        This method connects the recipe_selected signal from each MealWidget to the update_meal 
        method, allowing the PlannerLayout to update its internal state when a recipe is selected.
        """
        for key, widget in self.meal_widgets.items():
            widget.recipe_selected.connect(lambda mt, rid, k=key: self.update_meal(k, rid))

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
                self.meal_widgets[side].setEnabled(True)
                self.meal_widgets[side].setToolTip("")
        elif key.startswith("side") and self.current_meal["main"] is None:
            # Failsafe (should never trigger)
            return

    def get_meal_data(self):
        """Returns the internal meal selection state."""
        return self.current_meal.copy()

    def set_meal_data(self, meal_dict):
        """Pre-populates the layout with given recipe IDs."""
        for key, recipe_id in meal_dict.items():
            if recipe_id:
                self.meal_widgets[key].set_selected_recipe(recipe_id)
                if key == "main":
                    for side in ["side1", "side2", "side3"]:
                        self.meal_widgets[side].setEnabled(True)
                        self.meal_widgets[side].setToolTip("")

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
