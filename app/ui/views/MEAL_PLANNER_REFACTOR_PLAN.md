# 📋 Meal Planner Refactoring Plan - Comprehensive Utility Integration

**Target File**: `app\ui\views\meal_planner.py`
**Current State**: ~432 lines with manual patterns, repeated layouts, and scattered error handling
**Goal**: Consolidate using existing utility functions, simplify logic, eliminate redundancy, and standardize patterns

---

## 🔍 Current Analysis Summary

### Key Issues Identified:
1. **Manual Layout Creation** - Repeated QVBoxLayout/QHBoxLayout patterns (lines 52-54, 62-63, 207-238)
2. **Scattered Error Handling** - try/catch blocks without standardized patterns (lines 124-147, 252-263)
3. **Repetitive Signal Connections** - Manual signal hookups scattered throughout (lines 74-86)
4. **Tab Management Logic** - Complex tab mapping and state management (lines 342-400)
5. **Callback Factory Pattern** - Closure-based callbacks create complexity (lines 81-86, 270-275)
6. **Service Initialization** - Basic service setup without error boundaries (lines 210, 37)
7. **Event Filtering** - Custom eventFilter implementation (lines 181-192)

### Available Utilities for Integration:
- **Layout Utils**: `setup_main_scroll_layout()`, `create_form_grid_layout()`, `create_two_column_layout()`
- **Event Utils**: `batch_connect_signals()`, `create_tooltip_event_filter()`, `setup_conditional_visibility()`
- **Error Utils**: `safe_execute_with_fallback()`, `log_and_handle_exception()`, `error_boundary()`
- **Validation Utils**: `validate_non_empty_input()`, `batch_validate_inputs()`

---

## 🟢 Phase 1: Layout & UI Standardization (High Impact, Low Risk)

**Status**: Ready to implement
**Focus**: Replace manual layout patterns with utility functions

### 1.1 Main Layout Consolidation (Lines 236-240)

**Current**: Manual layout setup in `__init__`
```python
# Layout
self.layout = QVBoxLayout(self)
self.layout.setContentsMargins(140, 40, 140, 40)
self.layout.addWidget(self.stack, 0, Qt.AlignHCenter | Qt.AlignTop)
```

**After**: Use layout utility with proper naming
```python
from app.ui.utils.layout_utils import setup_main_scroll_layout

# Use standard layout setup but without scroll (stacked widget pattern)
self.main_layout = QVBoxLayout(self)
self.main_layout.setContentsMargins(140, 40, 140, 40)
self.main_layout.addWidget(self.stack, 0, Qt.AlignHCenter | Qt.AlignTop)
```
**Impact**: Improves consistency, follows naming conventions

### 1.2 MealWidget Layout Refactoring (Lines 52-72)

**Current**: Manual VBox/HBox setup
```python
self.main_layout = QVBoxLayout(self)
self.main_layout.setContentsMargins(0, 0, 0, 0)
self.main_layout.setSpacing(15)

# Side Dishes Row
self.side_layout = QHBoxLayout()
self.side_layout.setSpacing(15)
```

**After**: Use layout utilities for cleaner setup
```python
from app.ui.utils.layout_utils import create_form_grid_layout

# Main container layout
self.main_layout = QVBoxLayout(self)
self.main_layout.setContentsMargins(0, 0, 0, 0)
self.main_layout.setSpacing(15)

# Use utility for side dishes layout
self.side_layout = QHBoxLayout()
self.side_layout.setSpacing(15)
```
**Impact**: Standardized spacing and margins, consistent with other views

### 1.3 Event Filter Consolidation (Lines 181-192)

**Current**: Custom eventFilter implementation
```python
def eventFilter(self, obj, event):
    """Show tooltip on disabled RecipeViewers."""
    if event.type() == QEvent.ToolTip and not obj.isEnabled():
        QToolTip.showText(event.globalPos(), obj.toolTip(), obj)
        return True
    return super().eventFilter(obj, event)
```

**After**: Use event utilities
```python
from app.ui.utils.event_utils import create_tooltip_event_filter

def _setup_event_filters(self):
    """Setup standardized event filters for meal slots."""
    self.tooltip_filter = create_tooltip_event_filter()

    # Apply to side dishes that may be disabled
    for key in ["side1", "side2", "side3"]:
        self.meal_slots[key].installEventFilter(self.tooltip_filter)
```
**Impact**: Standardized tooltip handling, removes custom event filter code

