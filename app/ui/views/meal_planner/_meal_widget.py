"""app/ui/views/meal_planner/meal_widget.py
A QWidget layout that organizes a main dish and side dish RecipeViewers.
Handles layout creation, user interaction, and delegates business logic to ViewModel.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from typing import Dict, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from _dev_tools.debug_logger import DebugLogger
from app.ui.components.composite.recipe_card import LayoutSize, create_recipe_card
from app.ui.utils.event_utils import (
    batch_connect_signals,
    create_tooltip_event_filter,
    signal_blocker,
)
from app.ui.view_models.meal_widget_vm import MealWidgetViewModel

class MealWidget(QWidget):
    """
    A QWidget layout that organizes a main dish and side dish RecipeViewers.
    Handles layout creation, user interaction, and delegates business logic to ViewModel.
    """

    # signal emitted when a recipe slot requests selection; passes the slot key (e.g., 'main', 'side1')
    recipe_selection_requested = Signal(str)

    def __init__(self, meal_view_model: MealWidgetViewModel, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.view_model = meal_view_model
        self.meal_slots: Dict[str, QWidget] = {}
        self.tooltip_filter = create_tooltip_event_filter()

        self._build_ui()
        self._connect_signals()
        self._connect_view_model_signals()

    def _build_ui(self) -> None:
        """
        Setup the UI layout for the MealWidget.

        This method initializes the layout with a large main dish card and 3 small side dishes.
        Following the new design: large card on top, 3 small cards in a row below.
        """
        self.setObjectName("MealWidget")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(15)

        # Main Dish (Large Card)
        self.main_slot = create_recipe_card(LayoutSize.LARGE)
        self.meal_slots["main"] = self.main_slot
        self.main_layout.addWidget(self.main_slot, 0, Qt.AlignHCenter | Qt.AlignTop)

        # Side Dishes Row
        self.side_layout = QHBoxLayout()
        self.side_layout.setSpacing(15)

        for i in range(1, 3 + 1):
            side_slot = create_recipe_card(LayoutSize.SMALL)
            side_slot.setEnabled(False) # initially disabled
            side_slot.setToolTip("Select a main dish first") # tooltip for disabled state
            side_slot.installEventFilter(self.tooltip_filter)
            self.side_layout.addWidget(side_slot)
            self.meal_slots[f"side{i}"] = side_slot

        self.main_layout.addLayout(self.side_layout)

    def _connect_signals(self) -> None:
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

    def _connect_view_model_signals(self) -> None:
        """Connect ViewModel signals to UI updates."""
        # Recipe slot updates
        self.view_model.recipe_slot_updated.connect(self._on_recipe_slot_updated)

        # Side slots enabled/disabled
        self.view_model.side_slots_enabled_changed.connect(self._on_side_slots_enabled_changed)

        # Meal data changes
        self.view_model.meal_data_changed.connect(self._on_meal_data_changed)

        # Recipe selection requests (forward to parent)
        self.view_model.recipe_selection_requested.connect(self.recipe_selection_requested.emit)

    def update_recipe_selection(self, key: str, recipe_id: int) -> None:
        """
        Update recipe selection using ViewModel.

        Args:
            key (str): The key representing the recipe slot (main, side1, side2, side3).
            recipe_id (int): The ID of the selected recipe.
        """
        self.view_model.update_recipe_selection(key, recipe_id)

    def _on_recipe_slot_updated(self, slot_key: str, recipe_dto) -> None:
        """Handle recipe slot update from ViewModel."""
        slot = self.meal_slots.get(slot_key)
        if slot is not None:
            with signal_blocker(slot):
                slot.set_recipe(recipe_dto)

    def _on_side_slots_enabled_changed(self) -> None:
        """Handle side slots enabled state change from ViewModel."""
        if self.view_model.side_slots_enabled:
            self._enable_side_slots()
        else:
            self._disable_side_slots()

    def _on_meal_data_changed(self, meal_summary_dto) -> None:
        """Handle meal data changes from ViewModel."""
        # Update UI if needed based on meal data changes
        pass  # UI updates are handled by slot updates

    def _create_recipe_selection_handler(self, key: str) -> callable:
        """Create recipe selection handler for the given slot key."""
        def handler(recipe_id: int) -> None:
            self.update_recipe_selection(key, recipe_id)
        return handler

    def _create_add_meal_handler(self, key: str) -> callable:
        """Create add meal handler for the given slot key."""
        def handler() -> None:
            DebugLogger.log(f"Add meal clicked for slot: {key}", "info")
            self.view_model.request_recipe_selection(key)
        return handler

    def _enable_side_slots(self) -> None:
        """Enable side dish slots when main dish is selected."""
        for i in range(1, 3 + 1):
            slot = self.meal_slots[f"side{i}"]
            slot.setEnabled(True)
            slot.setToolTip("")

    def _disable_side_slots(self) -> None:
        """Disable side dish slots and reset their tooltips."""
        for i in range(1, 3 + 1):
            slot = self.meal_slots[f"side{i}"]
            slot.setEnabled(False)
            slot.setToolTip("Select a main dish first")

    def save_meal(self) -> bool:
        """Save the meal using ViewModel."""
        return self.view_model.save_meal()

    def load_meal(self, meal_id: int) -> bool:
        """Load a meal using ViewModel."""
        return self.view_model.load_meal(meal_id)

    def get_meal_id(self) -> int | None:
        """Get the current meal ID from ViewModel."""
        return self.view_model.meal_id

    def has_changes(self) -> bool:
        """Check if meal has unsaved changes."""
        return self.view_model.has_changes
