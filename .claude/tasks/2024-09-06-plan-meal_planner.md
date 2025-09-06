# Refactoring Plan: meal_planner.py

## Overview
- **File**: `C:\Users\mjmil\Documents\recipe_app\app\ui\views\meal_planner.py`
- **Review Date**: 2024-09-06
- **Total Tasks**: 13 tasks across 4 phases
- **Estimated Effort**: High (4-6 weeks)
- **Architecture Pattern**: MVVM with proper layer separation

## Executive Summary

The meal_planner.py file contains critical architectural violations that break the MVVM pattern and clean architecture principles. This refactoring plan addresses 13+ issues ranging from critical to minor, with a focus on:

1. **Eliminating MVVM violations** - Remove direct Core model usage in UI
2. **Implementing proper ViewModels** - Create MealPlannerViewModel and MealWidgetViewModel  
3. **Establishing DTO patterns** - Replace model instances with proper DTOs
4. **Extracting business logic** - Move all business logic from UI to ViewModels
5. **Creating reusable utilities** - TabManager and StateManager for common patterns

The refactoring will be executed in 4 phases, prioritizing critical architectural violations first.

---

## Phase 1: Critical Architecture Fixes (Priority: CRITICAL)

### Task 1: Create Core DTO Extensions
**Priority**: Critical | **Agent**: Core Data Specialist | **Effort**: Medium (3-4 days)

**Files Affected**: 
- `app/core/dtos/planner_dtos.py` (extend existing)
- `app/core/dtos/ui_planner_dtos.py` (new file)

**Description**: 
Create UI-specific DTOs to replace direct MealSelection model usage in the UI layer. Current violations on lines 127-130 and 219-226 show UI directly instantiating Core models.

**New DTOs Required**:
```python
# UI-specific DTOs for meal planner
class MealDataDTO(BaseModel):
    meal_name: str = "Custom Meal"
    main_recipe: Optional[RecipeDisplayDTO] = None
    side_recipes: List[RecipeDisplayDTO] = Field(default_factory=list)
    slot_assignments: Dict[str, Optional[int]] = Field(default_factory=dict)

class MealSlotUpdateDTO(BaseModel):
    slot_key: str  # "main", "side1", "side2", "side3"
    recipe_id: Optional[int] = None
    action: str  # "add", "remove", "replace"

class MealWidgetStateDTO(BaseModel):
    meal_id: Optional[int] = None
    is_modified: bool = False
    validation_errors: List[str] = Field(default_factory=list)
    last_saved: Optional[datetime] = None
```

**Implementation Steps**:
1. Create `app/core/dtos/ui_planner_dtos.py` with UI-specific DTOs
2. Add conversion methods between Core DTOs and UI DTOs
3. Implement validation rules specific to UI interactions
4. Create factory methods for common DTO creation patterns
5. Add comprehensive unit tests for all new DTOs

**Success Criteria**:
- UI layer never directly instantiates Core models
- All meal data passed between layers uses DTOs
- DTO validation catches invalid data before database operations

---

### Task 2: Create MealWidgetViewModel
**Priority**: Critical | **Agent**: PySide6 UI Specialist | **Effort**: Large (5-7 days)

**Files Affected**:
- `app/ui/view_models/meal_widget_view_model.py` (new file)
- `app/ui/views/meal_planner.py` (refactor MealWidget class)

**Description**:
Extract all business logic from MealWidget class into a dedicated ViewModel. Current violations include business logic in save_meal() (lines 177-192), load_meal() (lines 194-243), and complex state management throughout the widget.

