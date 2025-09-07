"""app/ui/views/recipe_browser/filter_coordinator.py

Specialized coordinator for handling recipe-specific filtering logic and state management
in the RecipeBrowser view. This class extracts filtering concerns from the view layer
and provides a dedicated interface for recipe domain filtering operations.

The FilterCoordinator implements recipe domain intelligence including:
- Recipe category filtering with RECIPE_CATEGORIES integration
- Advanced sort option mapping and validation
- Favorites-only filtering with state persistence
- Search functionality with recipe-specific search patterns
- Combined filter operations with dependency management
- Filter state persistence and restoration
- Filter preset management for common use cases
- Recipe domain validation and constraint handling

Classes:
    FilterState: Immutable filter state representation
    FilterPreset: Predefined filter configurations
    FilterCoordinator: Main coordinator for recipe filtering logic

Example:
    # Basic usage
    coordinator = FilterCoordinator(view_model, config)
    coordinator.setup_filter_controls({
        'category': category_combo,
        'sort': sort_combo,
        'favorites': favorites_checkbox
    })

    # Apply recipe-specific filters
    coordinator.apply_category_filter("Chicken")
    coordinator.apply_favorites_filter(True)
    coordinator.apply_search_filter("spicy")

    # Use filter presets
    coordinator.apply_filter_preset("quick_healthy_meals")
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
import weakref

from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtWidgets import QWidget

from _dev_tools import DebugLogger
from app.config import RECIPE_CATEGORIES, SORT_OPTIONS
from app.core.dtos.recipe_dtos import RecipeFilterDTO
from app.ui.components.widgets.checkbox import CheckBox
from app.ui.components.widgets.combobox import ComboBox
from app.ui.view_models.recipe_browser_view_model import RecipeBrowserViewModel
from .config import RecipeBrowserConfig

# ── Filter Domain Models ─────────────────────────────────────────────────────────────────────────────────────────
class FilterChangeType(Enum):
    """Types of filter changes for tracking and optimization."""
    CATEGORY = "category"
    SORT = "sort"
    FAVORITES = "favorites"
    SEARCH = "search"
    COMBINED = "combined"
    PRESET = "preset"
    RESET = "reset"


@dataclass(frozen=True)
class FilterState:
    """Immutable filter state representation with recipe domain validation."""
    category: Optional[str] = None
    sort_option: str = "A-Z"
    favorites_only: bool = False
    search_term: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate filter state using recipe domain rules."""
        # Validate category against RECIPE_CATEGORIES
        if self.category is not None and self.category not in RECIPE_CATEGORIES:
            if self.category not in ("All", "Filter", ""):  # Allow UI placeholders
                raise ValueError(f"Invalid recipe category: {self.category}. Valid categories: {RECIPE_CATEGORIES}")

        # Validate sort option against SORT_OPTIONS
        if self.sort_option not in SORT_OPTIONS:
            raise ValueError(f"Invalid sort option: {self.sort_option}. Valid options: {SORT_OPTIONS}")

        # Validate search term format
        if self.search_term is not None:
            if not isinstance(self.search_term, str):
                raise ValueError("Search term must be a string")
            if len(self.search_term.strip()) == 0:
                object.__setattr__(self, 'search_term', None)  # Normalize empty search

    def to_filter_dto(self) -> RecipeFilterDTO:
        """Convert to RecipeFilterDTO for service layer interaction."""
        # Parse sort option using recipe domain knowledge
        sort_field, sort_order = self._parse_sort_option(self.sort_option)

        # Normalize category for DTO
        category = None if self.category in ("All", "Filter", "") else self.category

        # Normalize search term
        search_term = self.search_term.strip().lower() if self.search_term else None

        return RecipeFilterDTO(
            recipe_category=category,
            sort_by=sort_field,
            sort_order=sort_order,
            favorites_only=self.favorites_only,
            search_term=search_term
        )

    def _parse_sort_option(self, sort_option: str) -> tuple[str, str]:
        """Parse sort option using recipe domain knowledge."""
        sort_map = {
            "A-Z": ("recipe_name", "asc"),
            "Z-A": ("recipe_name", "desc"),
            "Newest": ("created_at", "desc"),
            "Oldest": ("created_at", "asc"),
            "Recently Updated": ("updated_at", "desc"),
            "Shortest Time": ("total_time", "asc"),
            "Longest Time": ("total_time", "desc"),
            "Most Servings": ("servings", "desc"),
            "Fewest Servings": ("servings", "asc"),
            "Favorites First": ("is_favorite", "desc"),
        }
        return sort_map.get(sort_option, ("recipe_name", "asc"))

    def has_active_filters(self) -> bool:
        """Check if any non-default filters are active."""
        return (
            self.category is not None and self.category not in ("All", "Filter", "") or
            self.sort_option != "A-Z" or
            self.favorites_only or
            self.search_term is not None
        )

    def get_filter_summary(self) -> str:
        """Get human-readable summary of active filters."""
        parts = []

        if self.category and self.category not in ("All", "Filter", ""):
            parts.append(f"Category: {self.category}")

        if self.sort_option != "A-Z":
            parts.append(f"Sort: {self.sort_option}")

        if self.favorites_only:
            parts.append("Favorites Only")

        if self.search_term:
            parts.append(f"Search: '{self.search_term}'")

        return ", ".join(parts) if parts else "No filters active"