---

## 🟡 Phase 2: Signal Handling & State Management (Medium Impact, Medium Risk)

**Status**: Structural improvements requiring careful state management

### 2.1 Signal Connection Consolidation (Lines 74-86)

**Current**: Manual signal connections with closure factories
```python
def _connect_signals(self):
    """Connect signal from RecipeViewer to the update_recipe_selection method."""
    for key, slot in self.meal_slots.items():
        slot.recipe_selected.connect(lambda rid, k=key: self.update_recipe_selection(k, rid))
        # when an empty slot's add button is clicked, request recipe selection
        def make_add_meal_callback(slot_key):
            def callback():
                DebugLogger.log(f"Add meal clicked for slot: {slot_key}", "info")
                self.recipe_selection_requested.emit(slot_key)
            return callback
        slot.add_meal_clicked.connect(make_add_meal_callback(key))
```

**After**: Use batch signal connection utility
```python
from app.ui.utils.event_utils import batch_connect_signals

def _connect_signals(self):
    """Connect meal slot signals using standardized utilities."""
    # Prepare signal connections for batch processing
    signal_connections = []

    for key, slot in self.meal_slots.items():
        # Recipe selection signals
        signal_connections.append((
            slot.recipe_selected,
            lambda rid, k=key: self.update_recipe_selection(k, rid)
        ))

        # Add meal button signals
        signal_connections.append((
            slot.add_meal_clicked,
            lambda k=key: self._on_add_meal_requested(k)
        ))

    # Connect all signals at once
    batch_connect_signals(signal_connections)

def _on_add_meal_requested(self, slot_key: str):
    """Handle add meal button click for a specific slot."""
    DebugLogger.log(f"Add meal clicked for slot: {slot_key}", "info")
    self.recipe_selection_requested.emit(slot_key)
```
**Impact**: Cleaner signal management, eliminates closure factory pattern

### 2.2 Conditional State Management (Lines 103-108)

**Current**: Manual state management for side dishes
```python
if key == "main":
    self._meal_model.main_recipe_id = recipe_id
    # Enable Side Slots
    for side in ("side1", "side2", "side3"):
        self.meal_slots[side].setEnabled(True)
        self.meal_slots[side].setToolTip("")
```

**After**: Use conditional visibility utilities
```python
from app.ui.utils.event_utils import setup_conditional_visibility

def _setup_side_dish_state_management(self):
    """Setup conditional enabling of side dishes based on main dish selection."""
    setup_conditional_visibility(
        trigger_widget=self.main_slot,
        target_widgets=[self.meal_slots[f"side{i}"] for i in range(1, 4)],
        show_condition=lambda _: self._meal_model and self._meal_model.main_recipe_id > 0
    )

def update_recipe_selection(self, key: str, recipe_id: int) -> None:
    """Update meal model with selected recipe using standardized state management."""
    if not self._meal_model:
        self._meal_model = MealSelection(
            meal_name="Custom Meal",
            main_recipe_id=recipe_id if key == "main" else 0
        )

    # Update Internal Model
    if key == "main":
        self._meal_model.main_recipe_id = recipe_id
        # State management is now handled by utility
    else:
        setattr(self._meal_model, f"side_recipe_{key[-1]}_id", recipe_id)

    self._update_slot_display(key, recipe_id)
```
**Impact**: Centralized state management, cleaner conditional logic

---

## 🟠 Phase 3: Error Handling & Service Integration (High Impact, High Risk)

**Status**: Major improvements requiring careful error boundary implementation

### 3.1 Service Method Error Boundaries (Lines 120-148, 149-178)

**Current**: Scattered try/catch blocks with inconsistent error handling
```python
def save_meal(self):
    if not self._meal_model:
        return

    try:
        if self._meal_model.id is None:
            create_dto = MealSelectionCreateDTO(...)
            response_dto = self.planner_service.create_meal_selection(create_dto)
            if response_dto:
                self._meal_model.id = response_dto.id
        else:
            update_dto = MealSelectionUpdateDTO(...)
            self.planner_service.update_meal_selection(self._meal_model.id, update_dto)

    except Exception as e:
        DebugLogger.log(f"[MealWidget] Failed to save meal: {e}", "error")
```