**ViewModel Interface**:
```python
class MealWidgetViewModel(BaseViewModel):
    # Signals for UI updates
    recipe_loaded = Signal(str, dict)  # slot_key, recipe_data
    meal_saved = Signal(bool, str)  # success, message
    validation_error = Signal(str, str)  # field_name, error_message
    state_changed = Signal(dict)  # current_state
    
    def __init__(self, planner_service: PlannerService, recipe_service: RecipeService):
        super().__init__()
        self.planner_service = planner_service
        self.recipe_service = recipe_service
        self.meal_data = MealDataDTO()
        self._is_modified = False
    
    def load_meal(self, meal_id: int) -> bool:
        """Load meal data into ViewModel"""
        
    def update_recipe_slot(self, slot_key: str, recipe_id: int) -> bool:
        """Update a recipe slot assignment"""
        
    def save_meal(self) -> MealSaveResultDTO:
        """Save current meal state"""
        
    def validate_meal_data(self) -> ValidationResultDTO:
        """Validate current meal configuration"""
```

**Implementation Steps**:
1. Create `MealWidgetViewModel` extending `BaseViewModel`
2. Move all save logic from UI to `save_meal()` method
3. Move all load logic from UI to `load_meal()` method  
4. Implement slot update logic in `update_recipe_slot()`
5. Add comprehensive validation in `validate_meal_data()`
6. Create state management methods for tracking modifications
7. Implement error handling with proper signal emissions
8. Add detailed logging for all operations
9. Write comprehensive unit tests for all methods

**Success Criteria**:
- MealWidget class contains no business logic
- All meal operations go through ViewModel methods
- Error handling is centralized in ViewModel
- State tracking is managed by ViewModel

---

### Task 3: Create MealPlannerViewModel
**Priority**: Critical | **Agent**: PySide6 UI Specialist | **Effort**: Large (5-7 days)

**Files Affected**:
- `app/ui/view_models/meal_planner_view_model.py` (new file) 
- `app/ui/views/meal_planner.py` (refactor MealPlanner class)

**Description**:
Create main ViewModel for coordinating the overall meal planning interface. Current violations include direct service instantiation (lines 61, 262) and complex state management throughout the main class.

**ViewModel Interface**:
```python
class MealPlannerViewModel(BaseViewModel):
    # Signals for coordinating UI updates
    tab_added = Signal(int, str)  # tab_index, meal_name
    tab_removed = Signal(int)  # tab_index
    navigation_requested = Signal(str, dict)  # view_name, context
    meal_plan_saved = Signal(bool, str)  # success, message
    
    def __init__(self, planner_service: PlannerService, recipe_service: RecipeService):
        super().__init__()
        self.planner_service = planner_service
        self.recipe_service = recipe_service
        self.tab_manager = TabManagerState()
        self.active_meals: Dict[int, MealWidgetViewModel] = {}
    
    def create_new_meal_tab(self) -> int:
        """Create a new meal planning tab"""
        
    def save_meal_plan(self) -> MealPlanSaveResultDTO:
        """Save complete meal plan"""
        
    def load_saved_meal_plan(self) -> bool:
        """Load previously saved meal plan"""
        
    def get_meal_viewmodel(self, tab_index: int) -> Optional[MealWidgetViewModel]:
        """Get ViewModel for specific meal tab"""
```

**Implementation Steps**:
1. Create `MealPlannerViewModel` extending `BaseViewModel`
2. Implement dependency injection for services (no direct instantiation)
3. Create tab coordination logic in `create_new_meal_tab()`
4. Implement meal plan save/load operations
5. Add meal plan validation and error handling
6. Create meal ViewModel factory methods
7. Implement navigation coordination methods
8. Add comprehensive state management
9. Write unit tests for all coordination logic

**Success Criteria**:
- No direct service instantiation in UI classes
- All meal plan operations coordinated through ViewModel
- Tab management logic centralized
- Proper dependency injection implemented

---

### Task 4: Refactor MealWidget to Use ViewModel
**Priority**: Critical | **Agent**: PySide6 UI Specialist | **Effort**: Large (4-5 days)

**Files Affected**:
- `app/ui/views/meal_planner.py` (MealWidget class major refactor)

**Description**:
Refactor the MealWidget class to become a pure UI component that delegates all business logic to MealWidgetViewModel. Remove all direct service usage and model instantiation.

