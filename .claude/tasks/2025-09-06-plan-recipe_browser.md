# Refactoring Plan: RecipeBrowser Component

## Executive Summary
**Component**: RecipeBrowser and associated wrapper components
**Review Date**: 2025-09-06
**Total Tasks**: 12
**Estimated Effort**: High (12-18 hours)
**Architecture Decision**: **Option A - MainView Conversion** (Recommended for full MVVM compliance)

The RecipeBrowser component suffers from wrapper layer proliferation, MVVM non-compliance, and navigation inconsistencies. This plan addresses three major architectural concerns through a coordinated multi-phase refactoring that converts RecipeBrowser to a proper MainView, establishes MVVM compliance, and standardizes navigation patterns.

---

## Architecture Decision: Option A - MainView Conversion

**Rationale**: Option A provides the most comprehensive solution aligning with MealGenie's layered clean architecture:
- ✅ **Full MVVM Compliance**: Separates business logic into ViewModel layer
- ✅ **Navigation Standardization**: Uses navigation service consistently
- ✅ **Eliminates Wrapper Proliferation**: Single RecipeBrowserView handles all use cases
- ✅ **Architectural Consistency**: Aligns with other MainView implementations

**Trade-offs**: Higher implementation effort but delivers complete architectural alignment.

---

## Critical Issues (Must Fix)

### Task 1: Create RecipeBrowserViewModel
**Priority**: Critical
**Files Affected**:
- `app/ui/view_models/recipe_browser_view_model.py` (create)
- `_tests/unit/ui/view_models/test_recipe_browser_view_model.py` (create)

**Description**: Extract business logic from RecipeBrowser component into dedicated ViewModel following MVVM pattern.

**Implementation Steps**:
1. Create `RecipeBrowserViewModel` class with filtering, sorting, and search logic
2. Move all `RecipeService` interactions to ViewModel layer
3. Implement proper data binding patterns with signals/slots
4. Add comprehensive unit tests for business logic
5. Ensure DTO usage for data transfer

**Agent Assignment**: python-backend-architect (business logic patterns)

**Dependencies**: None
**Estimated Effort**: 4-6 hours

---

### Task 2: Convert RecipeBrowser to RecipeBrowserView (MainView)
**Priority**: Critical
**Files Affected**:
- `app/ui/views/recipe_browser_view.py` (create)
- `app/ui/components/composite/recipe_browser.py` (refactor/deprecate)

**Description**: Convert RecipeBrowser component to proper ScrollableNavView implementation integrating with ViewModel.

**Implementation Steps**:
1. Create `RecipeBrowserView` inheriting from `ScrollableNavView`
2. Integrate with `RecipeBrowserViewModel` for business logic
3. Support both normal and selection modes via parameters
4. Implement proper navigation lifecycle methods
5. Migrate UI layout and component initialization
6. Add signals for navigation events (`recipe_selected`, `recipe_opened`)

**Agent Assignment**: pyside6-frontend-architect (MainView patterns, UI composition)

**Dependencies**: Task 1 (RecipeBrowserViewModel)
**Estimated Effort**: 4-5 hours

---

### Task 3: Update Navigation Routes and Service Integration
**Priority**: Critical
**Files Affected**:
- `app/ui/managers/navigation/routes.py`
- Navigation service route mappings

**Description**: Register new RecipeBrowserView routes and update navigation service integration.

**Implementation Steps**:
1. Add routes for `/recipes/browse` and `/recipes/browse/selection`
2. Update route configuration to support selection_mode parameter
3. Remove ViewRecipes route (replaced by RecipeBrowserView)
4. Ensure proper route title and description metadata
5. Test route resolution and parameter passing

**Agent Assignment**: pyside6-frontend-architect (navigation patterns)

**Dependencies**: Task 2 (RecipeBrowserView)
**Estimated Effort**: 2-3 hours

---

### Task 4: Remove Wrapper Classes (ViewRecipes, RecipeSelection)
**Priority**: Critical
**Files Affected**:
- `app/ui/views/view_recipes/view_recipes.py` (remove)
- `app/ui/views/recipe_selection.py` (remove)
- `app/ui/views/__init__.py` (update imports)

