"""app/ui/pages/meal_planner/meal_widget.py

Defines the MealWidget widget, which organizes recipe slots for a main dish and up to three side dishes.
This is a pure UI widget responsible only for rendering and updating meal data selection state.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from typing import Optional

from PySide6.QtCore import QEvent, Qt
from PySide6.QtWidgets import QHBoxLayout, QToolTip, QVBoxLayout, QWidget

from app.core.data.models.meal_selection import MealSelection
from app.core.data.models.recipe import Recipe
from app.core.services.meal_service import MealService
from app.core.utils import DebugLogger
from app.ui.components.recipe_card import RecipeCard
from app.ui.components.recipe_card.constants import LayoutSize


# ── Class Definition ────────────────────────────────────────────────────────────
class MealWidget(QWidget):
    """
    A QWidget layout that organizes a main dish and side dish RecipeViewers.
    Handles layout creation, user interaction, and internal meal state tracking.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.meal_slots = {}
        self._meal_model: Optional[MealSelection] = None

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """
        Setup the UI layout for the MealWidget.

        This method initializes the layout and adds RecipeViewers for main and side dishes.
        """
        self.setObjectName("MealWidget")
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # ── Main Dish ──
        self.main_slot = RecipeCard(size=LayoutSize.MEDIUM)
        self.meal_slots["main"] = self.main_slot
        self.main_layout.addWidget(self.main_slot)

        # ── Side Dishes ──
        self.side_layout = QVBoxLayout()
        self.side_layout.setSpacing(10)

        for i in range(1, 4):
            side_slot = RecipeCard(size=LayoutSize.SMALL)
            side_slot.setEnabled(False) # initially disabled
            side_slot.setToolTip("Select a main dish first") # tooltip for disabled state
            self.side_layout.addWidget(side_slot)
            self.meal_slots[f"side{i}"] = side_slot

        self.main_layout.addLayout(self.side_layout)

    def _connect_signals(self):
        """
        Connect signal from RecipeViewer to the update_recipe_selection method.
        """
        for key, slot in self.meal_slots.items():
            slot.recipe_selected.connect(lambda rid, k=key: self.update_recipe_selection(k, rid))

    def update_recipe_selection(self, key: str, recipe_id) -> None:
        """
        Update the meal model with the selected recipe ID.

        This slot is triggered by :class:`RecipeCard` widgets. Some PySide
        signal connections were inadvertently passing the widget instance
        itself instead of the recipe ID, which resulted in ``int()`` casting
        errors when constructing :class:`MealSelection` models.  To guard
        against this we coerce ``recipe_id`` to an ``int`` when possible.

        Args:
            key (str): The key representing the recipe slot (main, side1, side2, side3).
            recipe_id: The ID of the selected recipe or a widget containing it.
        """
        # ── Normalize Input ──
        if not isinstance(recipe_id, int):
            rid = getattr(recipe_id, "id", None)
            if rid is None:
                recipe_attr = getattr(recipe_id, "recipe", None)
                if callable(recipe_attr):
                    recipe_attr = recipe_attr()
                if recipe_attr is not None:
                    rid = getattr(recipe_attr, "id", None)
            recipe_id = rid if isinstance(rid, int) else 0
        if not self._meal_model:
            self._meal_model = MealSelection(
                meal_name="Custom Meal",  # or dynamic name later
                main_recipe_id=recipe_id if key == "main" else 0
            )

        if key == "main": 
            self._meal_model.main_recipe_id = recipe_id # update main recipe 
            # ── Enable Side Slots ──
            for side in ["side1", "side2", "side3"]:
                self.meal_slots[side].setEnabled(True)
                self.meal_slots[side].setToolTip("")

        elif key in ("side1", "side2", "side3"): # update side recipe
            setattr(self._meal_model, f"side_recipe_{key[-1]}", recipe_id)

    def save_meal(self):
        if not self._meal_model:
            return

        if self._meal_model.id is None:
            saved = MealService.create_meal(self._meal_model)
            self._meal_model = saved
        else:
            MealService.update_meal(self._meal_model)

    def load_meal(self, meal_id: int):
        """
        Load a meal by its ID and populate the RecipeViewers.

        Args:
            meal_id (int): The ID of the meal to load.
        """
        self._meal_model = MealService.load_meal(meal_id)

        if not self._meal_model:
            DebugLogger.log(f"[MealWidget] Failed to load meal with ID {meal_id}", "error")
            return

        self.main_slot.set_recipe(Recipe.get(self._meal_model.main_recipe_id))
        self.meal_slots["side1"].set_recipe(Recipe.get(self._meal_model.side_recipe_1))
        self.meal_slots["side2"].set_recipe(Recipe.get(self._meal_model.side_recipe_2))
        self.meal_slots["side3"].set_recipe(Recipe.get(self._meal_model.side_recipe_3))

    def eventFilter(self, obj, event):
        """
        Show tooltip on disabled RecipeViewers.

        Args:
            obj: The object receiving the event.
            event: The event itself.
        """
        if event.type() == QEvent.ToolTip and not obj.isEnabled():
            QToolTip.showText(event.globalPos(), obj.toolTip(), obj)
            return True
        return super().eventFilter(obj, event)
