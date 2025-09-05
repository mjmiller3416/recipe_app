---
description: Validate architectural boundaries and layer separation
argument-hint: @<file-path>
---

# Check Architectural Layers: $ARGUMENTS

Please analyze $ARGUMENTS for proper architectural layer separation:

## Layer Definitions
- **Core layer** (`app/core/`): Business logic, data models, repositories, services, utilities
- **UI layer** (`app/ui/`): Presentation logic, components, view models, views, UI utilities
- **Style layer** (`app/style/`): Styling, theming, animations, visual effects

## Validation Checks

### 1. Import Analysis
- Core modules should NOT import from UI or Style layers
- UI modules can import from Core but should minimize direct dependencies
- Style modules should be independent of business logic
- Check for circular dependencies between layers

### 2. Responsibility Validation
- Business logic should be in Core layer (models, services, repositories)
- UI-specific logic should be in UI layer (view models, component logic)
- Presentation concerns should be in UI layer, not Core
- Database/API logic should be in Core services/repositories

### 3. Common Violations to Flag
- Database queries in UI components
- Business validation in UI layer
- UI components in Core modules
- Direct model manipulation in UI (should go through services)
- Hardcoded styling in business logic

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