**Refactoring Changes**:
```python
class MealWidget(QWidget):
    def __init__(self, view_model: MealWidgetViewModel, parent=None):
        super().__init__(parent)
        self.view_model = view_model
        # Remove: self.recipe_service = RecipeService()
        # Remove: Direct MealSelection instantiation
        
        self._setup_ui()
        self._connect_viewmodel_signals()
    
    def _connect_viewmodel_signals(self):
        """Connect ViewModel signals to UI updates"""
        self.view_model.recipe_loaded.connect(self._on_recipe_loaded)
        self.view_model.meal_saved.connect(self._on_meal_saved)
        self.view_model.validation_error.connect(self._on_validation_error)
        
    def save_meal(self):
        """Delegate to ViewModel - no business logic"""
        self.view_model.save_meal()
        
    def load_meal(self, meal_id: int):
        """Delegate to ViewModel - no business logic"""
        self.view_model.load_meal(meal_id)
```

**Implementation Steps**:
1. Remove all direct service instantiation from `__init__`
2. Add ViewModel dependency injection to constructor
3. Remove all business logic from `save_meal()` method
4. Remove all business logic from `load_meal()` method
5. Replace model instantiation with ViewModel method calls
6. Convert slot update methods to ViewModel delegates
7. Remove DTO creation logic - move to ViewModel
8. Add signal connections for ViewModel updates
9. Update all methods to delegate to ViewModel
10. Add error handling for ViewModel communication
11. Write integration tests for UI-ViewModel interaction

**Success Criteria**:
- MealWidget contains zero business logic
- All operations delegate to MealWidgetViewModel
- No direct service or model usage in UI
- Signal communication properly established

---

## Phase 2: Architecture Improvements (Priority: MAJOR)

### Task 5: Create TabManager Utility
**Priority**: Major | **Agent**: Core Utility Specialist | **Effort**: Medium (3-4 days)

**Files Affected**:
- `app/ui/utils/tab_manager.py` (new file)
- `app/ui/views/meal_planner.py` (refactor tab management)

**Description**:
Extract repeated tab management logic (lines 337-350, 446-487, 370-374) into a reusable TabManager utility class.

**TabManager Interface**:
```python
class TabManager:
    def __init__(self, tab_widget: QTabWidget):
        self.tab_widget = tab_widget
        self.tab_registry: Dict[int, TabMetadata] = {}
        self.next_tab_id = 1
        
    def add_tab(self, widget: QWidget, title: str, closeable: bool = True) -> int:
        """Add tab with metadata tracking"""
        
    def remove_tab(self, tab_index: int) -> bool:
        """Remove tab and cleanup metadata"""
        
    def get_tab_metadata(self, tab_index: int) -> Optional[TabMetadata]:
        """Get metadata for specific tab"""
        
    def update_tab_title(self, tab_index: int, title: str) -> bool:
        """Update tab title with validation"""

@dataclass
class TabMetadata:
    tab_id: int
    title: str
    widget: QWidget
    is_closeable: bool
    created_at: datetime
    last_modified: datetime
```

**Implementation Steps**:
1. Create `TabManager` class with proper interface
2. Implement tab addition with metadata tracking
3. Implement safe tab removal with cleanup
4. Add tab validation and error handling
5. Create helper methods for tab queries
6. Add comprehensive logging for tab operations
7. Write unit tests for all tab operations
8. Create integration tests with QTabWidget

**Success Criteria**:
- All tab operations go through TabManager
- Consistent tab metadata tracking
- Proper cleanup on tab removal
- Reusable across other components

---

### Task 6: Create StateManager for Complex State
**Priority**: Major | **Agent**: PySide6 UI Specialist | **Effort**: Large (4-5 days)

**Files Affected**:
- `app/ui/utils/state_manager.py` (new file)
- `app/ui/view_models/meal_planner_view_model.py` (integrate StateManager)

**Description**:
Extract complex state management logic (lines 267-268, 375-413, 446-487) into a dedicated StateManager to handle tab mappings, selection context, and view state.

