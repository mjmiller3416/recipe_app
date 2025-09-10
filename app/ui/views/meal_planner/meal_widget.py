
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from _dev_tools import DebugLogger
from app.core.dtos import MealSelectionCreateDTO, MealSelectionUpdateDTO
from app.core.models import MealSelection
from app.core.services import PlannerService, RecipeService
from app.core.utils import (
    create_error_context,
    error_boundary,
    log_and_handle_exception,
    validate_positive_number)
from app.ui.components.composite.recipe_card import LayoutSize, create_recipe_card
from app.ui.utils import batch_connect_signals, create_tooltip_event_filter

# ── Constants ──
SIDE_SLOT_COUNT = 3
LAYOUT_SPACING = 15


class MealWidget(QWidget):
    """
    A QWidget layout that organizes a main dish and side dish RecipeViewers.
    Handles layout creation, user interaction, and internal meal state tracking.
    """

    # signal emitted when a recipe slot requests selection; passes the slot key (e.g., 'main', 'side1')
    recipe_selection_requested = Signal(str)

    def __init__(self, planner_service: PlannerService, parent=None):
        super().__init__(parent)
        self.planner_service = planner_service
        self.recipe_service = RecipeService() # for loading recipe details
        self._meal_model: MealSelection | None = None
        self.meal_slots = {}
        self.tooltip_filter = create_tooltip_event_filter()

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        """
        Setup the UI layout for the MealWidget.

        This method initializes the layout with a large main dish card and 3 small side dishes.
        Following the new design: large card on top, 3 small cards in a row below.
        """
        self.setObjectName("MealWidget")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(LAYOUT_SPACING)

        # Main Dish (Large Card)
        self.main_slot = create_recipe_card(LayoutSize.LARGE)
        self.meal_slots["main"] = self.main_slot
        self.main_layout.addWidget(self.main_slot, 0, Qt.AlignHCenter | Qt.AlignTop)

        # Side Dishes Row
        self.side_layout = QHBoxLayout()
        self.side_layout.setSpacing(LAYOUT_SPACING)

        for i in range(1, SIDE_SLOT_COUNT + 1):
            side_slot = create_recipe_card(LayoutSize.SMALL)
            side_slot.setEnabled(False) # initially disabled
            side_slot.setToolTip("Select a main dish first") # tooltip for disabled state
            side_slot.installEventFilter(self.tooltip_filter)
            self.side_layout.addWidget(side_slot)
            self.meal_slots[f"side{i}"] = side_slot

        self.main_layout.addLayout(self.side_layout)

    def _connect_signals(self):
        """
        Connect signal from RecipeViewer to the update_recipe_selection method.
        """
        signal_connections = []

        for key, slot in self.meal_slots.items():
            # Create bound methods to avoid closure issues
            recipe_handler = self._create_recipe_selection_handler(key)
            add_meal_handler = self._create_add_meal_handler(key)

            signal_connections.extend([
                (slot.recipe_selected, recipe_handler),
                (slot.add_meal_clicked, add_meal_handler)
            ])

        batch_connect_signals(signal_connections)

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

        # Update Internal Model
        if key == "main":
            self._meal_model.main_recipe_id = recipe_id
            self._enable_side_slots()
        else:
            # Side Slot Update
            setattr(self._meal_model, f"side_recipe_{key[-1]}_id", recipe_id)
        # fetch recipe and update the slot UI, but block signals to avoid recursion
        slot = self.meal_slots.get(key)
        if slot is not None:
            recipe = self.recipe_service.get_recipe(recipe_id)
            slot.blockSignals(True)
            slot.set_recipe(recipe)
            slot.blockSignals(False)

    def _create_recipe_selection_handler(self, key: str):
        """Create recipe selection handler for the given slot key."""
        def handler(recipe_id: int):
            self.update_recipe_selection(key, recipe_id)
        return handler

    def _create_add_meal_handler(self, key: str):
        """Create add meal handler for the given slot key."""
        def handler():
            DebugLogger.log(f"Add meal clicked for slot: {key}", "info")
            self.recipe_selection_requested.emit(key)
        return handler

    def _enable_side_slots(self):
        """Enable side dish slots when main dish is selected."""
        for i in range(1, SIDE_SLOT_COUNT + 1):
            slot = self.meal_slots[f"side{i}"]
            slot.setEnabled(True)
            slot.setToolTip("")

    def _create_dto_fields(self) -> dict:
        """Create common DTO fields from meal model."""
        return {
            'meal_name': self._meal_model.meal_name,
            'main_recipe_id': self._meal_model.main_recipe_id,
            'side_recipe_1_id': self._meal_model.side_recipe_1_id,
            'side_recipe_2_id': self._meal_model.side_recipe_2_id,
            'side_recipe_3_id': self._meal_model.side_recipe_3_id
        }

    @error_boundary(fallback=None, logger_func=DebugLogger.log)
    def save_meal(self):
        if not self._meal_model:
            return

        dto_fields = self._create_dto_fields()

        if self._meal_model.id is None:
            create_dto = MealSelectionCreateDTO(**dto_fields)
            response_dto = self.planner_service.create_meal_selection(create_dto)
            if response_dto:
                self._meal_model.id = response_dto.id
        else:
            update_dto = MealSelectionUpdateDTO(**dto_fields)
            self.planner_service.update_meal_selection(self._meal_model.id, update_dto)

    @error_boundary(fallback=None, logger_func=DebugLogger.log)
    def load_meal(self, meal_id: int):
        """
        Load a meal by its ID and populate the RecipeViewers.
        """
        # Validate meal ID
        validation = validate_positive_number(meal_id, "Meal ID")
        if not validation.is_valid:
            DebugLogger.log(f"Invalid meal ID: {validation.error_message}", "error")
            return

        response_dto = self.planner_service.get_meal_selection(meal_id)
        if not response_dto:
            error_context = create_error_context(
                "meal_load",
                {"meal_id": meal_id},
                {"component": "MealWidget"}
            )
            log_and_handle_exception(
                "meal_load_not_found",
                ValueError(f"No meal found with ID {meal_id}"),
                DebugLogger.log,
                error_context
            )
            return

        self._meal_model = MealSelection(
            id=response_dto.id,
            meal_name=response_dto.meal_name,
            main_recipe_id=response_dto.main_recipe_id,
            side_recipe_1_id=response_dto.side_recipe_1_id,
            side_recipe_2_id=response_dto.side_recipe_2_id,
            side_recipe_3_id=response_dto.side_recipe_3_id
        )

        # Load Recipes
        self._load_main_recipe()
        self._load_side_recipes()

    def _load_main_recipe(self):
        """Load main recipe into the main slot."""
        main = self.recipe_service.get_recipe(self._meal_model.main_recipe_id)
        self.main_slot.set_recipe(main)

    def _load_side_recipes(self):
        """Load side recipes into their respective slots."""
        for idx in range(1, SIDE_SLOT_COUNT + 1):
            rid = getattr(self._meal_model, f"side_recipe_{idx}_id")
            recipe = self.recipe_service.get_recipe(rid) if rid else None
            self.meal_slots[f"side{idx}"].set_recipe(recipe)
