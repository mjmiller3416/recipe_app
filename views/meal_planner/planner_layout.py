"""views/meal_planner/planner_layout.py

Defines the PlannerLayout widget, which organizes recipe slots for a main dish and up to three side dishes.
This is a pure UI widget responsible only for rendering and updating meal data selection state.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QEvent, Qt
from PySide6.QtWidgets import QHBoxLayout, QToolTip, QVBoxLayout, QWidget

from recipe_widget.constants import LayoutSize
from recipe_widget.recipe_widget import RecipeWidget
from database.models.recipe import Recipe  

# ── Class Definition ────────────────────────────────────────────────────────────
class PlannerLayout(QWidget):
    """
    A QWidget layout that organizes a main dish and side dish RecipeWidgets.
    Handles layout creation, user interaction, and internal meal state tracking.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.meal_slots = {}
        self.current_meal = {"main": None, "side1": None, "side2": None, "side3": None}

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """
        Setup the UI layout for the PlannerLayout.

        This method initializes the layout and adds RecipeWidgets for main and side dishes.
        """
        self.setObjectName("PlannerLayout")
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # ── Main Dish ──
        self.main_slot = RecipeWidget(size=LayoutSize.MEDIUM)
        self.meal_slots["main"] = self.main_slot
        self.main_layout.addWidget(self.main_slot)

        # ── Side Dishes ──
        self.side_layout = QVBoxLayout()
        self.side_layout.setSpacing(10)

        for i in range(1, 4):
            side_slot = RecipeWidget(size=LayoutSize.SMALL)
            side_slot.setEnabled(False)
            side_slot.setToolTip("Select a main dish first")
            self.side_layout.addWidget(side_slot)
            self.meal_slots[f"side{i}"] = side_slot

        self.main_layout.addLayout(self.side_layout)

    def _connect_signals(self):
        """
        Connect signals from each RecipeWidget to the update_meal method.
        """
        for key, slot in self.meal_slots.items():
            slot.recipe_selected.connect(lambda rid, k=key: self.update_meal(k, rid))

    def update_meal(self, key: str, recipe_id: str) -> None:
        """
        Update the meal selection for the given key (main or side).

        Args:
            key (str): One of 'main', 'side1', 'side2', 'side3'.
            recipe_id (str): The ID of the selected recipe.
        """
        self.current_meal[key] = recipe_id

        if key == "main":
            for side in ["side1", "side2", "side3"]:
                self.meal_slots[side].setEnabled(True)
                self.meal_slots[side].setToolTip("")

    def get_meal_data(self) -> dict[str, str | None]:
        """Returns the current meal selection state."""
        return self.current_meal.copy()

    def set_meal_data(self, meal_dict):
        for key, rid in meal_dict.items():
            if key in self.meal_slots and rid:
                self.current_meal[key] = rid

                # Fetch and display the recipe
                recipe = Recipe.get(rid)
                if recipe:
                    self.meal_slots[key].set_recipe(recipe)

                # Enable side slots if main is set
                if key == "main":
                    for side in ["side1", "side2", "side3"]:
                        self.meal_slots[side].setEnabled(True)
                        self.meal_slots[side].setToolTip("")

    def eventFilter(self, obj, event):
        """
        Show tooltip on disabled RecipeWidgets.

        Args:
            obj: The object receiving the event.
            event: The event itself.
        """
        if event.type() == QEvent.ToolTip and not obj.isEnabled():
            QToolTip.showText(event.globalPos(), obj.toolTip(), obj)
            return True
        return super().eventFilter(obj, event)