**StateManager Interface**:
```python
class MealPlannerStateManager:
    def __init__(self):
        self.tab_map: Dict[int, MealWidgetViewModel] = {}
        self.selection_context: Optional[SelectionContext] = None
        self.current_view: ViewType = ViewType.PLANNER
        self.modification_tracking: Dict[int, bool] = {}
        
    def register_meal_tab(self, tab_index: int, viewmodel: MealWidgetViewModel):
        """Register meal tab with state tracking"""
        
    def update_selection_context(self, context: SelectionContext):
        """Update current selection context"""
        
    def mark_tab_modified(self, tab_index: int, is_modified: bool):
        """Track modification state for tabs"""
        
    def get_modified_tabs(self) -> List[int]:
        """Get list of modified tab indices"""
```

**Implementation Steps**:
1. Create `MealPlannerStateManager` class
2. Implement tab registration and tracking
3. Add selection context management
4. Create modification state tracking
5. Implement state validation methods
6. Add state persistence capabilities
7. Create state change event system
8. Add comprehensive logging
9. Write unit tests for state operations
10. Create integration tests with ViewModels

**Success Criteria**:
- Complex state logic centralized
- Consistent state tracking across tabs
- Proper state validation and error handling
- Integration with existing ViewModels

---

### Task 7: Standardize Error Handling Patterns
**Priority**: Major | **Agent**: Core Error Specialist | **Effort**: Medium (3-4 days)

**Files Affected**:
- `app/ui/view_models/meal_planner_view_model.py` (standardize patterns)
- `app/ui/view_models/meal_widget_view_model.py` (standardize patterns)
- `app/ui/views/meal_planner.py` (remove inconsistent patterns)

**Description**:
Current inconsistent error handling (lines 177, 193, 329-335, 386-396, 501) mixes `@error_boundary` and `safe_execute_with_fallback`. Standardize on consistent patterns in ViewModels.

**Standardized Pattern**:
```python
class MealPlannerViewModel(BaseViewModel):
    def save_meal_plan(self) -> MealPlanSaveResultDTO:
        """Save meal plan with standardized error handling"""
        try:
            self._set_processing_state(True)
            
            # Validation
            validation_result = self._validate_meal_plan()
            if not validation_result.is_valid:
                self._emit_validation_errors(validation_result.errors)
                return MealPlanSaveResultDTO(success=False, message="Validation failed")
            
            # Business logic
            result = self.planner_service.save_meal_plan(self._build_save_dto())
            
            if result.success:
                DebugLogger.log("Meal plan saved successfully", "info")
            else:
                self._handle_error(Exception(result.message), "Save meal plan", "save_error")
            
            return result
            
        except Exception as e:
            self._handle_error(e, "Save meal plan operation", "save_error")
            return MealPlanSaveResultDTO(success=False, message="Save operation failed")
        finally:
            self._set_processing_state(False)
```

**Implementation Steps**:
1. Audit all error handling in ViewModels and UI classes
2. Remove inconsistent `@error_boundary` usage from UI
3. Standardize on ViewModel-based error handling
4. Implement consistent try-catch-finally patterns
5. Add proper state management during error conditions
6. Create error categorization and reporting
7. Update error signals and messaging
8. Write tests for error handling scenarios

**Success Criteria**:
- Consistent error handling patterns across all components
- Error handling centralized in ViewModels
- Proper state management during errors
- Comprehensive error logging and reporting

---

### Task 8: Implement Dependency Injection
**Priority**: Major | **Agent**: Architecture Specialist | **Effort**: Medium (3-4 days)

**Files Affected**:
- `app/ui/views/meal_planner.py` (constructor refactor)
- `app/ui/view_models/meal_planner_view_model.py` (service injection)
- `app/ui/view_models/meal_widget_view_model.py` (service injection)

**Description**:
Remove direct service instantiation (lines 61, 262) and implement proper dependency injection pattern following established project patterns.

**Dependency Injection Pattern**:
```python
class MealPlanner(ScrollableNavView):
    def __init__(self, 
                 planner_service: PlannerService,
                 recipe_service: RecipeService,
                 parent=None):
        super().__init__(parent)
        
        # Create ViewModels with injected services
        self.view_model = MealPlannerViewModel(
            planner_service=planner_service,
            recipe_service=recipe_service
        )
        
        self._setup_ui()
        self._connect_viewmodel_signals()
```

