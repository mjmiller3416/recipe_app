"""app/ui/view_models/meal_planner_view_model.py

ViewModel for Meal Planner view implementing MVVM pattern.
Handles business logic for meal selection, tab management, recipe loading,
and UI state management for meal planning operations.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import Any, Dict, List, Optional

from PySide6.QtCore import Signal
from sqlalchemy.orm import Session

from _dev_tools import DebugLogger
from app.core.dtos.planner_dtos import (
    MealPlanSaveResultDTO,
    MealPlanSummaryDTO,
    MealSelectionCreateDTO,
    MealSelectionResponseDTO,
    MealSelectionUpdateDTO,
)
from app.core.services.planner_service import PlannerService
from app.core.services.recipe_service import RecipeService
from app.ui.view_models.base_view_model import BaseViewModel

# ── Meal Planner ViewModel ─────────────────────────────────────────────────────────────────────────────────
class MealPlannerViewModel(BaseViewModel):
    """
    ViewModel for meal planner operations following MVVM pattern.
    
    Provides:
    - Tab management and meal widget coordination  
    - Recipe selection workflow management
    - Meal loading and saving operations with DTOs
    - Error handling and validation
    - State management for meal planning operations
    """
    
    # Meal planner-specific signals
    meal_loaded = Signal(object)  # MealSelectionResponseDTO
    meal_saved = Signal(str)      # success message
    meal_deleted = Signal(int)    # meal_id
    recipe_selection_started = Signal(str, str)  # meal_widget_id, slot_key
    recipe_selection_finished = Signal(int)      # recipe_id
    tab_state_changed = Signal(dict)  # tab state information
    meal_plan_updated = Signal(object)  # MealPlanSummaryDTO
    
    def __init__(self, planner_service: PlannerService, recipe_service: RecipeService, session: Session | None = None):
        """
        Initialize the MealPlannerViewModel with injected services.
        
        Args:
            planner_service: Service for meal planning operations
            recipe_service: Service for recipe operations  
            session: Optional SQLAlchemy session for dependency injection
        """
        super().__init__(session)
        
        # Injected services (dependency injection pattern)
        self._planner_service = planner_service
        self._recipe_service = recipe_service
        
        # Tab management state
        self._active_tabs: Dict[str, Dict[str, Any]] = {}  # tab_id -> {meal_id, widget_ref, ...}
        self._tab_counter = 0
        
        # Recipe selection workflow state
        self._selection_context: Optional[Dict[str, str]] = None  # {meal_widget_id, slot_key}
        
        # Cached meal plan summary
        self._meal_plan_summary: Optional[MealPlanSummaryDTO] = None
        
        DebugLogger.log("MealPlannerViewModel initialized with service injection", "debug")
    
    # ── Tab Management ──────────────────────────────────────────────────────────────────────────────────────────
    
    def create_new_tab(self) -> str:
        """
        Create a new meal planning tab.
        
        Returns:
            str: Unique tab identifier
        """
        self._tab_counter += 1
        tab_id = f"meal_tab_{self._tab_counter}"
        
        self._active_tabs[tab_id] = {
            'meal_id': None,
            'is_dirty': False,
            'has_changes': False,
            'created_at': self._tab_counter
        }
        
        self.tab_state_changed.emit(self._get_tab_state_data())
        DebugLogger.log(f"Created new tab: {tab_id}", "debug")
        return tab_id
    
    def close_tab(self, tab_id: str) -> bool:
        """
        Close a meal planning tab.
        
        Args:
            tab_id: Unique tab identifier
            
        Returns:
            bool: True if closed successfully, False otherwise
        """
        if tab_id not in self._active_tabs:
            self._emit_validation_errors([f"Tab {tab_id} not found"])
            return False
        
        try:
            # Check for unsaved changes
            tab_data = self._active_tabs[tab_id]
            if tab_data.get('has_changes', False):
                # Emit signal to allow UI to handle unsaved changes confirmation
                # For now, just log the warning
                DebugLogger.log(f"Closing tab {tab_id} with unsaved changes", "warning")
            
            del self._active_tabs[tab_id]
            self.tab_state_changed.emit(self._get_tab_state_data())
            DebugLogger.log(f"Closed tab: {tab_id}", "debug")
            return True
            
        except Exception as e:
            self._handle_error(e, f"Failed to close tab {tab_id}", "tab_management")
            return False
    
    def set_tab_meal_id(self, tab_id: str, meal_id: Optional[int]) -> bool:
        """
        Associate a meal ID with a tab.
        
        Args:
            tab_id: Unique tab identifier
            meal_id: Meal ID to associate with tab
            
        Returns:
            bool: True if set successfully, False otherwise
        """
        if tab_id not in self._active_tabs:
            self._emit_validation_errors([f"Tab {tab_id} not found"])
            return False
        
        try:
            self._active_tabs[tab_id]['meal_id'] = meal_id
            self._active_tabs[tab_id]['has_changes'] = False  # Reset change tracking
            self.tab_state_changed.emit(self._get_tab_state_data())
            DebugLogger.log(f"Set meal ID {meal_id} for tab {tab_id}", "debug")
            return True
            
        except Exception as e:
            self._handle_error(e, f"Failed to set meal ID for tab {tab_id}", "tab_management")
            return False
    
    def mark_tab_dirty(self, tab_id: str, has_changes: bool = True) -> bool:
        """
        Mark a tab as having unsaved changes.
        
        Args:
            tab_id: Unique tab identifier
            has_changes: Whether the tab has changes
            
        Returns:
            bool: True if marked successfully, False otherwise
        """
        if tab_id not in self._active_tabs:
            return False
        
        try:
            self._active_tabs[tab_id]['has_changes'] = has_changes
            self._active_tabs[tab_id]['is_dirty'] = has_changes
            self.tab_state_changed.emit(self._get_tab_state_data())
            return True
            
        except Exception as e:
            self._handle_error(e, f"Failed to mark tab {tab_id} as dirty", "tab_management")
            return False
    
    def get_tab_info(self, tab_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific tab.
        
        Args:
            tab_id: Unique tab identifier
            
        Returns:
            Optional[Dict]: Tab information or None if not found
        """
        return self._active_tabs.get(tab_id, {}).copy()
    
    def get_all_tab_ids(self) -> List[str]:
        """
        Get all active tab IDs.
        
        Returns:
            List[str]: List of active tab identifiers
        """
        return list(self._active_tabs.keys())
    
    def _get_tab_state_data(self) -> Dict[str, Any]:
        """Get current tab state data for signals."""
        return {
            'total_tabs': len(self._active_tabs),
            'tabs_with_changes': len([t for t in self._active_tabs.values() if t.get('has_changes', False)]),
            'active_meal_ids': [t.get('meal_id') for t in self._active_tabs.values() if t.get('meal_id')],
            'tab_details': self._active_tabs.copy()
        }
    
    # ── Recipe Selection Workflow ───────────────────────────────────────────────────────────────────────────────
    
    def start_recipe_selection(self, meal_widget_id: str, slot_key: str) -> bool:
        """
        Start the recipe selection workflow for a specific meal slot.
        
        Args:
            meal_widget_id: Identifier for the meal widget requesting selection
            slot_key: Slot key (main, side1, side2, side3)
            
        Returns:
            bool: True if selection started successfully, False otherwise
        """
        if not meal_widget_id or not slot_key:
            self._emit_validation_errors(["Meal widget ID and slot key are required"])
            return False
        
        try:
            # Validate slot key
            valid_slots = ['main', 'side1', 'side2', 'side3']
            if slot_key not in valid_slots:
                self._emit_validation_errors([f"Invalid slot key: {slot_key}. Must be one of: {valid_slots}"])
                return False
            
            # Store selection context
            self._selection_context = {
                'meal_widget_id': meal_widget_id,
                'slot_key': slot_key
            }
            
            # Emit signal to UI to show recipe selection
            self.recipe_selection_started.emit(meal_widget_id, slot_key)
            DebugLogger.log(f"Started recipe selection for {meal_widget_id}.{slot_key}", "debug")
            return True
            
        except Exception as e:
            self._handle_error(e, f"Failed to start recipe selection for {meal_widget_id}.{slot_key}", "recipe_selection")
            return False
    
    def finish_recipe_selection(self, recipe_id: int) -> bool:
        """
        Finish the recipe selection workflow with selected recipe.
        
        Args:
            recipe_id: ID of the selected recipe
            
        Returns:
            bool: True if selection finished successfully, False otherwise
        """
        if not self._selection_context:
            self._emit_validation_errors(["No active recipe selection workflow"])
            return False
        
        if recipe_id <= 0:
            self._emit_validation_errors(["Invalid recipe ID"])
            return False
        
        try:
            # Validate recipe exists
            recipe = self._safe_execute(
                self._recipe_service.get_recipe,
                f"Failed to validate recipe {recipe_id}",
                recipe_id
            )
            
            if not recipe:
                self._emit_validation_errors([f"Recipe {recipe_id} not found"])
                return False
            
            # Emit signal with recipe selection
            self.recipe_selection_finished.emit(recipe_id)
            
            # Mark associated tab as dirty
            meal_widget_id = self._selection_context['meal_widget_id']
            # Extract tab_id from meal_widget_id if it follows pattern
            # For now, assume meal_widget_id maps to tab_id somehow
            # This may need adjustment based on actual UI implementation
            
            # Clear selection context
            self._selection_context = None
            
            DebugLogger.log(f"Finished recipe selection with recipe {recipe_id}", "debug")
            return True
            
        except Exception as e:
            self._handle_error(e, f"Failed to finish recipe selection with recipe {recipe_id}", "recipe_selection")
            self._selection_context = None  # Clear context on error
            return False
    
    def cancel_recipe_selection(self) -> bool:
        """
        Cancel the current recipe selection workflow.
        
        Returns:
            bool: True if cancelled successfully, False otherwise
        """
        if not self._selection_context:
            return True  # Nothing to cancel
        
        try:
            self._selection_context = None
            DebugLogger.log("Cancelled recipe selection", "debug")
            return True
            
        except Exception as e:
            self._handle_error(e, "Failed to cancel recipe selection", "recipe_selection")
            return False
    
    def get_selection_context(self) -> Optional[Dict[str, str]]:
        """
        Get current recipe selection context.
        
        Returns:
            Optional[Dict]: Selection context or None if no active selection
        """
        return self._selection_context.copy() if self._selection_context else None
    
    # ── Meal Loading Operations ─────────────────────────────────────────────────────────────────────────────────
    
    def load_meal_by_id(self, meal_id: int) -> Optional[MealSelectionResponseDTO]:
        """
        Load a meal by ID and return the DTO.
        
        Args:
            meal_id: ID of the meal to load
            
        Returns:
            Optional[MealSelectionResponseDTO]: Loaded meal DTO or None if failed
        """
        if meal_id <= 0:
            self._emit_validation_errors(["Invalid meal ID"])
            return None
        
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
                return None
            
            # Emit signal for UI update
            self.meal_loaded.emit(meal_dto)
            self._set_loading_state(False)
            
            DebugLogger.log(f"Successfully loaded meal {meal_id}: {meal_dto.meal_name}", "info")
            return meal_dto
            
        except Exception as e:
            self._set_loading_state(False)
            self._handle_error(e, f"Failed to load meal {meal_id}", "meal_loading")
            return None
    
    def load_saved_meal_ids(self) -> List[int]:
        """
        Load saved meal IDs from the meal plan.
        
        Returns:
            List[int]: List of saved meal IDs
        """
        try:
            self._set_loading_state(True, "Loading saved meal plan")
            
            meal_ids = self._safe_execute(
                self._planner_service.load_saved_meal_ids,
                "Failed to load saved meal IDs"
            )
            
            if meal_ids is None:
                meal_ids = []
            
            self._set_loading_state(False)
            DebugLogger.log(f"Loaded {len(meal_ids)} saved meal IDs", "debug")
            return meal_ids
            
        except Exception as e:
            self._set_loading_state(False)
            self._handle_error(e, "Failed to load saved meal IDs", "meal_loading")
            return []
    
    def get_meal_plan_summary(self) -> Optional[MealPlanSummaryDTO]:
        """
        Get current meal plan summary with caching.
        
        Returns:
            Optional[MealPlanSummaryDTO]: Meal plan summary or None if failed
        """
        try:
            self._set_loading_state(True, "Loading meal plan summary")
            
            summary = self._safe_execute(
                self._planner_service.get_meal_plan_summary,
                "Failed to get meal plan summary"
            )
            
            if summary:
                self._meal_plan_summary = summary
                self.meal_plan_updated.emit(summary)
            
            self._set_loading_state(False)
            return summary
            
        except Exception as e:
            self._set_loading_state(False)
            self._handle_error(e, "Failed to get meal plan summary", "meal_planning")
            return None
    
    # ── Meal Saving Operations ──────────────────────────────────────────────────────────────────────────────────
    
    def save_meal_selection(self, meal_data: Dict[str, Any], meal_id: Optional[int] = None) -> Optional[MealSelectionResponseDTO]:
        """
        Save a meal selection (create or update).
        
        Args:
            meal_data: Dictionary containing meal data fields
            meal_id: Optional meal ID for updates
            
        Returns:
            Optional[MealSelectionResponseDTO]: Saved meal DTO or None if failed
        """
        # Validate meal data
        validation_result = self._validate_meal_data(meal_data)
        if not validation_result.is_valid:
            self._emit_validation_errors(validation_result.errors)
            return None
        
        try:
            self._set_processing_state(True)
            
            if meal_id is None:
                # Create new meal
                return self._create_new_meal(meal_data)
            else:
                # Update existing meal
                return self._update_existing_meal(meal_id, meal_data)
                
        except Exception as e:
            self._set_processing_state(False)
            self._handle_error(e, "Failed to save meal selection", "meal_saving")
            return None
    
    def _create_new_meal(self, meal_data: Dict[str, Any]) -> Optional[MealSelectionResponseDTO]:
        """Create a new meal selection."""
        try:
            # Build create DTO
            create_dto = MealSelectionCreateDTO(
                meal_name=self._sanitize_form_input(meal_data.get('meal_name', 'Custom Meal')),
                main_recipe_id=meal_data['main_recipe_id'],
                side_recipe_1_id=meal_data.get('side_recipe_1_id'),
                side_recipe_2_id=meal_data.get('side_recipe_2_id'),
                side_recipe_3_id=meal_data.get('side_recipe_3_id')
            )
            
            # Create via service
            response_dto = self._safe_execute(
                self._planner_service.create_meal_selection,
                "Failed to create meal selection",
                create_dto
            )
            
            if response_dto:
                self._set_processing_state(False)
                self.meal_saved.emit(f"Created meal: {response_dto.meal_name}")
                DebugLogger.log(f"Created new meal {response_dto.id}: {response_dto.meal_name}", "info")
                return response_dto
            else:
                self._set_processing_state(False)
                self._emit_validation_errors(["Failed to create meal selection"])
                return None
                
        except Exception as e:
            self._set_processing_state(False)
            raise e
    
    def _update_existing_meal(self, meal_id: int, meal_data: Dict[str, Any]) -> Optional[MealSelectionResponseDTO]:
        """Update an existing meal selection."""
        try:
            # Build update DTO
            update_dto = MealSelectionUpdateDTO(
                meal_name=self._sanitize_form_input(meal_data.get('meal_name')),
                main_recipe_id=meal_data.get('main_recipe_id'),
                side_recipe_1_id=meal_data.get('side_recipe_1_id'),
                side_recipe_2_id=meal_data.get('side_recipe_2_id'),
                side_recipe_3_id=meal_data.get('side_recipe_3_id')
            )
            
            # Update via service
            response_dto = self._safe_execute(
                self._planner_service.update_meal_selection,
                f"Failed to update meal {meal_id}",
                meal_id,
                update_dto
            )
            
            if response_dto:
                self._set_processing_state(False)
                self.meal_saved.emit(f"Updated meal: {response_dto.meal_name}")
                DebugLogger.log(f"Updated meal {meal_id}: {response_dto.meal_name}", "info")
                return response_dto
            else:
                self._set_processing_state(False)
                self._emit_validation_errors([f"Failed to update meal {meal_id}"])
                return None
                
        except Exception as e:
            self._set_processing_state(False)
            raise e
    
    def save_meal_plan(self, meal_ids: List[int]) -> bool:
        """
        Save a complete meal plan.
        
        Args:
            meal_ids: List of meal IDs to save as the active plan
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        if not meal_ids:
            self._emit_validation_errors(["Meal IDs are required to save meal plan"])
            return False
        
        try:
            self._set_processing_state(True)
            
            # Save meal plan via service
            save_result = self._safe_execute(
                self._planner_service.saveMealPlan,
                "Failed to save meal plan",
                meal_ids
            )
            
            self._set_processing_state(False)
            
            if save_result and save_result.success:
                self.meal_saved.emit(save_result.message)
                # Refresh meal plan summary
                self.get_meal_plan_summary()
                DebugLogger.log(f"Saved meal plan with {save_result.saved_count} meals", "info")
                return True
            else:
                error_msg = save_result.message if save_result else "Unknown error saving meal plan"
                self._emit_validation_errors([error_msg])
                return False
                
        except Exception as e:
            self._set_processing_state(False)
            self._handle_error(e, "Failed to save meal plan", "meal_plan_saving")
            return False
    
    def delete_meal_selection(self, meal_id: int) -> bool:
        """
        Delete a meal selection.
        
        Args:
            meal_id: ID of the meal to delete
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        if meal_id <= 0:
            self._emit_validation_errors(["Invalid meal ID"])
            return False
        
        try:
            self._set_processing_state(True)
            
            # Delete via service
            success = self._safe_execute(
                self._planner_service.delete_meal_selection,
                f"Failed to delete meal {meal_id}",
                meal_id
            )
            
            self._set_processing_state(False)
            
            if success:
                self.meal_deleted.emit(meal_id)
                DebugLogger.log(f"Deleted meal {meal_id}", "info")
                return True
            else:
                self._emit_validation_errors([f"Failed to delete meal {meal_id}"])
                return False
                
        except Exception as e:
            self._set_processing_state(False)
            self._handle_error(e, f"Failed to delete meal {meal_id}", "meal_deletion")
            return False
    
    # ── Validation ──────────────────────────────────────────────────────────────────────────────────────────────
    
    def _validate_meal_data(self, meal_data: Dict[str, Any]) -> BaseValidationResult:
        """
        Validate meal data for saving operations.
        
        Args:
            meal_data: Dictionary containing meal data fields
            
        Returns:
            BaseValidationResult: Validation result with errors and warnings
        """
        from app.ui.view_models.base_view_model import BaseValidationResult
        
        result = BaseValidationResult()
        
        # Validate required main recipe
        main_recipe_id = meal_data.get('main_recipe_id')
        if not main_recipe_id or main_recipe_id <= 0:
            result.add_error("Main recipe is required")
        
        # Validate meal name
        meal_name = meal_data.get('meal_name', '').strip()
        if not meal_name:
            result.add_error("Meal name is required")
        elif len(meal_name) > 255:
            result.add_error("Meal name cannot exceed 255 characters")
        
        # Validate side recipe IDs (if provided)
        side_keys = ['side_recipe_1_id', 'side_recipe_2_id', 'side_recipe_3_id']
        for key in side_keys:
            side_id = meal_data.get(key)
            if side_id is not None and side_id <= 0:
                result.add_error(f"Invalid {key}: must be positive number")
        
        return result
    
    # ── State Management ────────────────────────────────────────────────────────────────────────────────────────
    
    def clear_meal_plan(self) -> bool:
        """
        Clear the current meal plan.
        
        Returns:
            bool: True if cleared successfully, False otherwise
        """
        try:
            self._set_processing_state(True)
            
            success = self._safe_execute(
                self._planner_service.clear_meal_plan,
                "Failed to clear meal plan"
            )
            
            self._set_processing_state(False)
            
            if success:
                # Reset cached summary
                self._meal_plan_summary = None
                self.meal_plan_updated.emit(MealPlanSummaryDTO(
                    total_meals=0,
                    total_recipes=0,
                    meal_names=[],
                    has_saved_plan=False
                ))
                DebugLogger.log("Cleared meal plan", "info")
                return True
            else:
                self._emit_validation_errors(["Failed to clear meal plan"])
                return False
                
        except Exception as e:
            self._set_processing_state(False)
            self._handle_error(e, "Failed to clear meal plan", "meal_planning")
            return False
    
    def refresh_meal_plan_data(self) -> bool:
        """
        Refresh meal plan data and emit updates.
        
        Returns:
            bool: True if refreshed successfully, False otherwise
        """
        try:
            # Refresh meal plan summary
            summary = self.get_meal_plan_summary()
            if summary:
                return True
            else:
                self._emit_validation_errors(["Failed to refresh meal plan data"])
                return False
                
        except Exception as e:
            self._handle_error(e, "Failed to refresh meal plan data", "meal_planning")
            return False
    
    def reset_view_state(self) -> None:
        """Reset all ViewModel state to initial values."""
        try:
            # Clear tab management
            self._active_tabs.clear()
            self._tab_counter = 0
            
            # Clear selection context
            self._selection_context = None
            
            # Clear cached data
            self._meal_plan_summary = None
            
            # Reset base state
            self.reset_state()
            
            # Emit state updates
            self.tab_state_changed.emit(self._get_tab_state_data())
            
            DebugLogger.log("MealPlannerViewModel state reset", "info")
            
        except Exception as e:
            self._handle_error(e, "Failed to reset view state", "state_management")