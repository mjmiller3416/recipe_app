---
description: Comprehensive MealGenie code review focusing on recipe domain bugs, MVVM patterns, and architectural concerns
argument-hint: @<file-path>
allowed-tools: Read, Write, Grep, Glob, Task
---

# MealGenie Code Review: $ARGUMENTS

**AGENT STRATEGY**: Use **architecture-reviewer** agent for architectural validation and **recipe-domain-expert** for recipe-specific business logic review.

Read @_docs/ARCHITECTURE.md and @CLAUDE.md for MealGenie architecture context.

Please perform a comprehensive review of the file $ARGUMENTS focusing on MealGenie's recipe management domain and MVVM architecture:

## 1. Critical Bug Detection
- Identify potential runtime errors, logic bugs, and edge cases
- Propose specific solutions with code examples where applicable
- Highlight any security vulnerabilities or data integrity issues

## 2. Pattern Extraction Opportunities
- Look for repeated code patterns that could benefit from helper functions
- Identify common logic that appears multiple times and suggest abstractions
- Consider maintainability and reusability when recommending extractions

## 3. Single Responsibility Principle
- Evaluate if functions are doing too much and should be split
- **Important**: Only recommend splitting when it genuinely improves readability and maintainability
- Consider the trade-off between function complexity and overall code clarity
- Avoid over-engineering - sometimes a slightly longer function is more readable than multiple tiny ones

## 4. MealGenie MVVM Architecture & Layer Violations
- **CRITICAL**: Views must NEVER import from `app.core.services.*` or `app.core.repositories.*`
- **UI Utils Rule**: `app/ui/utils/` should ONLY be imported by UI layer components
- **EXCEPTION**: `app/core/utils/` imports are ALLOWED from any layer (shared utilities)
- Flag any recipe domain business logic that has leaked into UI components
- Identify UI-specific code that might be in core modules
- **MealGenie-specific architectural concerns:**
  - Recipe business logic must stay in `RecipeService`, not UI components or ViewModels
  - Nutrition calculations belong in `app/core/services/`, not ViewModels
  - Meal planning algorithms must be in `PlannerService`, not Views
  - Shopping list generation logic belongs in `ShoppingService`
  - Database queries must be in repositories (`RecipeRepository`, `IngredientRepository`), never in Views
  - Recipe ingredient parsing should be in `ingredient_service.py`, not UI forms
  - **Data flow**: Models → DTOs → ViewModels → Views (never skip layers)

## 5. Logic Simplification
- Look for overly complex implementations that could be simplified
- **Critical**: Only suggest simplifications that maintain full functionality
- Consider readability, performance, and maintainability in recommendations
- Avoid premature optimization - focus on clarity improvements

## 6. MealGenie Performance Considerations (PySide6/Qt & Recipe Domain)
- **Recipe Browsing Performance**: Identify widget creation in recipe card loops that could cause UI lag
- **Recipe Search Efficiency**: Check for inefficient database queries in recipe/ingredient searches
- **Image Loading**: Look for blocking recipe image loading that should be moved to background threads
- **Memory Management**: Flag potential memory leaks in recipe card UI component lifecycle
- **Signal/Slot Optimization**: Identify excessive signal/slot connections in recipe forms and meal planning widgets
- **Recipe Data Loading**: Flag N+1 query problems in recipe-ingredient relationship loading
- **Meal Planning Performance**: Check calendar widget updates and meal plan persistence efficiency

## 7. Configuration Management
- Verify config.py exists in the package directory
- Check that configuration constants are properly imported and used
- Identify hardcoded values that should be moved to config
- Validate configuration naming conventions (ALL_CAPS for constants)
- Ensure configuration is accessible but not directly modified by UI components

## Configuration Analysis Commands
```bash
# Check if config exists
find $(dirname $FILE_PATH) -name "config.py" -type f

# Find hardcoded constants that should be in config
grep -r "= [0-9]\+\|= '[^']*'\|= \"[^\"]*\"" $PACKAGE_PATH --include="*.py" | grep -v config.py

# Check config imports
grep -r "from.*config import\|import.*config" $PACKAGE_PATH

# Find magic numbers/strings
grep -rE "[^a-zA-Z_][0-9]{2,}[^a-zA-Z_]|'[A-Z_]{3,}'|\"[A-Z_]{3,}\"" $PACKAGE_PATH --include="*.py"
```

## Review Guidelines
- Focus exclusively on the provided file unless cross-file context is essential
- Provide specific, actionable recommendations with code examples
- Explain the reasoning behind each suggestion
- Prioritize suggestions by impact (critical bugs first, then architectural issues, then improvements)

## Agent Delegation Strategy
**Primary Review**: Use **architecture-reviewer** agent for comprehensive architectural validation
**Recipe Domain Analysis**: Use **recipe-domain-expert** agent for recipe-specific business logic validation
**Final Integration**: Combine both agent findings into complete review

## Response Format
- **Review summary MUST be exported to .claude/reviews/review-$FILENAME.md**
- Use markdown formatting with code blocks for examples
- Structure the review into sections corresponding to the focus areas above
- **Include severity levels for each issue:**
  - **Critical**: MVVM boundary violations, recipe data integrity issues, security problems
  - **Major**: Architecture violations, significant performance issues in recipe workflows
  - **Minor**: Code quality improvements, minor optimizations
- **Add estimated effort:** Small (< 1 hour), Medium (1-4 hours), Large (> 4 hours)  
- **Note dependencies:** Issues that must be fixed before others can be addressed
- **Cross-reference**: Link to related refactoring commands (`plan-refactor.md`, `complete-task.md`)