**Implementation Steps**:
1. Refactor MealPlanner constructor to accept service dependencies
2. Update MealWidget constructor for service injection
3. Modify ViewModel constructors to accept service parameters
4. Remove all direct service instantiation (`RecipeService()`, `PlannerService()`)
5. Update service creation in application bootstrap
6. Add service validation in constructors
7. Create factory methods for dependency creation
8. Write tests for dependency injection
9. Update documentation for new constructor patterns

**Success Criteria**:
- Zero direct service instantiation in UI components
- Services injected through constructors
- Proper service lifetime management
- Improved testability through dependency injection

---

## Phase 3: Structure & Performance (Priority: MINOR)

### Task 9: Extract Configuration Constants
**Priority**: Minor | **Agent**: Code Quality Specialist | **Effort**: Small (1-2 days)

**Files Affected**:
- `app/ui/config/meal_planner_config.py` (new file)
- `app/ui/views/meal_planner.py` (remove magic numbers)

**Description**:
Extract magic numbers and constants (lines 90-91, 162-163, 239, 372, 430) into a centralized configuration class.

**Configuration Class**:
```python
@dataclass(frozen=True)
class MealPlannerConfig:
    """Configuration constants for meal planner interface"""
    
    # Tab Configuration
    MAX_TABS: int = 10
    ADD_TAB_INDEX_OFFSET: int = 1
    TAB_ICON_SIZE: QSize = QSize(32, 32)
    
    # Recipe Slot Configuration  
    SIDE_SLOT_COUNT: int = 3
    MAX_SIDE_RECIPES: int = 3
    
    # UI Configuration
    LAYOUT_SPACING: int = 15
    DEFAULT_MEAL_NAME: str = "Custom Meal"
    
    # Tooltips
    ADD_TAB_TOOLTIP: str = "Add Meal"
    SAVE_BUTTON_TOOLTIP: str = "Save Meal Plan"
```

**Implementation Steps**:
1. Create `MealPlannerConfig` dataclass with all constants
2. Replace magic numbers throughout meal_planner.py
3. Add validation for configuration values
4. Create configuration loading utilities
5. Add environment-based configuration override capability
6. Update tests to use configuration constants
7. Document configuration options

**Success Criteria**:
- No magic numbers in meal_planner.py
- Centralized configuration management
- Easy configuration customization
- Proper constant typing and validation

---

### Task 10: Optimize Service Usage Patterns
**Priority**: Minor | **Agent**: Performance Specialist | **Effort**: Medium (2-3 days)

**Files Affected**:
- `app/ui/view_models/meal_planner_view_model.py` (service optimization)
- `app/ui/view_models/meal_widget_view_model.py` (service optimization)

**Description**:
Address inefficient service instantiation (line 61) and implement service singletons/caching patterns for better performance.

**Service Optimization Pattern**:
```python
class MealPlannerViewModel(BaseViewModel):
    def __init__(self, planner_service: PlannerService, recipe_service: RecipeService):
        super().__init__()
        
        # Use injected services (no instantiation)
        self.planner_service = planner_service
        self.recipe_service = recipe_service
        
        # Cache frequently used data
        self._recipe_cache: Dict[int, RecipeDisplayDTO] = {}
        self._cache_expiry: datetime = datetime.now()
        
    def get_recipe_display_data(self, recipe_id: int) -> Optional[RecipeDisplayDTO]:
        """Get recipe data with caching"""
        if self._is_cache_expired() or recipe_id not in self._recipe_cache:
            recipe_data = self.recipe_service.get_recipe_display_dto(recipe_id)
            if recipe_data:
                self._recipe_cache[recipe_id] = recipe_data
        
        return self._recipe_cache.get(recipe_id)
```

**Implementation Steps**:
1. Implement recipe data caching in ViewModels
2. Add cache invalidation strategies
3. Optimize database query patterns
4. Implement lazy loading for non-critical data
5. Add performance monitoring and logging
6. Create cache size limits and cleanup
7. Add cache hit/miss metrics
8. Write performance tests

