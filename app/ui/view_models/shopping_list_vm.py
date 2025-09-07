"""app/ui/view_models/shopping_list_vm.py

ViewModel for Shopping List screen implementing MVVM pattern.
Handles business logic for shopping list generation, manual item management,
and UI state management for shopping list operations.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from PySide6.QtCore import Signal
from sqlalchemy.orm import Session

from _dev_tools import DebugLogger
from app.core.dtos.shopping_dtos import ManualItemCreateDTO
from app.core.services.shopping_service import ShoppingService
from app.ui.utils.form_validation import FormValidator, ValidationResult
from app.ui.view_models.base_view_model import BaseViewModel

# ── Shopping List ViewModel ─────────────────────────────────────────────────────────────────────────────────
class ShoppingListViewModel(BaseViewModel):
    """
    ViewModel for shopping list operations following MVVM pattern.

    Provides:
    - Shopping list generation from recipe IDs
    - Manual item addition with validation
    - Categorized item organization
    - Error handling and user feedback
    - State management for shopping operations
    """

    # Shopping-specific signals
    list_updated = Signal(dict, list)  # grouped_items, manual_items
    manual_item_added = Signal(str)    # success message
    item_status_toggled = Signal(int, bool)  # item_id, new_status
    categories_changed = Signal(dict)  # category counts

    def __init__(self, session: Session | None = None):
        """Initialize the ShoppingListViewModel."""
        super().__init__(session)

        # Initialize service
        self._shopping_service: Optional[ShoppingService] = None

        # Shopping list state
        self._active_recipe_ids: List[int] = []
        self._grouped_items: Dict[str, List] = {}
        self._manual_items: List = []
        self._breakdown_map: Dict[str, List] = {}

        DebugLogger.log("ShoppingListViewModel initialized", "debug")

    # ── Service Management ──────────────────────────────────────────────────────────────────────────────────────

    def _ensure_shopping_service(self) -> bool:
        """Ensure shopping service is available with proper session."""
        if self._shopping_service is not None:
            return True

        try:
            if not self._ensure_session():
                return False

            self._shopping_service = ShoppingService(self._session)
            DebugLogger.log("ShoppingService initialized in ViewModel", "debug")
            return True
        except Exception as e:
            self._handle_error(e, "Failed to initialize shopping service", "service_init")
            return False

    # ── Shopping List Operations ────────────────────────────────────────────────────────────────────────────────

    def generate_shopping_list(self, recipe_ids: List[int]) -> bool:
        """
        Generate shopping list from recipe IDs.

        Args:
            recipe_ids: List of recipe IDs to generate shopping list from

        Returns:
            bool: True if successful, False otherwise
        """
        if not recipe_ids:
            self._emit_validation_errors(["Recipe IDs are required to generate shopping list"])
            return False

        if not self._ensure_shopping_service():
            return False

        try:
            self._set_loading_state(True, "Generating shopping list")

            # Store active recipe IDs
            self._active_recipe_ids = recipe_ids.copy()

            # Generate shopping list via service
            self._shopping_service.generate_shopping_list(recipe_ids)

            # Fetch updated shopping items
            ingredients = self._shopping_service.shopping_repo.get_all_shopping_items()
            DebugLogger.log(f"Fetched {len(ingredients)} shopping items", "debug")

            # Get breakdown mapping for tooltips
            self._breakdown_map = self._shopping_service.shopping_repo.get_ingredient_breakdown(recipe_ids)
            if self._breakdown_map is None:
                self._breakdown_map = {}

            # Organize items by category
            self._organize_items(ingredients)

            # Emit updated data to UI
            self.list_updated.emit(self._grouped_items, self._manual_items)
            self.categories_changed.emit(self._get_category_counts())

            self._set_loading_state(False)
            DebugLogger.log("Shopping list generated successfully", "info")
            return True

        except Exception as e:
            self._set_loading_state(False)
            self._handle_error(e, "Failed to generate shopping list", "generation")
            return False

    def add_manual_item(self, name: str, qty: str, unit: str, category: str) -> bool:
        """
        Add manual item to shopping list with validation.

        Args:
            name: Item name
            qty: Quantity as string
            unit: Measurement unit
            category: Item category

        Returns:
            bool: True if successful, False otherwise
        """
        # Validate inputs
        validation_result = self._validate_manual_item_input(name, qty, unit, category)
        if not validation_result.is_valid:
            self._emit_validation_errors(validation_result.errors)
            return False

        if not self._ensure_shopping_service():
            return False

        try:
            self._set_processing_state(True)

            # Convert quantity to float
            qty_float = float(qty.strip())

            # Create DTO
            dto = ManualItemCreateDTO(
                ingredient_name=name.strip(),
                quantity=qty_float,
                unit=unit,
                category=category
            )

            # Add item via service
            self._shopping_service.add_manual_item(dto)

            # Refresh shopping list to show new item
            if self._active_recipe_ids:
                self.generate_shopping_list(self._active_recipe_ids)

            self._set_processing_state(False)
            self.manual_item_added.emit(f"Added {name} to shopping list")
            DebugLogger.log(f"Manual item added: {name}", "info")
            return True

        except ValueError as e:
            self._set_processing_state(False)
            self._emit_validation_errors(["Please enter a valid quantity (numbers only)"])
            return False
        except Exception as e:
            self._set_processing_state(False)
            self._handle_error(e, "Failed to add manual item", "manual_item")
            return False

    def toggle_item_status(self, item_id: int) -> bool:
        """
        Toggle shopping item checked status.

        Args:
            item_id: ID of the shopping item to toggle

        Returns:
            bool: True if successful, False otherwise
        """
        if not self._ensure_shopping_service():
            return False

        try:
            # Toggle via service
            self._shopping_service.toggle_item_status(item_id)

            # Emit signal for UI update
            # Note: We don't know the new status here, let UI handle visual update
            self.item_status_toggled.emit(item_id, True)  # UI will determine actual status

            DebugLogger.log(f"Item {item_id} status toggled", "debug")
            return True

        except Exception as e:
            self._handle_error(e, f"Failed to toggle item {item_id} status", "item_toggle")
            return False

    # ── Data Access and Organization ────────────────────────────────────────────────────────────────────────────

    def get_categorized_items(self) -> Tuple[Dict[str, List], List]:
        """
        Get current categorized items.

        Returns:
            Tuple of (grouped_items, manual_items)
        """
        return self._grouped_items.copy(), self._manual_items.copy()

    def get_breakdown_map(self) -> Dict[str, List]:
        """Get current ingredient breakdown mapping."""
        return self._breakdown_map.copy()

    def get_active_recipe_ids(self) -> List[int]:
        """Get currently active recipe IDs."""
        return self._active_recipe_ids.copy()

    def _organize_items(self, ingredients: List) -> None:
        """
        Organize shopping items by category.

        Args:
            ingredients: List of shopping items from repository
        """
        grouped = defaultdict(list)
        manual_items = []

        for item in ingredients:
            if item.source == "manual":
                manual_items.append(item)
            else:
                category = item.category or "Other"
                grouped[category].append(item)

        self._grouped_items = dict(grouped)
        self._manual_items = manual_items

        DebugLogger.log(f"Organized items: {len(grouped)} categories, {len(manual_items)} manual items", "debug")

    def _get_category_counts(self) -> Dict[str, int]:
        """Get count of items per category."""
        counts = {}

        for category, items in self._grouped_items.items():
            counts[category] = len(items)

        if self._manual_items:
            counts["Manual Entries"] = len(self._manual_items)

        return counts

    # ── Validation ──────────────────────────────────────────────────────────────────────────────────────────────

    def _validate_manual_item_input(self, name: str, qty: str, unit: str, category: str) -> ValidationResult:
        """
        Validate manual item input data using comprehensive form validation.

        Args:
            name: Item name
            qty: Quantity string
            unit: Unit string
            category: Category string

        Returns:
            ValidationResult: Comprehensive validation result with errors and warnings
        """
        return FormValidator.validate_shopping_item_form(name, qty, unit, category)

    # ── State Management ────────────────────────────────────────────────────────────────────────────────────────

    def refresh_current_list(self) -> bool:
        """Refresh the current shopping list using active recipe IDs."""
        if not self._active_recipe_ids:
            self._emit_validation_errors(["No active recipes to refresh from"])
            return False

        return self.generate_shopping_list(self._active_recipe_ids)

    def clear_shopping_list(self) -> bool:
        """Clear all items from the current shopping list."""
        if not self._ensure_shopping_service():
            return False

        try:
            self._set_processing_state(True)

            # Clear via service (implementation depends on service capabilities)
            # For now, just clear local state
            self._grouped_items.clear()
            self._manual_items.clear()
            self._breakdown_map.clear()
            self._active_recipe_ids.clear()

            # Emit cleared state
            self.list_updated.emit({}, [])
            self.categories_changed.emit({})

            self._set_processing_state(False)
            DebugLogger.log("Shopping list cleared", "info")
            return True

        except Exception as e:
            self._set_processing_state(False)
            self._handle_error(e, "Failed to clear shopping list", "clear")
            return False

    def reset_view_state(self) -> None:
        """Reset all ViewModel state to initial values."""
        self.clear_shopping_list()
        self.reset_state()
        DebugLogger.log("ShoppingListViewModel state reset", "info")
