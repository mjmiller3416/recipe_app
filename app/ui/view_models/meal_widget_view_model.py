"""app/ui/view_models/meal_widget_view_model.py

ViewModel for individual MealWidget operations implementing MVVM pattern.
Handles individual meal state management, recipe slot operations, and persistence
for single meal widgets within the meal planner interface.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import Any, Dict, Optional

from PySide6.QtCore import Signal
from sqlalchemy.orm import Session

from _dev_tools import DebugLogger
from app.core.dtos.planner_dtos import (
    MealSelectionCreateDTO, MealSelectionResponseDTO, MealSelectionUpdateDTO,
)
from app.core.dtos.recipe_dtos import RecipeResponseDTO
from app.core.services.planner_service import PlannerService
from app.core.services.recipe_service import RecipeService
from app.ui.view_models.base_view_model import BaseViewModel

# ── Meal Summary DTO for UI ────────────────────────────────────────────────────────────────────────────────
class MealSummaryDTO:
    """DTO for meal summary information displayed in UI."""
    
    def __init__(self, meal_name: str, main_recipe_name: str, side_count: int, has_changes: bool):
        self.meal_name = meal_name
        self.main_recipe_name = main_recipe_name
        self.side_count = side_count
        self.has_changes = has_changes


# ── Meal Widget ViewModel ──────────────────────────────────────────────────────────────────────────────────
class MealWidgetViewModel(BaseViewModel):
    """
    ViewModel for individual meal widget operations following MVVM pattern.
    
    Provides:
    - Individual meal state management
    - Recipe slot operations (main, side1, side2, side3) 
    - Meal persistence operations
    - Recipe loading and caching
    - Slot state management and validation
    """
    
    # Meal widget-specific signals
    meal_data_changed = Signal(object)          # MealSummaryDTO
    recipe_slot_updated = Signal(str, object)   # slot_key, RecipeResponseDTO or None
    side_slots_enabled_changed = Signal()       # side slots enabled after main selection
    meal_saved = Signal(int, str)               # meal_id, meal_name
    meal_loaded = Signal(int, str)              # meal_id, meal_name
    recipe_selection_requested = Signal(str)    # slot_key for UI coordination
    
    def __init__(self, planner_service: PlannerService, recipe_service: RecipeService, session: Session | None = None):
        """
        Initialize the MealWidgetViewModel with injected services.
        
        Args:
            planner_service: Service for meal planning operations
            recipe_service: Service for recipe operations
            session: Optional SQLAlchemy session for dependency injection
        """
        super().__init__(session)
        
        # Injected services (dependency injection pattern)
        self._planner_service = planner_service
        self._recipe_service = recipe_service
        
        # Meal state
        self._meal_id: Optional[int] = None
        self._meal_name: str = "Custom Meal"
        self._has_changes: bool = False
        
        # Recipe slot state - tracks recipe IDs for each slot
        self._recipe_slots: Dict[str, Optional[int]] = {
            'main': None,
            'side1': None,
            'side2': None,
            'side3': None
        }
        
        # Recipe cache - stores loaded recipes to avoid repeated service calls
        self._recipe_cache: Dict[int, RecipeResponseDTO] = {}
        
        # Side slots enabled state
        self._side_slots_enabled = False
        
        DebugLogger.log("MealWidgetViewModel initialized with service injection", "debug")
    
    # ── Properties ──────────────────────────────────────────────────────────────────────────────────────────────
    
    @property
    def meal_id(self) -> Optional[int]:
        """Get current meal ID."""
        return self._meal_id
    
    @property
    def meal_name(self) -> str:
        """Get current meal name."""
        return self._meal_name
    
    @property
    def has_changes(self) -> bool:
        """Check if meal has unsaved changes."""
        return self._has_changes
    
    @property
    def side_slots_enabled(self) -> bool:
        """Check if side slots are enabled."""
        return self._side_slots_enabled
    
    @property
    def is_new_meal(self) -> bool:
        """Check if this is a new (unsaved) meal."""
        return self._meal_id is None
    
    # ── Recipe Slot Operations ──────────────────────────────────────────────────────────────────────────────────
    
    def update_recipe_selection(self, slot_key: str, recipe_id: int) -> bool:
        """
        Update recipe selection for a specific meal slot.
        
        Args:
            slot_key: Slot identifier (main, side1, side2, side3)
            recipe_id: ID of the selected recipe
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        # Validate slot key
        if slot_key not in self._recipe_slots:
            self._emit_validation_errors([f"Invalid slot key: {slot_key}"])
            return False
        
        if recipe_id <= 0:
            self._emit_validation_errors(["Invalid recipe ID"])
            return False
        
        try:
            # Load and cache recipe if not already cached
            recipe = self._get_or_load_recipe(recipe_id)
            if not recipe:
                self._emit_validation_errors([f"Recipe {recipe_id} not found"])
                return False
            
            # Update slot
            old_recipe_id = self._recipe_slots[slot_key]
            self._recipe_slots[slot_key] = recipe_id
            
            # Enable side slots if main dish was selected
            if slot_key == 'main' and not self._side_slots_enabled:
                self._enable_side_slots()
            
            # Mark as changed if this is an actual change
            if old_recipe_id != recipe_id:
                self._set_has_changes(True)
            
            # Emit signals
            self.recipe_slot_updated.emit(slot_key, recipe)
            self._emit_meal_data_changed()
            
            DebugLogger.log(f"Updated {slot_key} slot with recipe {recipe_id}: {recipe.recipe_name}", "debug")
            return True
            
        except Exception as e:
            self._handle_error(e, f"Failed to update recipe selection for {slot_key}", "recipe_selection")
            return False
    
    def get_recipe_for_slot(self, slot_key: str) -> Optional[RecipeResponseDTO]:
        """
        Get recipe for a specific slot.
        
        Args:
            slot_key: Slot identifier
            
        Returns:
            Optional[RecipeResponseDTO]: Recipe DTO or None if slot is empty
        """
        if slot_key not in self._recipe_slots:
            return None
        
        recipe_id = self._recipe_slots[slot_key]
        if recipe_id is None:
            return None
        
        return self._get_or_load_recipe(recipe_id)
    
    def clear_recipe_slot(self, slot_key: str) -> bool:
        """
        Clear a recipe slot.
        
        Args:
            slot_key: Slot identifier
            
        Returns:
            bool: True if cleared successfully, False otherwise
        """
        if slot_key not in self._recipe_slots:
            self._emit_validation_errors([f"Invalid slot key: {slot_key}"])
            return False
        
        try:
            old_recipe_id = self._recipe_slots[slot_key]
            self._recipe_slots[slot_key] = None
            
            # Mark as changed if slot had a recipe
            if old_recipe_id is not None:
                self._set_has_changes(True)
            
            # Disable side slots if main slot was cleared
            if slot_key == 'main' and self._side_slots_enabled:
                self._disable_side_slots()
            
            # Emit signals
            self.recipe_slot_updated.emit(slot_key, None)
            self._emit_meal_data_changed()
            
            DebugLogger.log(f"Cleared {slot_key} slot", "debug")
            return True
            
        except Exception as e:
            self._handle_error(e, f"Failed to clear recipe slot {slot_key}", "slot_management")
            return False
    
    def request_recipe_selection(self, slot_key: str) -> bool:
        """
        Request recipe selection for a slot (triggers UI workflow).
        
        Args:
            slot_key: Slot identifier
            
        Returns:
            bool: True if request was valid, False otherwise
        """
        if slot_key not in self._recipe_slots:
            self._emit_validation_errors([f"Invalid slot key: {slot_key}"])
            return False
        
        # Validate side slot access
        if slot_key.startswith('side') and not self._side_slots_enabled:
            self._emit_validation_errors(["Select a main dish first"])
            return False
        
        try:
            self.recipe_selection_requested.emit(slot_key)
            DebugLogger.log(f"Recipe selection requested for {slot_key}", "debug")
            return True
            
        except Exception as e:
            self._handle_error(e, f"Failed to request recipe selection for {slot_key}", "recipe_selection")
            return False
    
    # ── Slot Management ────────────────────────────────────────────────────────────────────────────────────────
    
    def enable_side_slots(self) -> None:
        """Enable side dish slots (called after main dish selection)."""
        if not self._side_slots_enabled:
            self._side_slots_enabled = True
            self.side_slots_enabled_changed.emit()
            DebugLogger.log("Side slots enabled", "debug")
    
    def _enable_side_slots(self) -> None:
        """Internal method to enable side slots."""
        self.enable_side_slots()
    
    def _disable_side_slots(self) -> None:
        """Disable side slots and clear side recipes."""
        if self._side_slots_enabled:
            # Clear all side slots
            for slot_key in ['side1', 'side2', 'side3']:
                self._recipe_slots[slot_key] = None
                self.recipe_slot_updated.emit(slot_key, None)
            
            self._side_slots_enabled = False
            DebugLogger.log("Side slots disabled and cleared", "debug")
    
    def get_slot_state(self, slot_key: str) -> Dict[str, Any]:
        """
        Get current state for a specific slot.
        
        Args:
            slot_key: Slot identifier
            
        Returns:
            Dict with slot state information
        """
        if slot_key not in self._recipe_slots:
            return {'exists': False}
        
        recipe_id = self._recipe_slots[slot_key]
        recipe = self._get_or_load_recipe(recipe_id) if recipe_id else None
        
        return {
            'exists': True,
            'recipe_id': recipe_id,
            'recipe': recipe,
            'has_recipe': recipe is not None,
            'enabled': slot_key == 'main' or self._side_slots_enabled
        }
    
    # ── Meal Persistence ────────────────────────────────────────────────────────────────────────────────────────
    
    def save_meal(self) -> bool:
        """
        Save the current meal (create or update).
        
        Returns:
            bool: True if saved successfully, False otherwise
        """
        # Validate meal has main recipe
        if not self._recipe_slots['main']:
            self._emit_validation_errors(["Main recipe is required"])
            return False
        
        # Validate meal name
        if not self._meal_name.strip():
            self._emit_validation_errors(["Meal name is required"])
            return False
        
        try:
            self._set_processing_state(True)
            
            # Build meal data
            meal_data = {
                'meal_name': self._meal_name,
                'main_recipe_id': self._recipe_slots['main'],
                'side_recipe_1_id': self._recipe_slots['side1'],
                'side_recipe_2_id': self._recipe_slots['side2'],
                'side_recipe_3_id': self._recipe_slots['side3']
            }
            
            if self.is_new_meal:
                result = self._create_new_meal(meal_data)
            else:
                result = self._update_existing_meal(meal_data)
            
            self._set_processing_state(False)
            
            if result:
                self._set_has_changes(False)
                self.meal_saved.emit(result.id, result.meal_name)
                DebugLogger.log(f"Saved meal {result.id}: {result.meal_name}", "info")
                return True
            else:
                self._emit_validation_errors(["Failed to save meal"])
                return False
                
        except Exception as e:
            self._set_processing_state(False)
            self._handle_error(e, "Failed to save meal", "meal_saving")
            return False
    
    def load_meal(self, meal_id: int) -> bool:
        """
        Load a meal by ID and populate slots.
        
        Args:
            meal_id: ID of the meal to load
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        if meal_id <= 0:
            self._emit_validation_errors(["Invalid meal ID"])
            return False
        
        try:
            self._set_loading_state(True, f"Loading meal {meal_id}")
            
            # Load meal via service
            meal_dto = self._safe_execute(
                self._planner_service.get_meal_selection,
                f"Failed to load meal {meal_id}",
                meal_id
            )
            
            if not meal_dto:
                self._emit_validation_errors([f"Meal {meal_id} not found"])
                self._set_loading_state(False)
                return False
            
            # Update internal state
            self._meal_id = meal_dto.id
            self._meal_name = meal_dto.meal_name
            
            # Update recipe slots
            self._recipe_slots['main'] = meal_dto.main_recipe_id
            self._recipe_slots['side1'] = meal_dto.side_recipe_1_id
            self._recipe_slots['side2'] = meal_dto.side_recipe_2_id
            self._recipe_slots['side3'] = meal_dto.side_recipe_3_id
            
            # Enable side slots if main recipe exists
            if meal_dto.main_recipe_id:
                self._enable_side_slots()
            
            # Load recipes and emit slot updates
            self._load_and_emit_slot_updates()
            
            self._set_has_changes(False)
            self._set_loading_state(False)
            
            # Emit signals
            self.meal_loaded.emit(meal_dto.id, meal_dto.meal_name)
            self._emit_meal_data_changed()
            
            DebugLogger.log(f"Successfully loaded meal {meal_id}: {meal_dto.meal_name}", "info")
            return True
            
        except Exception as e:
            self._set_loading_state(False)
            self._handle_error(e, f"Failed to load meal {meal_id}", "meal_loading")
            return False
    
    def _create_new_meal(self, meal_data: Dict[str, Any]) -> Optional[MealSelectionResponseDTO]:
        """Create a new meal selection."""
        try:
            create_dto = MealSelectionCreateDTO(**meal_data)
            
            response_dto = self._safe_execute(
                self._planner_service.create_meal_selection,
                "Failed to create meal selection",
                create_dto
            )
            
            if response_dto:
                self._meal_id = response_dto.id
                return response_dto
            return None
            
        except Exception as e:
            raise e
    
    def _update_existing_meal(self, meal_data: Dict[str, Any]) -> Optional[MealSelectionResponseDTO]:
        """Update an existing meal selection."""
        try:
            update_dto = MealSelectionUpdateDTO(**meal_data)
            
            response_dto = self._safe_execute(
                self._planner_service.update_meal_selection,
                f"Failed to update meal {self._meal_id}",
                self._meal_id,
                update_dto
            )
            
            return response_dto
            
        except Exception as e:
            raise e
    
    def _load_and_emit_slot_updates(self) -> None:
        """Load recipes for all slots and emit update signals."""
        for slot_key, recipe_id in self._recipe_slots.items():
            if recipe_id:
                recipe = self._get_or_load_recipe(recipe_id)
                self.recipe_slot_updated.emit(slot_key, recipe)
            else:
                self.recipe_slot_updated.emit(slot_key, None)
    
    # ── Recipe Management ───────────────────────────────────────────────────────────────────────────────────────
    
    def _get_or_load_recipe(self, recipe_id: int) -> Optional[RecipeResponseDTO]:
        """
        Get recipe from cache or load from service.
        
        Args:
            recipe_id: Recipe ID to load
            
        Returns:
            Optional[RecipeResponseDTO]: Recipe DTO or None if not found
        """
        if recipe_id in self._recipe_cache:
            return self._recipe_cache[recipe_id]
        
        try:
            recipe = self._safe_execute(
                self._recipe_service.get_recipe,
                f"Failed to load recipe {recipe_id}",
                recipe_id
            )
            
            if recipe:
                self._recipe_cache[recipe_id] = recipe
            
            return recipe
            
        except Exception as e:
            DebugLogger.log(f"Error loading recipe {recipe_id}: {e}", "error")
            return None
    
    def clear_recipe_cache(self) -> None:
        """Clear the recipe cache."""
        self._recipe_cache.clear()
        DebugLogger.log("Recipe cache cleared", "debug")
    
    # ── State Management ────────────────────────────────────────────────────────────────────────────────────────
    
    def reset_meal_data(self) -> None:
        """Reset meal data to initial state."""
        try:
            # Clear meal state
            self._meal_id = None
            self._meal_name = "Custom Meal"
            
            # Clear recipe slots
            for slot_key in self._recipe_slots:
                self._recipe_slots[slot_key] = None
                self.recipe_slot_updated.emit(slot_key, None)
            
            # Disable side slots
            self._side_slots_enabled = False
            
            # Clear cache
            self.clear_recipe_cache()
            
            # Reset change tracking
            self._set_has_changes(False)
            
            # Emit updates
            self._emit_meal_data_changed()
            
            DebugLogger.log("Meal data reset to initial state", "debug")
            
        except Exception as e:
            self._handle_error(e, "Failed to reset meal data", "state_management")
    
    def set_meal_name(self, meal_name: str) -> bool:
        """
        Set the meal name.
        
        Args:
            meal_name: New meal name
            
        Returns:
            bool: True if set successfully, False otherwise
        """
        if not meal_name.strip():
            self._emit_validation_errors(["Meal name cannot be empty"])
            return False
        
        try:
            old_name = self._meal_name
            self._meal_name = meal_name.strip()
            
            if old_name != self._meal_name:
                self._set_has_changes(True)
                self._emit_meal_data_changed()
            
            return True
            
        except Exception as e:
            self._handle_error(e, "Failed to set meal name", "state_management")
            return False
    
    def get_meal_summary(self) -> MealSummaryDTO:
        """
        Get summary information about the current meal.
        
        Returns:
            MealSummaryDTO: Summary of meal state
        """
        main_recipe = self.get_recipe_for_slot('main')
        main_recipe_name = main_recipe.recipe_name if main_recipe else "No main dish"
        
        side_count = len([slot for slot in ['side1', 'side2', 'side3'] if self._recipe_slots[slot]])
        
        return MealSummaryDTO(
            meal_name=self._meal_name,
            main_recipe_name=main_recipe_name,
            side_count=side_count,
            has_changes=self._has_changes
        )
    
    def _set_has_changes(self, has_changes: bool) -> None:
        """Set the has_changes flag and emit signal if changed."""
        if self._has_changes != has_changes:
            self._has_changes = has_changes
            self._emit_meal_data_changed()
    
    def _emit_meal_data_changed(self) -> None:
        """Emit meal data changed signal with current summary."""
        summary = self.get_meal_summary()
        self.meal_data_changed.emit(summary)
    
    # ── State Reset ─────────────────────────────────────────────────────────────────────────────────────────────
    
    def reset_view_state(self) -> None:
        """Reset all ViewModel state to initial values."""
        try:
            # Reset meal data
            self.reset_meal_data()
            
            # Reset base state
            self.reset_state()
            
            DebugLogger.log("MealWidgetViewModel state reset", "info")
            
        except Exception as e:
            self._handle_error(e, "Failed to reset view state", "state_management")