**Success Criteria**:
- Improved response times for recipe operations
- Reduced database query frequency
- Proper cache management and cleanup
- Performance metrics tracking

---

### Task 11: Improve Signal Management
**Priority**: Minor | **Agent**: PySide6 UI Specialist | **Effort**: Small (1-2 days)

**Files Affected**:
- `app/ui/utils/signal_utils.py` (new utility)
- `app/ui/views/meal_planner.py` (safer signal blocking)

**Description**:
Improve signal blocking pattern (lines 143-145) with safer context manager approach to prevent issues if exceptions occur.

**Signal Blocking Context Manager**:
```python
@contextmanager
def signal_blocker(*signal_objects):
    """Context manager for safe signal blocking"""
    blocked_signals = []
    try:
        # Block all signals
        for obj in signal_objects:
            if hasattr(obj, 'blockSignals'):
                was_blocked = obj.signalsBlocked()
                obj.blockSignals(True)
                blocked_signals.append((obj, was_blocked))
        
        yield
        
    finally:
        # Restore signal state
        for obj, was_blocked in blocked_signals:
            obj.blockSignals(was_blocked)

# Usage:
with signal_blocker(self.slot_widget):
    self.slot_widget.set_recipe(recipe)
```

**Implementation Steps**:
1. Create `signal_blocker` context manager utility
2. Replace all manual signal blocking with context manager
3. Add error handling within signal operations
4. Create batch signal operations utilities
5. Add signal state validation
6. Write tests for signal management
7. Document signal blocking patterns

**Success Criteria**:
- Safe signal blocking that prevents state corruption
- Consistent signal management patterns
- Proper error handling during signal operations
- Improved code reliability

---

## Phase 4: Testing & Validation (Priority: TESTING)

### Task 12: Create Comprehensive ViewModel Tests
**Priority**: Testing | **Agent**: Test Specialist | **Effort**: Large (4-5 days)

**Files Affected**:
- `_tests/unit/ui/view_models/test_meal_planner_view_model.py` (new file)
- `_tests/unit/ui/view_models/test_meal_widget_view_model.py` (new file)
- `_tests/integration/ui/test_meal_planner_integration.py` (new file)

**Description**:
Create comprehensive test coverage for all new ViewModels, ensuring business logic is thoroughly tested in isolation.

**Test Categories**:
```python
class TestMealPlannerViewModel:
    """Unit tests for MealPlannerViewModel"""
    
    def test_create_new_meal_tab_success(self):
        """Test successful meal tab creation"""
        
    def test_save_meal_plan_validation_errors(self):
        """Test meal plan save with validation failures"""
        
    def test_service_dependency_injection(self):
        """Test proper service dependency handling"""
        
    def test_error_handling_patterns(self):
        """Test standardized error handling"""
        
    def test_state_management_operations(self):
        """Test complex state tracking"""

class TestMealWidgetViewModel:
    """Unit tests for MealWidgetViewModel"""
    
    def test_load_meal_success(self):
        """Test successful meal loading"""
        
    def test_update_recipe_slot_validation(self):
        """Test recipe slot update validation"""
        
    def test_save_meal_with_modifications(self):
        """Test meal saving with tracked modifications"""
```

**Implementation Steps**:
1. Create test fixtures for ViewModels with mocked services
2. Write unit tests for all ViewModel public methods
3. Create integration tests for ViewModel-Service interactions
4. Add tests for error handling scenarios
5. Create tests for signal emissions and state changes
6. Add performance tests for caching operations
7. Create mock objects for complex dependencies
8. Add test coverage reporting
9. Write UI integration tests with pytest-qt

**Success Criteria**:
- 90%+ code coverage for all ViewModels
- All business logic paths tested
- Proper mocking of service dependencies
- Integration tests validate cross-layer communication

---

### Task 13: Create UI Integration Tests
**Priority**: Testing | **Agent**: UI Test Specialist | **Effort**: Medium (3-4 days)