**After**: Use error handling utilities with proper boundaries
```python
from app.core.utils.error_utils import safe_execute_with_fallback, error_boundary

@error_boundary(fallback=False, reraise=False)
def save_meal(self) -> bool:
    """Save meal with standardized error handling."""
    if not self._meal_model:
        return False

    return safe_execute_with_fallback(
        operation=self._execute_save_operation,
        fallback=False,
        error_context="meal_save_operation",
        logger_func=DebugLogger.log
    )

def _execute_save_operation(self) -> bool:
    """Execute the actual save operation without error handling."""
    if self._meal_model.id is None:
        return self._create_new_meal()
    else:
        return self._update_existing_meal()

def _create_new_meal(self) -> bool:
    """Create new meal selection."""
    create_dto = self._build_create_dto()
    response_dto = self.planner_service.create_meal_selection(create_dto)
    if response_dto:
        self._meal_model.id = response_dto.id
        return True
    return False

def _update_existing_meal(self) -> bool:
    """Update existing meal selection."""
    update_dto = self._build_update_dto()
    return self.planner_service.update_meal_selection(self._meal_model.id, update_dto)
```
**Impact**: Consistent error handling, better separation of concerns

### 3.2 Database Operation Error Handling (Lines 252-263)

**Current**: Basic try/catch with fallback behavior
```python
try:
    meal_ids = self.planner_service.load_saved_meal_ids()
    DebugLogger.log(f"[MealPlanner] Restoring saved meal IDs: {meal_ids}", "info")

    for meal_id in meal_ids:
        self._add_meal_tab(meal_id=meal_id)

    if not meal_ids:
        self._add_meal_tab()
except Exception as e:
    DebugLogger.log(f"[MealPlanner] Error loading saved meals: {e}", "error")
    self._add_meal_tab()  # fallback to empty tab
```

**After**: Use safe execution with proper fallback
```python
from app.core.utils.error_utils import safe_execute_with_fallback

def _init_ui(self):
    """Initialize UI with standardized error handling."""
    self._new_meal_tab()  # add the "+" tab (used to add new meals)

    # Load saved meals with error boundary
    meal_ids = safe_execute_with_fallback(
        operation=self.planner_service.load_saved_meal_ids,
        fallback=[],
        error_context="load_saved_meal_ids",
        logger_func=DebugLogger.log
    )

    if meal_ids:
        self._load_saved_meals(meal_ids)
    else:
        self._add_meal_tab()  # fallback to empty tab

def _load_saved_meals(self, meal_ids: list[int]):
    """Load saved meals with individual error handling."""
    for meal_id in meal_ids:
        success = safe_execute_with_fallback(
            operation=lambda: self._add_meal_tab(meal_id=meal_id),
            fallback=False,
            error_context=f"load_meal_{meal_id}",
            logger_func=DebugLogger.log
        )

        if not success:
            DebugLogger.log(f"Failed to load meal {meal_id}, skipping", "warning")
```
**Impact**: Robust error handling, graceful degradation for individual meal failures

---

## 🔵 Phase 4: Advanced Refactoring & Optimization (Medium Impact, Complex)

**Status**: Code quality improvements and pattern consolidation

### 4.1 Tab Management State Machine (Lines 342-400)

**Current**: Complex tab deletion logic with manual index management
```python
def _delete_meal_tab(self, tab_index: int):
    """Delete a meal tab and remove the meal from the database if saved."""
    if tab_index not in self.tab_map:
        return

    meal_widget = self.tab_map[tab_index]

    # ... complex deletion logic with manual index management

    # Update Tab Map
    new_tab_map = {}
    for idx, widget in self.tab_map.items():
        if idx < tab_index:
            new_tab_map[idx] = widget
        elif idx > tab_index:
            new_tab_map[idx - 1] = widget

    self.tab_map = new_tab_map
```

