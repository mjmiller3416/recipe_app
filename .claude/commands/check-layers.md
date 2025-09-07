---
description: Validate MealGenie MVVM architectural boundaries and recipe domain layer separation  
argument-hint: @<file-path>
allowed-tools: Read, Write, Edit, Task
---

# Check MealGenie Architectural Layers: $ARGUMENTS

**AGENT COORDINATION**: Use **architecture-reviewer** for comprehensive MVVM boundary analysis and **recipe-domain-expert** for recipe business logic placement validation.

Please analyze $ARGUMENTS for proper MealGenie MVVM architectural layer separation with focus on recipe domain boundaries:

## Layer Definitions
- **Core layer** (`app/core/`): Business logic, data models, repositories, services, utilities
- **UI layer** (`app/ui/`): Presentation logic, components, view models, views, UI utilities
- **Style layer** (`app/style/`): Styling, theming, animations, visual effects

## Validation Checks

### 1. MealGenie MVVM Import Analysis
- **CRITICAL**: Views must NEVER import from `app.core.services.*` or `app.core.repositories.*`
- **UI Layer Rules**: UI modules can ONLY import `app.core.utils.*` (shared utilities) from Core, all other Core access through ViewModels
- **Core Layer Rules**: Core modules should NEVER import from UI or Style layers
- **Style Layer Rules**: Style modules must be independent of recipe business logic
- Check for circular dependencies between MealGenie architectural layers

### 2. Recipe Domain Responsibility Validation
- **Recipe Business Logic**: Must be in Core layer (`RecipeService`, `IngredientService`, `PlannerService`)
- **Recipe UI Logic**: Should be in UI layer (recipe ViewModels, recipe component logic)
- **Presentation Concerns**: Recipe displays, forms, and widgets in UI layer, not Core
- **Recipe Data Access**: Database/API logic in Core repositories (`RecipeRepository`, `IngredientRepository`)
- **Meal Planning Logic**: Meal planning algorithms in `PlannerService`, not UI components

### 3. MealGenie-Specific Violations to Flag
- Recipe database queries in UI components (Views, recipe forms, meal widgets)
- Recipe business validation in UI layer (ingredient parsing in forms vs services)
- UI components in Core modules (recipe card logic in services)
- Direct recipe model manipulation in UI (should go through DTOs and services)
- Hardcoded recipe styling and theming in business logic

### 4. Data Flow Validation
- UI should communicate with Core through well-defined interfaces
- Core should not know about UI implementation details
- Events/notifications should flow properly between layers

## Response Format
- **Review summary should be exported to .claude/reviews/review-$FILENAME.md**
1. **Use markdown formatting with code blocks for examples**
2. **Violations found**: Specific issues with file/line references
3. **Recommended fixes**: Where to move misplaced code
4. **Architecture score**: Overall adherence to layer separation
5. **Suggestions**: Improvements for better layer separation

---