@dataclass
class FilterPreset:
    """Predefined filter configuration for common recipe browsing scenarios."""
    name: str
    display_name: str
    description: str
    filter_state: FilterState
    category: str = "general"  # general, dietary, meal_planning, etc.

    @classmethod
    def create_default_presets(cls) -> Dict[str, 'FilterPreset']:
        """Create default filter presets for common recipe scenarios."""
        return {
            "all_recipes": cls(
                name="all_recipes",
                display_name="All Recipes",
                description="Show all recipes with default sorting",
                filter_state=FilterState(),
                category="general"
            ),
            "favorites_only": cls(
                name="favorites_only",
                display_name="Favorite Recipes",
                description="Show only favorited recipes",
                filter_state=FilterState(favorites_only=True),
                category="general"
            ),
            "quick_meals": cls(
                name="quick_meals",
                display_name="Quick Meals",
                description="Recipes sorted by shortest cooking time",
                filter_state=FilterState(sort_option="Shortest Time"),
                category="meal_planning"
            ),
            "newest_recipes": cls(
                name="newest_recipes",
                display_name="Latest Additions",
                description="Recently added recipes",
                filter_state=FilterState(sort_option="Newest"),
                category="general"
            ),
            "chicken_favorites": cls(
                name="chicken_favorites",
                display_name="Favorite Chicken Recipes",
                description="Favorite chicken recipes",
                filter_state=FilterState(category="Chicken", favorites_only=True),
                category="dietary"
            ),
            "veggie_quick": cls(
                name="veggie_quick",
                display_name="Quick Veggie Meals",
                description="Vegetarian recipes sorted by cooking time",
                filter_state=FilterState(category="Veggie", sort_option="Shortest Time"),
                category="dietary"
            )
        }


