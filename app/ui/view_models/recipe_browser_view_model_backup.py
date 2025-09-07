"""app/ui/view_models/recipe_browser_view_model.py

RecipeBrowserViewModel - Business logic layer for recipe browsing following MVVM pattern.

This ViewModel provides all business logic for recipe browsing operations while maintaining
strict separation from UI concerns. Handles data operations through RecipeService,
manages filtering and sorting state, and coordinates recipe selection workflows.

## Architecture Role

The RecipeBrowserViewModel serves as the intermediary between the RecipeBrowserView (UI layer)
and the RecipeService (data layer), ensuring proper MVVM architecture compliance:

- **UI Layer**: RecipeBrowserView handles presentation and user interactions
- **ViewModel Layer (this class)**: Business logic, state management, data coordination  
- **Service Layer**: RecipeService performs data access through repositories
- **Model Layer**: Recipe entities and DTOs for data transfer

## Key Responsibilities

### Data Operations
- Recipe loading with filtering and sorting
- Search functionality with term-based filtering
- Real-time filter updates and data refresh
- Efficient state management for UI updates

### Business Logic
- Filter validation and normalization
- Sort option parsing and mapping
- Selection mode state management
- Recipe favorite status toggling

### State Coordination
- Current recipe collection management
- Filter state tracking and persistence
- Loading and error state management
- Selection mode coordination

## Usage Patterns

### Basic Initialization
```python
# Standard ViewModel initialization
view_model = RecipeBrowserViewModel()

# Connect to UI signals
view_model.recipes_loaded.connect(ui.update_recipe_display)
view_model.filter_state_changed.connect(ui.update_filter_ui)
```

### Filter Management
```python
# Update individual filters
view_model.update_category_filter("Breakfast") 
view_model.update_favorites_filter(True)
view_model.update_sort_option("Newest")

# Perform searches
view_model.search_recipes("chicken soup")
view_model.clear_search()
```

### Selection Mode Operations
```python
# Enable selection mode for meal planning
view_model.set_selection_mode(True)

# Handle recipe selections
view_model.handle_recipe_selection(recipe)
```

## Signal Architecture

### Data Signals
- `recipes_loaded(List[Recipe])`: New recipe data available for UI display
- `recipes_cleared()`: Recipe display should be cleared
- `search_completed(int)`: Search completed with result count

### State Signals  
- `filter_state_changed(RecipeFilterDTO)`: Current filter state changed
- `selection_mode_changed(bool)`: Selection mode enabled/disabled
- `recipe_selected(int, Recipe)`: Recipe selected in selection mode

### Status Signals
- `error_occurred(Dict)`: Error occurred during operations
- `loading_changed(bool)`: Loading state changed (if supported)

## Filter Operations

### Category Filtering
```python
# Set specific category filter
view_model.update_category_filter("Desserts")

# Clear category filter (show all)
view_model.update_category_filter(None)
view_model.update_category_filter("All")  # Equivalent
```

### Search Operations
```python
# Search with current filters applied
view_model.search_recipes("chicken", apply_current_filters=True)

# Search without additional filters
view_model.search_recipes("pasta", apply_current_filters=False) 

# Clear search and restore filtered view
view_model.clear_search()
```

### Sort Management
```python
# Available sort options (from config.SORT_OPTIONS)
sort_options = view_model.get_available_sort_options()
# ["A-Z", "Z-A", "Newest", "Oldest", "Shortest Time", etc.]

# Apply sort option
view_model.update_sort_option("Newest")  # Maps to created_at DESC
view_model.update_sort_option("A-Z")     # Maps to recipe_name ASC
```

## Selection Mode Integration

### Meal Planning Workflow
```python
class MealPlannerIntegration:
    def setup_recipe_selection(self):
        # Configure ViewModel for selection
        self.browser_vm = RecipeBrowserViewModel()
        self.browser_vm.set_selection_mode(True)
        
        # Handle recipe selections
        self.browser_vm.recipe_selected.connect(self.add_to_meal_plan)
        
    def add_to_meal_plan(self, recipe_id: int, recipe: Recipe):
        # Process selected recipe for meal planning
        self.meal_service.add_recipe_to_plan(recipe_id, self.target_meal)
```

## Error Handling Patterns

The ViewModel provides comprehensive error handling:

```python
def handle_view_model_errors(self):
    view_model.error_occurred.connect(lambda error: 
        self.show_error_message(error.get('message', 'Unknown error'))
    )
```

Common error scenarios:
- Service initialization failures
- Database connection issues  
- Invalid filter parameters
- Recipe not found for operations

## Performance Considerations

### Efficient Data Loading
- Lazy service initialization
- Batched UI updates through signals
- Minimal data transfer via DTOs
- Optimized filter application

### Memory Management
- Proper session management
- Service cleanup in destructor
- Efficient recipe list management
- Filter state optimization

## MVVM Compliance Guidelines

### ViewModel Responsibilities (this class)
- ✅ Business logic coordination
- ✅ Data service management
- ✅ Filter and search operations
- ✅ State management and validation
- ✅ Error handling and reporting

### View Integration
- ✅ Signal-based communication only
- ✅ DTO usage for data transfer
- ✅ No direct UI manipulation
- ✅ Pure business logic focus

### Forbidden Patterns
- ❌ Direct UI widget manipulation
- ❌ Import of UI components
- ❌ Presentation logic (colors, fonts, layouts)
- ❌ Direct user interaction handling

## Testing Support

The ViewModel is designed for comprehensive unit testing:

```python
def test_recipe_filtering():
    vm = RecipeBrowserViewModel()
    
    # Test filter application
    vm.update_category_filter("Breakfast")
    vm.update_favorites_filter(True)
    
    # Verify filter state
    assert vm.current_filter.recipe_category == "Breakfast"
    assert vm.current_filter.favorites_only == True

def test_selection_mode():
    vm = RecipeBrowserViewModel()
    vm.set_selection_mode(True)
    
    # Verify selection mode state
    assert vm.selection_mode == True
```

See Also:
- `RecipeBrowserView`: UI presentation layer
- `RecipeService`: Data access service  
- `RecipeFilterDTO`: Filter data transfer object
- BaseViewModel: Parent class with common ViewModel functionality
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import Dict, List, Optional

from PySide6.QtCore import Signal
from sqlalchemy.orm import Session

from _dev_tools import DebugLogger
from app.config import RECIPE_CATEGORIES, SORT_OPTIONS
from app.core.dtos.recipe_dtos import RecipeFilterDTO
from app.core.models.recipe import Recipe
from app.core.services.recipe_service import RecipeService
from app.ui.view_models.base_view_model import BaseViewModel

# ── Recipe Browser ViewModel ────────────────────────────────────────────────────────────────────────────────
class RecipeBrowserViewModel(BaseViewModel):
    """
    ViewModel for recipe browsing operations following strict MVVM architecture.
    
    Handles all business logic for recipe browsing while maintaining separation from UI concerns.
    Coordinates between RecipeBrowserView (presentation) and RecipeService (data access).
    
    Key Features:
    - Advanced filtering: category, favorites, search terms
    - Multiple sorting options with database mapping
    - Selection mode state management for meal planning
    - Real-time search with filter combination
    - Recipe favorite status toggling
    - Comprehensive error handling and state management
    
    Usage Examples:
        # Basic initialization and data loading
        vm = RecipeBrowserViewModel()
        vm.recipes_loaded.connect(ui_update_handler)
        vm.load_recipes()  # Load with default filters
        
        # Filter management
        vm.update_category_filter("Breakfast")
        vm.update_favorites_filter(True) 
        vm.update_sort_option("Newest")
        
        # Search operations
        vm.search_recipes("chicken soup")
        vm.clear_search()
        
        # Selection mode for meal planning
        vm.set_selection_mode(True)
        vm.recipe_selected.connect(meal_plan_handler)
    
    Signals:
        recipes_loaded(List[Recipe]): New recipe data for UI display
        recipe_selected(int, Recipe): Recipe selected in selection mode
        filter_state_changed(RecipeFilterDTO): Filter state updated
        selection_mode_changed(bool): Selection mode toggled
        search_completed(int): Search finished with result count
        recipes_cleared(): Recipe display should be cleared
        error_occurred(Dict): Error during operations
        
    Architecture:
        - Inherits from BaseViewModel for common ViewModel functionality
        - Uses RecipeService for all data operations via repositories  
        - Communicates with UI via signals only (no direct UI access)
        - Transfers data using DTOs to maintain layer separation
        
    MVVM Compliance:
        ✅ Business logic only (no UI concerns)
        ✅ Service coordination and data management
        ✅ Signal-based UI communication
        ✅ DTO usage for data transfer
        ❌ No direct UI manipulation or imports
    """
    
    # Recipe browser specific signals
    recipes_loaded = Signal(list)           # List[Recipe] - recipes to display
    recipe_selected = Signal(int, object)   # recipe_id, recipe_object
    filter_state_changed = Signal(object)   # RecipeFilterDTO - current filter state
    selection_mode_changed = Signal(bool)   # selection_mode_enabled
    recipes_cleared = Signal()              # when recipe display should be cleared
    search_completed = Signal(int)          # result_count
    
    def __init__(self, session: Session | None = None):
        """Initialize the RecipeBrowserViewModel."""
        super().__init__(session)
        
        # Initialize service
        self._recipe_service: Optional[RecipeService] = None
        
        # Browser state
        self._current_recipes: List[Recipe] = []
        self._current_filter: RecipeFilterDTO = RecipeFilterDTO()
        self._selection_mode: bool = False
        self._recipes_loaded: bool = False
        
        # Filter/sort state
        self._category_filter: Optional[str] = None
        self._sort_option: str = "A-Z"
        self._favorites_only: bool = False
        self._search_term: Optional[str] = None
        
        DebugLogger.log("RecipeBrowserViewModel initialized", "debug")
    
    # ── Service Management ──────────────────────────────────────────────────────────────────────────────────────
    
    def _ensure_recipe_service(self) -> bool:
        """Ensure recipe service is available with proper session."""
        if self._recipe_service is not None:
            return True
        
        try:
            if not self._ensure_session():
                return False
            
            self._recipe_service = RecipeService(self._session)
            DebugLogger.log("RecipeService initialized in RecipeBrowserViewModel", "debug")
            return True
        except Exception as e:
            self._handle_error(e, "Failed to initialize recipe service", "service_init")
            return False
    
    # ── Properties ──────────────────────────────────────────────────────────────────────────────────────────────
    
    @property
    def selection_mode(self) -> bool:
        """Get current selection mode state."""
        return self._selection_mode
    
    @property
    def recipes_loaded_state(self) -> bool:
        """Get whether recipes have been loaded."""
        return self._recipes_loaded
    
    @property
    def current_recipes(self) -> List[Recipe]:
        """Get current recipe list (read-only copy)."""
        return self._current_recipes.copy()
    
    @property
    def current_filter(self) -> RecipeFilterDTO:
        """Get current filter state."""
        return self._current_filter
    
    @property
    def recipe_count(self) -> int:
        """Get count of currently loaded recipes."""
        return len(self._current_recipes)
    
    # ── Core Recipe Loading ─────────────────────────────────────────────────────────────────────────────────────
    
    def load_recipes(self) -> bool:
        """
        Load recipes with default filter settings.
        
        Returns:
            bool: True if successful, False otherwise
        """
        default_filter = RecipeFilterDTO(
            recipe_category=None,
            sort_by="recipe_name",
            sort_order="asc",
            favorites_only=False
        )
        
        return self._fetch_and_emit_recipes(default_filter)
    
    def load_filtered_sorted_recipes(self, filter_dto: RecipeFilterDTO) -> bool:
        """
        Load recipes based on provided filter criteria.
        
        Args:
            filter_dto: RecipeFilterDTO containing filter and sort criteria
            
        Returns:
            bool: True if successful, False otherwise
        """
        if filter_dto is None:
            DebugLogger.log("Filter DTO cannot be None", "warning")
            return False
        
        return self._fetch_and_emit_recipes(filter_dto)
    
    def refresh_recipes(self) -> bool:
        """
        Refresh the current recipe display with existing filter settings.
        
        Returns:
            bool: True if successful, False otherwise
        """
        self._recipes_loaded = False
        return self._fetch_and_emit_recipes(self._current_filter)
    
    def clear_recipes(self) -> None:
        """Clear all loaded recipes and emit signal."""
        self._current_recipes.clear()
        self._recipes_loaded = False
        self.recipes_cleared.emit()
        DebugLogger.log("Recipes cleared from ViewModel", "debug")
    
    # ── Filter Management ───────────────────────────────────────────────────────────────────────────────────────
    
    def update_category_filter(self, category: str) -> bool:
        """
        Update category filter and reload recipes.
        
        Args:
            category: Category name to filter by, or None/"All"/"Filter" for no filter
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Normalize category filter
        if category in ("All", "Filter", "") or not category:
            category = None
        
        self._category_filter = category
        return self._update_filter_and_reload()
    
    def update_sort_option(self, sort_option: str) -> bool:
        """
        Update sort option and reload recipes.
        
        Args:
            sort_option: Sort option from SORT_OPTIONS
            
        Returns:
            bool: True if successful, False otherwise
        """
        if sort_option not in SORT_OPTIONS:
            DebugLogger.log(f"Invalid sort option: {sort_option}", "warning")
            return False
        
        self._sort_option = sort_option
        return self._update_filter_and_reload()
    
    def update_favorites_filter(self, favorites_only: bool) -> bool:
        """
        Update favorites filter and reload recipes.
        
        Args:
            favorites_only: Whether to show only favorite recipes
            
        Returns:
            bool: True if successful, False otherwise
        """
        self._favorites_only = favorites_only
        return self._update_filter_and_reload()
    
    def update_search_term(self, search_term: Optional[str]) -> bool:
        """
        Update search term and reload recipes.
        
        Args:
            search_term: Search term to filter by, None or empty for no search
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Normalize search term
        if not search_term or not search_term.strip():
            search_term = None
        else:
            search_term = search_term.strip()
        
        self._search_term = search_term
        return self._update_filter_and_reload()
    
    def _update_filter_and_reload(self) -> bool:
        """Update filter DTO from current state and reload recipes."""
        try:
            # Map sort option to database field and order
            sort_field, sort_order = self._parse_sort_option(self._sort_option)
            
            # Build filter DTO
            filter_dto = RecipeFilterDTO(
                recipe_category=self._category_filter,
                sort_by=sort_field,
                sort_order=sort_order,
                favorites_only=self._favorites_only,
                search_term=self._search_term
            )
            
            return self._fetch_and_emit_recipes(filter_dto)
            
        except Exception as e:
            self._handle_error(e, "Failed to update filter and reload recipes")
            return False
    
    def _parse_sort_option(self, sort_option: str) -> tuple[str, str]:
        """
        Parse UI sort option to database field and order.
        
        Args:
            sort_option: Sort option from UI
            
        Returns:
            tuple[str, str]: (sort_field, sort_order)
        """
        sort_map = {
            "A-Z": ("recipe_name", "asc"),
            "Z-A": ("recipe_name", "desc"),
            "Newest": ("created_at", "desc"),
            "Oldest": ("created_at", "asc"),
            "Shortest Time": ("total_time", "asc"),
            "Longest Time": ("total_time", "desc"),
            "Most Servings": ("servings", "desc"),
            "Fewest Servings": ("servings", "asc"),
        }
        
        return sort_map.get(sort_option, ("recipe_name", "asc"))
    
    # ── Selection Mode Management ───────────────────────────────────────────────────────────────────────────────
    
    def set_selection_mode(self, enabled: bool) -> None:
        """
        Set selection mode state and emit signal.
        
        Args:
            enabled: Whether selection mode should be enabled
        """
        if self._selection_mode != enabled:
            self._selection_mode = enabled
            self.selection_mode_changed.emit(enabled)
            DebugLogger.log(f"Selection mode {'enabled' if enabled else 'disabled'}", "debug")
    
    def handle_recipe_selection(self, recipe: Recipe) -> None:
        """
        Handle recipe selection in selection mode.
        
        Args:
            recipe: Recipe object that was selected
        """
        if not self._selection_mode:
            DebugLogger.log("Recipe selection attempted when not in selection mode", "warning")
            return
        
        if recipe is None:
            DebugLogger.log("Cannot select None recipe", "warning")
            return
        
        self.recipe_selected.emit(recipe.id, recipe)
        DebugLogger.log(f"Recipe selected: {recipe.recipe_name} (ID: {recipe.id})", "debug")
    
    # ── Core Data Operations ────────────────────────────────────────────────────────────────────────────────────
    
    def _fetch_and_emit_recipes(self, filter_dto: RecipeFilterDTO) -> bool:
        """
        Fetch recipes using filter and emit results.
        
        Args:
            filter_dto: Filter criteria for recipes
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self._ensure_recipe_service():
            return False
        
        try:
            self._set_loading_state(True, "Loading recipes")
            self._clear_validation_errors()
            
            # Store current filter
            self._current_filter = filter_dto
            
            # Fetch recipes via service
            recipes = self._recipe_service.list_filtered(filter_dto)
            
            # Update state
            self._current_recipes = recipes
            self._recipes_loaded = True
            
            # Emit signals
            self.recipes_loaded.emit(recipes)
            self.filter_state_changed.emit(filter_dto)
            self.search_completed.emit(len(recipes))
            
            DebugLogger.log(f"Loaded {len(recipes)} recipes with filter: {filter_dto.model_dump()}", "debug")
            return True
            
        except Exception as e:
            self._handle_error(e, "Failed to fetch and display recipes", "data_fetch")
            self._current_recipes = []
            self._recipes_loaded = False
            self.recipes_loaded.emit([])
            return False
        finally:
            self._set_loading_state(False)
    
    # ── Search Operations ───────────────────────────────────────────────────────────────────────────────────────
    
    def search_recipes(self, search_term: str, apply_current_filters: bool = True) -> bool:
        """
        Search recipes by term with optional filter application.
        
        Args:
            search_term: Search term to look for in recipe names/content
            apply_current_filters: Whether to apply current category/sort filters
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not search_term or not search_term.strip():
            # Empty search - show all recipes with current filters
            self._search_term = None
            return self._update_filter_and_reload() if apply_current_filters else self.load_recipes()
        
        self._search_term = search_term.strip()
        
        if apply_current_filters:
            return self._update_filter_and_reload()
        else:
            # Search without other filters
            search_filter = RecipeFilterDTO(
                search_term=self._search_term,
                sort_by="recipe_name",
                sort_order="asc"
            )
            return self._fetch_and_emit_recipes(search_filter)
    
    def clear_search(self) -> bool:
        """
        Clear search term and reload with current filters.
        
        Returns:
            bool: True if successful, False otherwise
        """
        self._search_term = None
        return self._update_filter_and_reload()
    
    # ── Recipe Actions ──────────────────────────────────────────────────────────────────────────────────────────
    
    def toggle_recipe_favorite(self, recipe_id: int) -> bool:
        """
        Toggle favorite status of a recipe and refresh display.
        
        Args:
            recipe_id: ID of recipe to toggle favorite status
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self._ensure_recipe_service():
            return False
        
        try:
            self._set_processing_state(True)
            
            # Toggle favorite via service
            updated_recipe = self._recipe_service.toggle_favorite(recipe_id)
            
            if updated_recipe is None:
                self._handle_error(
                    ValueError(f"Recipe with ID {recipe_id} not found"),
                    "Failed to toggle favorite status",
                    "recipe_not_found"
                )
                return False
            
            # Update recipe in current list if it exists
            for i, recipe in enumerate(self._current_recipes):
                if recipe.id == recipe_id:
                    self._current_recipes[i] = updated_recipe
                    break
            
            # Re-emit current recipes to update UI
            self.recipes_loaded.emit(self._current_recipes)
            
            DebugLogger.log(
                f"Toggled favorite status for recipe {recipe_id} to {updated_recipe.is_favorite}",
                "debug"
            )
            return True
            
        except Exception as e:
            self._handle_error(e, f"Failed to toggle favorite for recipe {recipe_id}")
            return False
        finally:
            self._set_processing_state(False)
    
    def get_recipe_by_id(self, recipe_id: int) -> Optional[Recipe]:
        """
        Get recipe by ID from current loaded recipes.
        
        Args:
            recipe_id: ID of recipe to find
            
        Returns:
            Optional[Recipe]: Recipe if found, None otherwise
        """
        for recipe in self._current_recipes:
            if recipe.id == recipe_id:
                return recipe
        return None
    
    # ── State Reset ─────────────────────────────────────────────────────────────────────────────────────────────
    
    def reset_browser_state(self) -> None:
        """Reset browser to initial state."""
        self._current_recipes.clear()
        self._recipes_loaded = False
        self._category_filter = None
        self._sort_option = "A-Z"
        self._favorites_only = False
        self._search_term = None
        self._selection_mode = False
        
        # Reset filter to default
        self._current_filter = RecipeFilterDTO()
        
        # Reset base state
        self.reset_state()
        
        # Emit state change signals
        self.recipes_cleared.emit()
        self.selection_mode_changed.emit(False)
        
        DebugLogger.log("RecipeBrowserViewModel state reset", "debug")
    
    # ── Utility Methods ─────────────────────────────────────────────────────────────────────────────────────────
    
    def get_available_categories(self) -> List[str]:
        """Get available recipe categories from configuration."""
        return RECIPE_CATEGORIES.copy()
    
    def get_available_sort_options(self) -> List[str]:
        """Get available sort options from configuration."""
        return SORT_OPTIONS.copy()
    
    def validate_filter_dto(self, filter_dto: RecipeFilterDTO) -> bool:
        """
        Validate RecipeFilterDTO for correctness.
        
        Args:
            filter_dto: Filter DTO to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Pydantic will validate during model creation
            RecipeFilterDTO.model_validate(filter_dto.model_dump())
            return True
        except Exception as e:
            DebugLogger.log(f"Filter DTO validation failed: {e}", "error")
            return False