**Files Affected**:
- `_tests/ui/views/test_meal_planner_ui.py` (new file)
- `_tests/ui/components/test_meal_widget_ui.py` (new file)

**Description**:
Create comprehensive UI tests to validate the refactored components work correctly with pytest-qt.

**UI Test Categories**:
```python
class TestMealPlannerUI:
    """UI tests for refactored MealPlanner"""
    
    @pytest.fixture
    def meal_planner_widget(self, qtbot, mock_services):
        """Create MealPlanner widget with mocked services"""
        planner_service, recipe_service = mock_services
        widget = MealPlanner(
            planner_service=planner_service,
            recipe_service=recipe_service
        )
        qtbot.addWidget(widget)
        return widget
    
    def test_add_meal_tab_creates_widget(self, qtbot, meal_planner_widget):
        """Test adding new meal tab creates proper widget"""
        
    def test_save_meal_plan_triggers_viewmodel(self, qtbot, meal_planner_widget):
        """Test save button triggers ViewModel operation"""
        
    def test_error_handling_updates_ui(self, qtbot, meal_planner_widget):
        """Test error conditions update UI appropriately"""
```

**Implementation Steps**:
1. Create UI test fixtures with proper widget setup
2. Write tests for all major UI interactions
3. Test ViewModel signal connections to UI updates
4. Create tests for error state handling
5. Add tests for tab management operations
6. Test drag-and-drop functionality
7. Create tests for keyboard navigation
8. Add accessibility tests
9. Test responsive layout behavior

**Success Criteria**:
- All major UI interactions tested
- ViewModel-UI communication validated
- Error handling visually tested
- Accessibility requirements verified

---

## Implementation Sequence & Dependencies

### Phase 1 Dependencies
- Task 1 (DTOs) must complete before Tasks 2-4
- Tasks 2-3 (ViewModels) can proceed in parallel after Task 1
- Task 4 (Widget refactor) requires Tasks 2-3 completion

### Phase 2 Dependencies  
- Tasks 5-6 (Utilities) can proceed in parallel
- Task 7 (Error handling) requires Tasks 2-3 completion
- Task 8 (Dependency injection) requires Tasks 2-4 completion

### Phase 3 Dependencies
- Tasks 9-11 can proceed in parallel with Phase 2
- No critical dependencies within Phase 3

### Phase 4 Dependencies
- Task 12 (ViewModel tests) requires Phase 1 completion
- Task 13 (UI tests) requires Phases 1-2 completion

## Risk Mitigation

### High Risk Areas
1. **Service Migration**: Ensure no service instantiation breaks
2. **Signal Connections**: Verify all ViewModel-UI connections work
3. **State Migration**: Preserve existing state behavior during refactor
4. **Data Consistency**: Ensure DTOs properly represent all model data

### Mitigation Strategies
1. **Incremental Refactoring**: Refactor one component at a time
2. **Backward Compatibility**: Maintain old interfaces during transition
3. **Comprehensive Testing**: Test each component before integration
4. **Feature Flagging**: Allow fallback to original implementation

## Success Metrics

### Architecture Compliance
- [ ] Zero direct Core model usage in UI layer
- [ ] All business logic in ViewModels  
- [ ] Proper dependency injection implemented
- [ ] Consistent error handling patterns

### Code Quality
- [ ] No magic numbers or hardcoded constants
- [ ] Comprehensive type hints throughout
- [ ] Consistent naming conventions
- [ ] Proper documentation for all public interfaces

### Testing Coverage
- [ ] 90%+ test coverage for ViewModels
- [ ] All UI interactions tested
- [ ] Error scenarios properly tested
- [ ] Performance characteristics validated

### Performance
- [ ] Reduced service instantiation overhead
- [ ] Improved response times through caching
- [ ] Proper memory management
- [ ] No performance regressions

This refactoring plan will transform the meal_planner.py file from architectural violation-heavy code into a clean, maintainable, and properly structured MVVM implementation that adheres to the project's established patterns and principles.