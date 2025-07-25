"""app/ui/pages/meal_planner/meal_widget.py

Defines the MealWidget widget, which organizes recipe slots for a main dish and up to three side dishes.
This is a pure UI widget responsible only for rendering and updating meal data selection state.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from typing import Optional

from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QToolTip, QVBoxLayout, QWidget

from app.core.dtos.planner_dtos import (MealSelectionCreateDTO,
                                        MealSelectionUpdateDTO)
from app.core.models.meal_selection import MealSelection
from app.core.services.planner_service import PlannerService
# use RecipeService instead of direct Recipe.get()
from app.core.services.recipe_service import RecipeService
from app.ui.components.composite.recipe_card import LayoutSize, RecipeCard
from dev_tools import DebugLogger


# ── Class Definition ────────────────────────────────────────────────────────────
class MealWidget(QWidget):
    """
    A QWidget layout that organizes a main dish and side dish RecipeViewers.
    Handles layout creation, user interaction, and internal meal state tracking.
    """

    # Signal emitted when a recipe slot requests selection; passes the slot key (e.g., 'main', 'side1')
    recipe_selection_requested = Signal(str)
    def __init__(self, planner_service: PlannerService, parent=None):
        super().__init__(parent)
        self.planner_service = planner_service
        # for loading recipe details
        self.recipe_service = RecipeService()
        self._meal_model: MealSelection | None = None
        self.meal_slots = {}

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
            # when an empty slot's add button is clicked, request recipe selection
            slot.add_meal_clicked.connect(lambda k=key: self.recipe_selection_requested.emit(k))

    def update_recipe_selection(self, key: str, recipe_id: int) -> None:
        """
        Update the meal model with the selected recipe ID.

        Args:
            key (str): The key representing the recipe slot (main, side1, side2, side3).
            recipe_id (int): The ID of the selected recipe.
        """
        if not self._meal_model:
            self._meal_model = MealSelection(
                meal_name="Custom Meal",  # or dynamic name later
                main_recipe_id=recipe_id if key == "main" else 0
            )

        # Update internal model
        if key == "main":
            self._meal_model.main_recipe_id = recipe_id
            # ── Enable Side Slots ──
            for side in ("side1", "side2", "side3"):
                self.meal_slots[side].setEnabled(True)
                self.meal_slots[side].setToolTip("")
        else:
            # side slot update
            setattr(self._meal_model, f"side_recipe_{key[-1]}_id", recipe_id)
        # Fetch recipe and update the slot UI, but block signals to avoid recursion
        slot = self.meal_slots.get(key)
        if slot is not None:
            recipe = self.recipe_service.get_recipe(recipe_id)
            slot.blockSignals(True)
            slot.set_recipe(recipe)
            slot.blockSignals(False)

    def save_meal(self):
        if not self._meal_model:
            return

        try:
            if self._meal_model.id is None:
                create_dto = MealSelectionCreateDTO(
                    meal_name=self._meal_model.meal_name,
                    main_recipe_id=self._meal_model.main_recipe_id,
                    side_recipe_1_id=self._meal_model.side_recipe_1_id,
                    side_recipe_2_id=self._meal_model.side_recipe_2_id,
                    side_recipe_3_id=self._meal_model.side_recipe_3_id
                )
                response_dto = self.planner_service.create_meal_selection(create_dto)
                if response_dto:
                    self._meal_model.id = response_dto.id
            else:
                update_dto = MealSelectionUpdateDTO(
                    meal_name=self._meal_model.meal_name,
                    main_recipe_id=self._meal_model.main_recipe_id,
                    side_recipe_1_id=self._meal_model.side_recipe_1_id,
                    side_recipe_2_id=self._meal_model.side_recipe_2_id,
                    side_recipe_3_id=self._meal_model.side_recipe_3_id
                )
                self.planner_service.update_meal_selection(self._meal_model.id, update_dto)

        except Exception as e:
            DebugLogger.log(f"[MealWidget] Failed to save meal: {e}", "error")

    def load_meal(self, meal_id: int):
        """
        Load a meal by its ID and populate the RecipeViewers.
        """
        try:
            response_dto = self.planner_service.get_meal_selection(meal_id)
            if not response_dto:
                DebugLogger.log(f"[MealWidget] Failed to load meal with ID {meal_id}", "error")
                return

            self._meal_model = MealSelection(
                id=response_dto.id,
                meal_name=response_dto.meal_name,
                main_recipe_id=response_dto.main_recipe_id,
                side_recipe_1_id=response_dto.side_recipe_1_id,
                side_recipe_2_id=response_dto.side_recipe_2_id,
                side_recipe_3_id=response_dto.side_recipe_3_id
            )

            # load recipe models via RecipeService
            main = self.recipe_service.get_recipe(self._meal_model.main_recipe_id)
            self.main_slot.set_recipe(main)
            for idx in (1, 2, 3):
                rid = getattr(self._meal_model, f"side_recipe_{idx}_id")
                slot = self.meal_slots.get(f"side{idx}")
                recipe = self.recipe_service.get_recipe(rid) if rid else None
                slot.set_recipe(recipe)

        except Exception as e:
            DebugLogger.log(f"[MealWidget] Error loading meal {meal_id}: {e}", "error")


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
