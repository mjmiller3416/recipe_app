---
description: Comprehensive code review focusing on bugs, patterns, concerns, and simplification
argument-hint: @<file-path>
---

# Code Review for $FILE_PATH
**Read @_docs/ARCHITECTURE.md for MealGenie architecture context.**

Please perform a comprehensive review of the file $FILE_PATH with focus on the following areas:

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

## 4. Architectural Concerns & Layer Violations
- Check for logic that doesn't belong in the current file/directory based on this structure:
  - **Core layer** (`app/core/`): Business logic, data models, repositories, services
  - **UI layer** (`app/ui/`): Presentation logic, components, view models, views
  - **Style layer** (`app/style/`): Styling, theming, animations
- Flag any core business logic that has leaked into UI components
- Identify UI-specific code that might be in core modules
- **MealGenie-specific concerns:**
  - Recipe domain logic should stay in core services, not UI components
  - Nutrition calculations belong in core, not view models
  - Database queries should be in repositories, not views
  - Meal planning logic should be centralized in services
- Suggest proper layer placement for misplaced code

## 5. Logic Simplification
- Look for overly complex implementations that could be simplified
- **Critical**: Only suggest simplifications that maintain full functionality
- Consider readability, performance, and maintainability in recommendations
- Avoid premature optimization - focus on clarity improvements

## 6. Performance Considerations (PySide6/Qt Specific)
- Identify widget creation in loops that could cause UI lag
- Check for inefficient database queries in recipe searches
- Look for potential memory leaks in UI component lifecycle
- Flag blocking operations that should be moved to background threads
- Identify excessive signal/slot connections that could impact performance

## Review Guidelines
- Focus exclusively on the provided file unless cross-file context is essential
- Provide specific, actionable recommendations with code examples
- Explain the reasoning behind each suggestion
- Prioritize suggestions by impact (critical bugs first, then architectural issues, then improvements)

## Response Format
- **Review summary should be exported to .claude/reviews/review-$FILENAME.md**
- Use markdown formatting with code blocks for examples
- Structure the review into sections corresponding to the focus areas above
- **Include severity levels for each issue:**
  - 🔴 **Critical**: Bugs, security issues, data integrity problems
  - 🟡 **Major**: Architecture violations, significant performance issues
  - 🔵 **Minor**: Code quality improvements, minor optimizations
- **Add estimated effort:** Small (< 1 hour), Medium (1-4 hours), Large (> 4 hours)
- **Note dependencies:** Issues that must be fixed before others can be addressed