**Description**: Eliminate redundant wrapper classes and update all references to use direct navigation.

**Implementation Steps**:
1. Audit all usages of ViewRecipes and RecipeSelection
2. Update import statements throughout codebase
3. Remove deprecated wrapper class files
4. Update package __init__.py files
5. Verify no broken imports remain

**Agent Assignment**: python-backend-architect (code refactoring, import management)

**Dependencies**: Task 2, Task 3 (RecipeBrowserView and routes established)
**Estimated Effort**: 1-2 hours

---

## Navigation Standardization Tasks

### Task 5: Update Dashboard Navigation
**Priority**: High
**Files Affected**:
- Dashboard view implementation
- Navigation button click handlers

**Description**: Update Dashboard to use navigation service instead of ViewRecipes wrapper.

**Implementation Steps**:
1. Replace ViewRecipes instantiation with navigation service calls
2. Update button click handlers to use `navigate_to("/recipes/browse")`
3. Remove ViewRecipes imports
4. Test navigation flow from Dashboard

**Agent Assignment**: pyside6-frontend-architect (view updates)

**Dependencies**: Task 3 (routes established)
**Estimated Effort**: 1 hour

---

### Task 6: Update MealPlanner Navigation
**Priority**: High
**Files Affected**:
- MealPlanner view implementation
- Recipe selection integration

**Description**: Update MealPlanner to use navigation service for recipe selection instead of RecipeSelection wrapper.

Remove QStackedWidget, which currently holds RecipeSelection, and replace with navigation calls.

**Implementation Steps**:
1. Replace RecipeSelection instantiation with navigation calls
2. Use `navigate_to("/recipes/browse/selection")` for recipe selection
3. Implement proper signal handling for recipe selection results
4. Update UI layout to accommodate navigation-based flow
5. Test meal planning recipe selection workflow

**Agent Assignment**: pyside6-frontend-architect (complex view integration)

**Dependencies**: Task 3, Task 4 (routes and wrapper removal)
**Estimated Effort**: 2-3 hours

---

## Testing and Validation Tasks

### Task 7: Create RecipeBrowserView Integration Tests
**Priority**: High
**Files Affected**:
- `_tests/integration/ui/test_recipe_browser_view.py` (create)

**Description**: Comprehensive integration tests for RecipeBrowserView functionality.

**Implementation Steps**:
1. Test normal browsing mode (recipe viewing)
2. Test selection mode (recipe selection for meal planning)
3. Test filtering and sorting functionality
4. Test navigation integration (signals, route handling)
5. Test ViewModel integration and data binding

**Agent Assignment**: python-backend-architect (testing patterns)

**Dependencies**: Task 2 (RecipeBrowserView complete)
**Estimated Effort**: 2 hours

---

### Task 8: Create UI Tests for Navigation Integration
**Priority**: High
**Files Affected**:
- `_tests/ui/test_recipe_browser_navigation.py` (create)

**Description**: pytest-qt tests for navigation service integration.

**Implementation Steps**:
1. Test Dashboard → Recipe Browser navigation
2. Test MealPlanner → Recipe Selection navigation
3. Test back/forward navigation in recipe browsing
4. Test signal emission and handling
5. Mock navigation service for isolated testing

**Agent Assignment**: pyside6-frontend-architect (UI testing, pytest-qt)

**Dependencies**: Task 5, Task 6 (navigation updates)
**Estimated Effort**: 2 hours

---

## Code Quality and Documentation Tasks

### Task 9: Update Component Documentation
**Priority**: Medium
**Files Affected**:
- RecipeBrowserView class docstrings
- Navigation service documentation

**Description**: Update code documentation to reflect new architecture.

**Implementation Steps**:
1. Document RecipeBrowserView usage patterns and modes
2. Update navigation service route documentation
3. Document ViewModel interaction patterns
4. Add code examples for common use cases

**Agent Assignment**: architecture-reviewer (documentation standards)

**Dependencies**: Task 2, Task 3 (implementation complete)
**Estimated Effort**: 1 hour

---

### Task 10: Performance Optimization Review
**Priority**: Medium
**Files Affected**:
- RecipeBrowserView rendering logic
- ViewModel data handling