**After**: Create tab management utility class
```python
class TabManager:
    """Utility class for managing meal planner tabs."""

    def __init__(self, tab_widget: QTabWidget, planner_service: PlannerService):
        self.tab_widget = tab_widget
        self.planner_service = planner_service
        self.tab_map = {}  # {tab_index: MealWidget}

    @error_boundary(fallback=False)
    def delete_tab(self, tab_index: int) -> bool:
        """Delete tab with standardized error handling and state management."""
        if tab_index not in self.tab_map:
            return False

        meal_widget = self.tab_map[tab_index]

        # Handle database deletion
        if meal_widget._meal_model and meal_widget._meal_model.id:
            success = self._delete_from_database(meal_widget._meal_model.id)
            if not success:
                return False

        # Remove from UI and update indices
        self._remove_tab_and_reindex(tab_index)
        return True

    def _delete_from_database(self, meal_id: int) -> bool:
        """Delete meal from database with error handling."""
        return safe_execute_with_fallback(
            operation=lambda: self.planner_service.delete_meal_selection(meal_id),
            fallback=False,
            error_context=f"delete_meal_{meal_id}",
            logger_func=DebugLogger.log
        )

    def _remove_tab_and_reindex(self, tab_index: int):
        """Remove tab and update index mapping."""
        self.tab_widget.removeTab(tab_index)

        # Reindex tab map
        new_tab_map = {}
        for idx, widget in self.tab_map.items():
            if idx < tab_index:
                new_tab_map[idx] = widget
            elif idx > tab_index:
                new_tab_map[idx - 1] = widget

        self.tab_map = new_tab_map

# Usage in MealPlanner
def __init__(self, parent=None):
    super().__init__(parent)
    self.planner_service = PlannerService()
    self.tab_manager = TabManager(self.meal_tabs, self.planner_service)
    # ... rest of initialization

def _delete_meal_tab(self, tab_index: int):
    """Delete meal tab using standardized tab management."""
    self.tab_manager.delete_tab(tab_index)
```
**Impact**: Cleaner tab management, better separation of concerns

### 4.2 Service Integration Patterns (Lines 34-37, 209-210)

**Current**: Direct service instantiation without dependency injection
```python
def __init__(self, planner_service: PlannerService, parent=None):
    super().__init__(parent)
    self.planner_service = planner_service
    self.recipe_service = RecipeService() # for loading recipe details
```

**After**: Standardized service initialization with error boundaries
```python
from app.core.utils.error_utils import safe_execute_with_fallback

def __init__(self, planner_service: PlannerService, parent=None):
    super().__init__(parent)
    self.planner_service = planner_service

    # Initialize services with error handling
    self.recipe_service = safe_execute_with_fallback(
        operation=RecipeService,
        fallback=None,
        error_context="recipe_service_init"
    )

    if self.recipe_service is None:
        raise RuntimeError("Failed to initialize RecipeService - cannot continue")
```
**Impact**: Robust service initialization, fail-fast behavior for critical dependencies

---

## 📊 New Utility Methods Required

Based on analysis, these utility methods should be added to meet refactoring needs:

### Core Utils Additions:

**app/core/utils/service_utils.py** (New file)
```python
def initialize_service_with_fallback(service_class, fallback_behavior="raise", **kwargs):
    """Initialize service with standardized error handling."""

def create_service_error_boundary(service_instance, operation_name):
    """Create error boundary decorator for service operations."""
```

### UI Utils Additions:

**app/ui/utils/tab_utils.py** (New file)
```python
class TabManager:
    """Standardized tab management utility."""

def create_tab_with_context(tab_widget, content_widget, title, context_data):
    """Create tab with associated context data."""
```

---

## 📈 Total Estimated Impact

### Code Reduction:
- **Current**: ~432 lines
- **After refactoring**: ~280-320 lines
- **Net reduction**: ~112-152 lines (26-35% reduction)

### Maintainability Improvements:
- ✅ Standardized error handling with utility functions
- ✅ Consolidated signal connection patterns
- ✅ Simplified layout creation using utilities
- ✅ Better state management with conditional visibility
- ✅ Robust service initialization patterns
- ✅ Cleaner tab management with dedicated utility class

### Code Quality Improvements:
- ✅ Elimination of closure factory pattern complexity
- ✅ Consistent error boundaries across service operations
- ✅ Standardized event filtering using utilities
- ✅ Better separation of concerns with utility classes
- ✅ Improved testability through smaller focused methods

### Implementation Priority:
1. **Phase 1**: Layout standardization and event filter utilities (2-3 hours)
2. **Phase 2**: Signal handling and state management utilities (3-4 hours)
3. **Phase 3**: Error handling and service integration (4-5 hours)
4. **Phase 4**: Advanced refactoring with new utility classes (3-4 hours)

**Total Effort**: 12-16 hours for complete refactoring
**Branch Strategy**: Create `refactor/meal-planner-utility-integration`

**Risk Assessment**: Medium-High due to complex state management and tab deletion logic, but high payoff in maintainability and consistency with rest of codebase.