# ── Main FilterCoordinator Class ─────────────────────────────────────────────────────────────────────────────────
class FilterCoordinator(QObject):
    """
    Specialized coordinator for recipe-specific filtering logic in RecipeBrowser.

    This coordinator implements recipe domain expertise including:
    - RECIPE_CATEGORIES integration and validation
    - Recipe-specific sort option mapping
    - Favorites filtering with state management
    - Search functionality with recipe domain patterns
    - Filter combination and dependency management
    - Filter state persistence and history
    - Recipe domain constraint validation
    - Performance optimization for filtering operations

    The FilterCoordinator maintains MVVM compliance by coordinating with the ViewModel
    for actual data operations while managing the UI filter state and validation.

    Signals:
        filter_changed: Emitted when any filter changes (RecipeFilterDTO)
        filter_state_changed: Emitted when filter state changes (FilterState)
        filter_validation_error: Emitted when filter validation fails (str error_message)
        filter_preset_applied: Emitted when a preset is applied (str preset_name)
        filter_history_changed: Emitted when filter history updates (int history_count)
    """

    # Core filter signals
    filter_changed = Signal(RecipeFilterDTO)
    filter_state_changed = Signal(FilterState)

    # Validation and error signals
    filter_validation_error = Signal(str)
    filter_constraint_violation = Signal(str, str)  # constraint_type, details

    # Advanced filtering signals
    filter_preset_applied = Signal(str)  # preset_name
    filter_history_changed = Signal(int)  # history_count
    combined_filter_optimized = Signal(int, float)  # result_count, optimization_time_ms

    # Performance monitoring
    filter_performance_changed = Signal(dict)  # performance metrics

    def __init__(self, view_model: RecipeBrowserViewModel, config: RecipeBrowserConfig):
        """
        Initialize FilterCoordinator with ViewModel and configuration.

        Args:
            view_model: RecipeBrowserViewModel for data operations
            config: RecipeBrowserConfig for behavior configuration
        """
        super().__init__()

        # Core dependencies (use weak references to prevent circular references)
        self._view_model_ref = weakref.ref(view_model)
        self._config = config

        # Filter state management
        self._current_state = FilterState()
        self._previous_state: Optional[FilterState] = None
        self._filter_history: List[FilterState] = [self._current_state]
        self._max_history_size = 20

        # UI control references
        self._controls: Dict[str, QWidget] = {}
        self._control_handlers: Dict[str, Callable] = {}

        # Filter presets
        self._presets = FilterPreset.create_default_presets()

        # Debouncing and performance
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._execute_debounced_filter_update)
        self._pending_updates: Set[FilterChangeType] = set()

        # Performance tracking
        self._filter_start_time: Optional[float] = None
        self._filter_count = 0
        self._optimization_count = 0

        # Recipe domain validation cache
        self._validation_cache: Dict[str, bool] = {}

        DebugLogger.log("FilterCoordinator initialized with recipe domain expertise", "debug")

    @property
    def view_model(self) -> Optional[RecipeBrowserViewModel]:
        """Get the ViewModel instance (may be None if garbage collected)."""
        return self._view_model_ref()

    @property
    def current_state(self) -> FilterState:
        """Get the current filter state."""
        return self._current_state

    @property
    def has_active_filters(self) -> bool:
        """Check if any non-default filters are currently active."""
        return self._current_state.has_active_filters()

    @property
    def filter_summary(self) -> str:
        """Get human-readable summary of current filters."""
        return self._current_state.get_filter_summary()

    # ── UI Control Setup and Management ──────────────────────────────────────────────────────────────────────────
    def setup_filter_controls(self, controls: Dict[str, QWidget]) -> bool:
        """
        Setup UI filter controls with recipe domain validation.

        Args:
            controls: Dictionary mapping control names to widgets
                     Expected keys: 'category', 'sort', 'favorites', optionally 'search'

        Returns:
            bool: True if setup successful, False otherwise
        """
        try:
            self._controls = controls.copy()

            # Setup category filter control
            if 'category' in controls:
                category_control = controls['category']
                if isinstance(category_control, ComboBox):
                    self._setup_category_control(category_control)
                else:
                    DebugLogger.log(f"Category control must be QComboBox, got {type(category_control)}", "warning")

            # Setup sort control
            if 'sort' in controls:
                sort_control = controls['sort']
                if isinstance(sort_control, ComboBox):
                    self._setup_sort_control(sort_control)
                else:
                    DebugLogger.log(f"Sort control must be QComboBox, got {type(sort_control)}", "warning")

            # Setup favorites control
            if 'favorites' in controls:
                favorites_control = controls['favorites']
                if isinstance(favorites_control, CheckBox):
                    self._setup_favorites_control(favorites_control)
                else:
                    DebugLogger.log(f"Favorites control must be QCheckBox, got {type(favorites_control)}", "warning")

            # Setup search control (optional)
            if 'search' in controls:
                search_control = controls['search']
                self._setup_search_control(search_control)

            # Apply initial state to controls
            self._sync_controls_to_state(self._current_state)

            DebugLogger.log(f"FilterCoordinator controls setup with {len(controls)} controls", "debug")
            return True

        except Exception as e:
            DebugLogger.log(f"Error setting up filter controls: {e}", "error")
            self.filter_validation_error.emit(f"Failed to setup filter controls: {str(e)}")
            return False

    def _setup_category_control(self, control: ComboBox):
        """Setup category filter control with recipe domain validation."""
        # Validate that control has recipe categories
        control_items = [control.itemText(i) for i in range(control.count())]

        # Verify all items are valid recipe categories or placeholders
        for item in control_items:
            if item not in RECIPE_CATEGORIES and item not in ("All", "Filter", ""):
                DebugLogger.log(f"Category control contains invalid category: {item}", "warning")

        # Connect signal with debouncing
        control.currentTextChanged.connect(
            lambda text: self._schedule_filter_update(FilterChangeType.CATEGORY, text)
        )

        self._control_handlers['category'] = control.currentTextChanged

    def _setup_sort_control(self, control: ComboBox):
        """Setup sort control with recipe domain validation."""
        # Validate that control has recipe sort options
        control_items = [control.itemText(i) for i in range(control.count())]

        # Verify all items are valid sort options
        for item in control_items:
            if item not in SORT_OPTIONS and item not in ("Sort", ""):
                DebugLogger.log(f"Sort control contains invalid option: {item}", "warning")

        # Connect signal with debouncing
        control.currentTextChanged.connect(
            lambda text: self._schedule_filter_update(FilterChangeType.SORT, text)
        )

        self._control_handlers['sort'] = control.currentTextChanged

    def _setup_favorites_control(self, control: CheckBox):
        """Setup favorites control with state tracking."""
        # Connect signal with debouncing
        control.stateChanged.connect(
            lambda state: self._schedule_filter_update(FilterChangeType.FAVORITES, state == 2)
        )

        self._control_handlers['favorites'] = control.stateChanged

    def _setup_search_control(self, control: QWidget):
        """Setup search control with recipe-specific search patterns."""
        # Handle different search control types
        if hasattr(control, 'textChanged'):
            # QLineEdit or similar
            control.textChanged.connect(
                lambda text: self._schedule_filter_update(FilterChangeType.SEARCH, text)
            )
            self._control_handlers['search'] = control.textChanged
        else:
            DebugLogger.log(f"Search control type {type(control)} not fully supported", "warning")

    # ── Individual Filter Application Methods ─────────────────────────────────────────────────────────────────────
    def apply_category_filter(self, category: str) -> bool:
        """
        Apply recipe category filter with domain validation.

        Args:
            category: Recipe category from RECIPE_CATEGORIES or "All"/"Filter" for no filter

        Returns:
            bool: True if successfully applied, False otherwise
        """
        try:
            # Normalize category
            normalized_category = self._normalize_category(category)

            # Validate against recipe domain
            if not self._validate_category(normalized_category):
                self.filter_validation_error.emit(f"Invalid recipe category: {category}")
                return False

            # Create new state
            new_state = FilterState(
                category=normalized_category,
                sort_option=self._current_state.sort_option,
                favorites_only=self._current_state.favorites_only,
                search_term=self._current_state.search_term
            )

            return self._apply_new_filter_state(new_state, FilterChangeType.CATEGORY)

        except Exception as e:
            DebugLogger.log(f"Error applying category filter: {e}", "error")
            self.filter_validation_error.emit(f"Failed to apply category filter: {str(e)}")
            return False

    def apply_sort_option(self, sort_option: str) -> bool:
        """
        Apply sort option with recipe domain validation.

        Args:
            sort_option: Sort option from SORT_OPTIONS

        Returns:
            bool: True if successfully applied, False otherwise
        """
        try:
            # Validate sort option
            if not self._validate_sort_option(sort_option):
                self.filter_validation_error.emit(f"Invalid sort option: {sort_option}")
                return False

            # Create new state
            new_state = FilterState(
                category=self._current_state.category,
                sort_option=sort_option,
                favorites_only=self._current_state.favorites_only,
                search_term=self._current_state.search_term
            )

            return self._apply_new_filter_state(new_state, FilterChangeType.SORT)

        except Exception as e:
            DebugLogger.log(f"Error applying sort option: {e}", "error")
            self.filter_validation_error.emit(f"Failed to apply sort option: {str(e)}")
            return False

    def apply_favorites_filter(self, enabled: bool) -> bool:
        """
        Apply favorites-only filter with state management.

        Args:
            enabled: Whether to show only favorite recipes

        Returns:
            bool: True if successfully applied, False otherwise
        """
        try:
            # Create new state
            new_state = FilterState(
                category=self._current_state.category,
                sort_option=self._current_state.sort_option,
                favorites_only=enabled,
                search_term=self._current_state.search_term
            )

            return self._apply_new_filter_state(new_state, FilterChangeType.FAVORITES)

        except Exception as e:
            DebugLogger.log(f"Error applying favorites filter: {e}", "error")
            self.filter_validation_error.emit(f"Failed to apply favorites filter: {str(e)}")
            return False

    def apply_search_filter(self, search_term: str) -> bool:
        """
        Apply search filter with recipe-specific search optimization.

        Args:
            search_term: Search term to filter recipes (empty string clears search)

        Returns:
            bool: True if successfully applied, False otherwise
        """
        try:
            # Normalize search term using recipe domain knowledge
            normalized_term = self._normalize_search_term(search_term)

            # Create new state
            new_state = FilterState(
                category=self._current_state.category,
                sort_option=self._current_state.sort_option,
                favorites_only=self._current_state.favorites_only,
                search_term=normalized_term
            )

            return self._apply_new_filter_state(new_state, FilterChangeType.SEARCH)

        except Exception as e:
            DebugLogger.log(f"Error applying search filter: {e}", "error")
            self.filter_validation_error.emit(f"Failed to apply search filter: {str(e)}")
            return False

    # ── Combined Filter Operations ───────────────────────────────────────────────────────────────────────────────
    def apply_combined_filters(self, **filters) -> bool:
        """
        Apply multiple filters atomically with optimization.

        Args:
            **filters: Keyword arguments for filters (category, sort_option, favorites_only, search_term)

        Returns:
            bool: True if successfully applied, False otherwise
        """
        try:
            start_time = self._get_current_time_ms()

            # Extract filter values with current state defaults
            category = filters.get('category', self._current_state.category)
            sort_option = filters.get('sort_option', self._current_state.sort_option)
            favorites_only = filters.get('favorites_only', self._current_state.favorites_only)
            search_term = filters.get('search_term', self._current_state.search_term)

            # Normalize values
            category = self._normalize_category(category)
            search_term = self._normalize_search_term(search_term)

            # Validate all filters
            validation_errors = []
            if not self._validate_category(category):
                validation_errors.append(f"Invalid category: {category}")
            if not self._validate_sort_option(sort_option):
                validation_errors.append(f"Invalid sort option: {sort_option}")

            if validation_errors:
                error_msg = "; ".join(validation_errors)
                self.filter_validation_error.emit(error_msg)
                return False

            # Create optimized combined state
            new_state = FilterState(
                category=category,
                sort_option=sort_option,
                favorites_only=favorites_only,
                search_term=search_term
            )

            success = self._apply_new_filter_state(new_state, FilterChangeType.COMBINED)

            if success:
                optimization_time = self._get_current_time_ms() - start_time
                self.combined_filter_optimized.emit(
                    self.view_model.recipe_count if self.view_model else 0,
                    optimization_time
                )
                self._optimization_count += 1

            return success

        except Exception as e:
            DebugLogger.log(f"Error applying combined filters: {e}", "error")
            self.filter_validation_error.emit(f"Failed to apply combined filters: {str(e)}")
            return False

    # ── Filter Preset Management ─────────────────────────────────────────────────────────────────────────────────
    def apply_filter_preset(self, preset_name: str) -> bool:
        """
        Apply a predefined filter preset.

        Args:
            preset_name: Name of the preset to apply

        Returns:
            bool: True if successfully applied, False otherwise
        """
        try:
            if preset_name not in self._presets:
                available_presets = list(self._presets.keys())
                self.filter_validation_error.emit(
                    f"Unknown preset '{preset_name}'. Available: {available_presets}"
                )
                return False

            preset = self._presets[preset_name]
            success = self._apply_new_filter_state(preset.filter_state, FilterChangeType.PRESET)

            if success:
                self.filter_preset_applied.emit(preset_name)
                DebugLogger.log(f"Applied filter preset: {preset.display_name}", "debug")

            return success

        except Exception as e:
            DebugLogger.log(f"Error applying filter preset: {e}", "error")
            self.filter_validation_error.emit(f"Failed to apply preset '{preset_name}': {str(e)}")
            return False

    def get_available_presets(self) -> Dict[str, str]:
        """
        Get available filter presets with display names.

        Returns:
            Dict[str, str]: Mapping of preset names to display names
        """
        return {name: preset.display_name for name, preset in self._presets.items()}

    def add_custom_preset(self, name: str, display_name: str, description: str,
                         category: str = "custom") -> bool:
        """
        Add a custom filter preset based on current state.

        Args:
            name: Unique preset name
            display_name: Human-readable name
            description: Preset description
            category: Preset category

        Returns:
            bool: True if successfully added, False otherwise
        """
        try:
            if name in self._presets:
                DebugLogger.log(f"Preset '{name}' already exists, overwriting", "warning")

            preset = FilterPreset(
                name=name,
                display_name=display_name,
                description=description,
                filter_state=self._current_state,
                category=category
            )

            self._presets[name] = preset
            DebugLogger.log(f"Added custom preset: {display_name}", "debug")
            return True

        except Exception as e:
            DebugLogger.log(f"Error adding custom preset: {e}", "error")
            return False

    # ── Filter State Management ──────────────────────────────────────────────────────────────────────────────────
    def get_filter_state(self) -> RecipeFilterDTO:
        """
        Get current filter state as RecipeFilterDTO for ViewModel interaction.

        Returns:
            RecipeFilterDTO: Current filter state ready for ViewModel
        """
        return self._current_state.to_filter_dto()

    def restore_previous_state(self) -> bool:
        """
        Restore the previous filter state (undo last change).

        Returns:
            bool: True if successfully restored, False if no previous state
        """
        if self._previous_state is None:
            DebugLogger.log("No previous filter state to restore", "debug")
            return False

        try:
            restored_state = self._previous_state
            self._previous_state = None  # Clear to prevent double restore

            success = self._apply_new_filter_state(restored_state, FilterChangeType.RESET)
            if success:
                DebugLogger.log("Previous filter state restored", "debug")

            return success

        except Exception as e:
            DebugLogger.log(f"Error restoring previous state: {e}", "error")
            return False

    def reset_to_defaults(self) -> bool:
        """
        Reset all filters to default values.

        Returns:
            bool: True if successfully reset, False otherwise
        """
        try:
            default_state = FilterState()
            success = self._apply_new_filter_state(default_state, FilterChangeType.RESET)

            if success:
                DebugLogger.log("Filters reset to defaults", "debug")

            return success

        except Exception as e:
            DebugLogger.log(f"Error resetting filters: {e}", "error")
            self.filter_validation_error.emit(f"Failed to reset filters: {str(e)}")
            return False

    def get_filter_history(self) -> List[FilterState]:
        """
        Get filter history for undo/redo functionality.

        Returns:
            List[FilterState]: Recent filter states (most recent first)
        """
        return self._filter_history.copy()

    def clear_filter_history(self):
        """Clear filter history."""
        self._filter_history = [self._current_state]
        self.filter_history_changed.emit(1)
        DebugLogger.log("Filter history cleared", "debug")

    # ── Internal State Management Methods ────────────────────────────────────────────────────────────────────────
    def _apply_new_filter_state(self, new_state: FilterState, change_type: FilterChangeType) -> bool:
        """
        Apply a new filter state with full coordination.

        Args:
            new_state: New FilterState to apply
            change_type: Type of change being applied

        Returns:
            bool: True if successfully applied, False otherwise
        """

        print(f"DEBUG: Applying filter state - current: {self._current_state}, new: {new_state}")
        print(f"DEBUG: States equal? {self._current_state == new_state}")

        # Store previous state for undo
        if self._current_state != new_state:
            print("DEBUG: States differ, proceeding with update")
            self._previous_state = self._current_state
        else:
            print("DEBUG: States are equal, should still proceed...")
            # Continue anyway - this might be the issue

        try:
            # Store previous state for undo
            if self._current_state != new_state:
                self._previous_state = self._current_state

            # Update current state
            self._current_state = new_state

            # Add to history
            self._add_to_history(new_state)

            # Sync UI controls to new state
            self._sync_controls_to_state(new_state)

            # Convert to DTO and delegate to ViewModel
            filter_dto = new_state.to_filter_dto()
            print(f"DEBUG: Created DTO - category: {filter_dto.recipe_category}, sort_by: {filter_dto.sort_by}")

            if self.view_model:
                # Use ViewModel's optimized filtering
                success = self.view_model.load_filtered_sorted_recipes(filter_dto)
                print(f"DEBUG: ViewModel.load_filtered_sorted_recipes returned: {success}")

                if success:
                    # Emit coordination signals
                    self.filter_changed.emit(filter_dto)
                    self.filter_state_changed.emit(new_state)

                    self._filter_count += 1

                    DebugLogger.log(
                        f"Filter applied ({change_type.value}): {new_state.get_filter_summary()}",
                        "debug"
                    )
                    return True
                else:
                    DebugLogger.log("ViewModel failed to apply filter", "error")
                    return False
            else:
                DebugLogger.log("ViewModel reference is None, cannot apply filter", "error")
                self.filter_validation_error.emit("Internal error: ViewModel not available")
                return False

        except Exception as e:
            DebugLogger.log(f"Error applying new filter state: {e}", "error")
            self.filter_validation_error.emit(f"Failed to apply filter: {str(e)}")
            return False

    def _add_to_history(self, state: FilterState):
        """Add filter state to history with size management."""
        # Remove duplicate if at end of history
        if self._filter_history and self._filter_history[-1] == state:
            return

        # Add new state
        self._filter_history.append(state)

        # Trim history if too large
        if len(self._filter_history) > self._max_history_size:
            self._filter_history = self._filter_history[-self._max_history_size:]

        self.filter_history_changed.emit(len(self._filter_history))

    def _sync_controls_to_state(self, state: FilterState):
        """Synchronize UI controls with filter state."""
        try:
            # Block signals to prevent recursion
            for control in self._controls.values():
                control.blockSignals(True)

            # Update category control
            if 'category' in self._controls:
                control = self._controls['category']
                display_category = state.category if state.category else "All"
                if isinstance(control, ComboBox):
                    index = control.findText(display_category)
                    if index >= 0:
                        control.setCurrentIndex(index)

            # Update sort control
            if 'sort' in self._controls:
                control = self._controls['sort']
                if isinstance(control, ComboBox):
                    index = control.findText(state.sort_option)
                    if index >= 0:
                        control.setCurrentIndex(index)

            # Update favorites control
            if 'favorites' in self._controls:
                control = self._controls['favorites']
                if isinstance(control, CheckBox):
                    control.setChecked(state.favorites_only)

            # Update search control
            if 'search' in self._controls:
                control = self._controls['search']
                if hasattr(control, 'setText'):
                    control.setText(state.search_term or "")

        finally:
            # Restore signal connections
            for control in self._controls.values():
                control.blockSignals(False)

    # ── Debouncing and Performance Optimization ──────────────────────────────────────────────────────────────────
    def _schedule_filter_update(self, change_type: FilterChangeType, value: Any):
        """Schedule a debounced filter update to prevent excessive operations."""
        try:
            # Store the pending change
            self._pending_updates.add(change_type)

            # Update appropriate state value
            if change_type == FilterChangeType.CATEGORY:
                self._pending_category = value
            elif change_type == FilterChangeType.SORT:
                self._pending_sort = value
            elif change_type == FilterChangeType.FAVORITES:
                self._pending_favorites = value
            elif change_type == FilterChangeType.SEARCH:
                self._pending_search = value

            # Reset debounce timer
            debounce_delay = self._config.interaction.filter_debounce_delay_ms
            self._debounce_timer.stop()
            self._debounce_timer.start(debounce_delay)

        except Exception as e:
            DebugLogger.log(f"Error scheduling filter update: {e}", "error")

    def _execute_debounced_filter_update(self):
        """Execute the debounced filter update with all pending changes."""
        try:
            if not self._pending_updates:
                return

            # Build new filter state with pending changes
            category = getattr(self, '_pending_category', self._current_state.category)
            sort_option = getattr(self, '_pending_sort', self._current_state.sort_option)
            favorites_only = getattr(self, '_pending_favorites', self._current_state.favorites_only)
            search_term = getattr(self, '_pending_search', self._current_state.search_term)

            # Determine change type for logging
            if len(self._pending_updates) > 1:
                change_type = FilterChangeType.COMBINED
            else:
                change_type = next(iter(self._pending_updates))

            # Apply combined changes
            success = self.apply_combined_filters(
                category=category,
                sort_option=sort_option,
                favorites_only=favorites_only,
                search_term=search_term
            )

            # Clear pending updates
            self._pending_updates.clear()

            # Clean up pending values
            for attr in ('_pending_category', '_pending_sort', '_pending_favorites', '_pending_search'):
                if hasattr(self, attr):
                    delattr(self, attr)

            if not success:
                DebugLogger.log("Debounced filter update failed", "warning")

        except Exception as e:
            DebugLogger.log(f"Error executing debounced filter update: {e}", "error")

    # ── Recipe Domain Validation Methods ──────────────────────────────────────────────────────────────────────────
    def _normalize_category(self, category: Optional[str]) -> Optional[str]:
        """Normalize category value using recipe domain knowledge."""
        if not category or category in ("All", "Filter", ""):
            return None
        return category.strip()

    def _normalize_search_term(self, search_term: Optional[str]) -> Optional[str]:
        """Normalize search term for recipe searching."""
        if not search_term or not search_term.strip():
            return None

        # Recipe-specific search normalization
        normalized = search_term.strip().lower()

        # Remove common recipe search stop words if desired
        # (could be enhanced with recipe-specific stop words)

        return normalized if normalized else None

    def _validate_category(self, category: Optional[str]) -> bool:
        """Validate recipe category against domain knowledge."""
        if category is None:
            return True

        # Use cache for performance
        cache_key = f"cat_{category}"
        if cache_key in self._validation_cache:
            return self._validation_cache[cache_key]

        is_valid = category in RECIPE_CATEGORIES
        self._validation_cache[cache_key] = is_valid

        return is_valid

    def _validate_sort_option(self, sort_option: str) -> bool:
        """Validate sort option against recipe domain knowledge."""
        cache_key = f"sort_{sort_option}"
        if cache_key in self._validation_cache:
            return self._validation_cache[cache_key]

        is_valid = sort_option in SORT_OPTIONS
        self._validation_cache[cache_key] = is_valid

        return is_valid

    # ── Performance Monitoring and Metrics ───────────────────────────────────────────────────────────────────────
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics for the filter coordinator."""
        return {
            'filter_count': self._filter_count,
            'optimization_count': self._optimization_count,
            'validation_cache_size': len(self._validation_cache),
            'history_size': len(self._filter_history),
            'preset_count': len(self._presets),
            'active_filters': self.has_active_filters,
            'current_filter_summary': self.filter_summary,
            'debounce_enabled': self._config.interaction.filter_debounce_delay_ms > 0,
            'debounce_delay_ms': self._config.interaction.filter_debounce_delay_ms,
        }

    def reset_performance_counters(self):
        """Reset performance monitoring counters."""
        self._filter_count = 0
        self._optimization_count = 0
        self._validation_cache.clear()
        DebugLogger.log("FilterCoordinator performance counters reset", "debug")

    def _get_current_time_ms(self) -> float:
        """Get current time in milliseconds for performance tracking."""
        from time import perf_counter
        return perf_counter() * 1000

    # ── Cleanup and Memory Management ────────────────────────────────────────────────────────────────────────────
    def cleanup(self):
        """Clean up resources and stop timers."""
        try:
            # Stop debounce timer
            if self._debounce_timer.isActive():
                self._debounce_timer.stop()

            # Clear references
            self._controls.clear()
            self._control_handlers.clear()
            self._validation_cache.clear()
            self._filter_history.clear()

            DebugLogger.log("FilterCoordinator cleanup completed", "debug")

        except Exception as e:
            DebugLogger.log(f"Error during FilterCoordinator cleanup: {e}", "error")

    def __del__(self):
        """Enhanced cleanup on destruction."""
        try:
            self.cleanup()
        except:
            pass  # Avoid exceptions during destruction
