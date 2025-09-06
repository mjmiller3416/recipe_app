---
description: Comprehensive package-level review analyzing entire features across MVVM layers with integration validation
argument-hint: <package-path> [additional-paths...]
allowed-tools: Read, Grep, Glob, Write
---

# Package Review: $ARGUMENTS

Please perform a comprehensive package-level architectural review of the specified feature package and its associated components across the MealGenie MVVM architecture.

## Analysis Strategy

### 1. Package Discovery Phase
- Identify the primary package directory and all contained files
- Use Grep/Glob to find associated ViewModels in `app/ui/view_models/`
- Discover related Core Services in `app/core/services/`
- Find supporting utilities in `app/ui/utils/` and `app/core/utils/`
- Map DTOs and models in `app/core/dtos/` and `app/core/models/`

### 2. Dependency Mapping
```bash
# Example discovery commands to use:
grep -r "import.*add_recipe" app/ui/view_models/
grep -r "AddRecipe" app/core/services/
find app/ -name "*recipe*" -type f
```

### 3. Architecture Flow Analysis
- **View → ViewModel**: Verify Views delegate business logic to ViewModels
- **ViewModel → Core**: Ensure ViewModels use Core Services through DTOs
- **Core Services → Repositories**: Validate business logic uses proper data access
- **Cross-cutting Concerns**: Check utilities, error handling, validation patterns

### 4. Integration Validation
- Signal/slot connections between UI components
- Service registration and dependency injection
- Shared state management
- Error propagation and handling

## Review Process

### Step 1: Discovery and Mapping (Use project-orchestrator agent)
Create a comprehensive map of all files and dependencies related to the package. Use Grep and Glob tools to discover the complete feature footprint.

### Step 2: Architectural Analysis (Use package-architecture-reviewer agent)
Analyze the discovered files for:
- MVVM layer compliance
- Integration completeness
- Data flow correctness
- Architecture pattern consistency

### Step 3: Component-Level Review (Use architecture-reviewer agent)
For each major component, verify:
- Single responsibility adherence
- Proper layer placement
- Code quality and patterns

### Step 4: Synthesis and Recommendations
Combine findings into actionable recommendations prioritized by:
- Critical integration failures
- Architecture violations
- Performance issues
- Code quality improvements

## Output Requirements

### Create Comprehensive Report
Save the analysis as `.claude/reviews/package-review-[package-name].md` containing:

```markdown
# Package Architecture Review: [Package Name]

## Discovery Summary
- **Primary Package**: [Path and file count]
- **Associated ViewModels**: [List with integration points]
- **Core Services**: [Related services and repositories]
- **Supporting Utilities**: [UI and Core utilities used]
- **DTOs/Models**: [Data transfer objects and models]

## Architecture Flow Analysis
### Data Flow Diagram (Text)
[Trace a typical user interaction through all layers]

### Layer Boundary Analysis
[Validate import restrictions and responsibility separation]

## Integration Assessment
### Signal/Slot Connections
[Review UI event handling and ViewModel coordination]

### Service Integration
[Validate business logic coordination and data access]

### Error Handling
[Check error propagation and user feedback patterns]

## Component Reviews
[Focused analysis of each major component within architectural context]

## Critical Issues
**Critical**: [Immediate fixes required]
**Major**: [Architecture violations, integration problems]
**Minor**: [Code quality improvements]

## Recommendations
### Immediate Actions
### Architectural Improvements
### Performance Optimizations

## Implementation Plan
[Suggested order of fixes and improvements]
```

### Multi-Agent Coordination
This command should coordinate multiple agents:
1. **project-orchestrator**: For discovery and planning
2. **package-architecture-reviewer**: For holistic architectural analysis
3. **architecture-reviewer**: For component-level validation
4. **pyside6-frontend-architect**: For UI-specific concerns
5. **python-backend-architect**: For Core layer analysis

## Usage Examples

```bash
# Review entire add_recipes package
/review-package app/ui/views/add_recipes

# Review with explicit additional components
/review-package app/ui/views/meal_planner app/ui/view_models/meal_planner_view_model.py

# Review core service package
/review-package app/core/services/recipe_service.py
```

The command will automatically discover related components and provide a comprehensive architectural assessment of how the entire feature works together.