**Description**: Review and optimize performance aspects of new implementation.

**Implementation Steps**:
1. Profile recipe loading and filtering performance
2. Optimize ViewModel data caching strategies
3. Review UI rendering performance in different modes
4. Implement lazy loading where appropriate

**Agent Assignment**: python-backend-architect (performance analysis)

**Dependencies**: Task 1, Task 2 (core implementation)
**Estimated Effort**: 1-2 hours

---

## Final Validation Tasks

### Task 11: Comprehensive Architecture Review
**Priority**: High
**Files Affected**:
- All modified files
- Architecture compliance validation

**Description**: Final architectural compliance validation against MealGenie standards.

**Implementation Steps**:
1. Verify MVVM pattern implementation correctness
2. Validate layer boundary compliance (no UI imports in core)
3. Confirm navigation service integration consistency
4. Review test coverage completeness
5. Document any remaining architectural debt

**Agent Assignment**: architecture-reviewer (final validation)

**Dependencies**: All previous tasks
**Estimated Effort**: 1-2 hours

---

### Task 12: End-to-End Application Testing
**Priority**: Critical
**Files Affected**:
- Full application workflow testing

**Description**: Comprehensive end-to-end testing of refactored functionality.

**Implementation Steps**:
1. Test complete recipe browsing workflow (Dashboard → Browse → Full Recipe)
2. Test meal planning workflow (MealPlanner → Recipe Selection → Selection)
3. Test navigation history (back/forward functionality)
4. Verify all features work in both modes
5. Performance validation under typical usage

**Agent Assignment**: pyside6-frontend-architect (E2E testing)

**Dependencies**: All previous tasks
**Estimated Effort**: 1-2 hours

---

## Implementation Phases

### Phase 1: Core Architecture (Tasks 1-2)
**Estimated Duration**: 8-11 hours
**Focus**: Establish ViewModel and MainView foundation
**Critical Path**: RecipeBrowserViewModel → RecipeBrowserView

### Phase 2: Navigation Integration (Tasks 3-6)
**Estimated Duration**: 6-9 hours
**Focus**: Navigation service integration and wrapper removal
**Critical Path**: Routes → Dashboard/MealPlanner updates → Wrapper removal

### Phase 3: Validation & Quality (Tasks 7-12)
**Estimated Duration**: 7-10 hours
**Focus**: Testing, documentation, and final validation
**Parallel Execution**: Testing tasks can run parallel to documentation

---

## Risk Mitigation

### High Risk Areas
1. **MealPlanner Integration**: Recipe selection workflow complexity
2. **Signal/Slot Changes**: Breaking existing connections
3. **Navigation History**: Maintaining proper back/forward behavior

### Mitigation Strategies
1. **Incremental Testing**: Test each component independently
2. **Backup Strategy**: Maintain wrapper classes until validation complete
3. **Rollback Plan**: Clear git commit boundaries for each phase

---

## Success Criteria

### Architecture Compliance
- [ ] **MVVM Pattern**: Business logic properly separated into ViewModel
- [ ] **Layer Boundaries**: No UI imports in core layer
- [ ] **Navigation Consistency**: All navigation uses navigation service
- [ ] **Wrapper Elimination**: No redundant wrapper classes

### Functional Requirements
- [ ] **Recipe Browsing**: Normal mode works identically to current
- [ ] **Recipe Selection**: Selection mode works identically for meal planning
- [ ] **Navigation**: Back/forward navigation functions properly
- [ ] **Performance**: No degradation in loading or rendering performance

### Quality Gates
- [ ] **Test Coverage**: 90%+ coverage for new ViewModel and View code
- [ ] **Integration Tests**: All navigation flows tested
- [ ] **Documentation**: Complete documentation of new patterns
- [ ] **Code Review**: Architecture reviewer approval

---

**Estimated Total Effort**: 12-18 hours across 3 phases
**Risk Level**: Medium-High (affects core navigation patterns)
**Architecture Compliance Goal**: 🟢 Full Navigation and MVVM Compliance
**Recommended Team**: 3 agents (python-backend-architect, pyside6-frontend-architect, architecture-reviewer)
