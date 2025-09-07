---
description: Investigate and resolve MealGenie runtime errors with focus on recipe domain and MVVM architectural issues
argument-hint: "<error-text-or-logs>"  
allowed-tools: Read, Grep, Glob, Edit, Bash, Task
---

# MealGenie Error Investigation: $ARGUMENTS

**AGENT STRATEGY**: Use **architecture-reviewer** for MVVM boundary violations and **recipe-domain-expert** for recipe-specific business logic errors.

Please investigate and resolve the following MealGenie error(s):

```
$ARGUMENTS
```

## Investigation Process

### 1. Error Analysis
- Parse error messages to identify root causes
- Extract key information: error types, missing attributes, failed operations
- Identify the execution flow that led to the error
- Determine if this is an initialization, runtime, or cleanup issue

### 2. Context Discovery
- Use Grep to search for relevant code patterns across the codebase
- Find where the failing attributes/methods should be defined
- Locate similar working implementations for comparison
- Identify recent changes that might have caused the issue

### 3. Root Cause Investigation
- Trace the error back to its source (missing initialization, incorrect imports, etc.)
- Check for architectural violations (UI importing Core, missing ViewModels, etc.)
- Verify proper dependency injection and service registration
- Look for timing issues (premature access, cleanup race conditions)

### 4. Solution Implementation
- Fix the immediate cause of the error
- Address any underlying architectural issues
- Ensure proper error handling is in place
- Add defensive coding where appropriate

### 5. Prevention Measures
- Suggest improvements to prevent similar errors
- Recommend additional validation or error handling
- Identify patterns that could be extracted to utilities

## Investigation Steps

### Step 1: Parse Error Details
Extract and analyze each error component:
- Error location (file, method, line if available)
- Error type and message
- Call stack or execution context
- Related warnings that might provide additional context

### Step 2: Code Search and Analysis
Use targeted searches to understand the problem:
```bash
# Search for missing attributes/methods
grep -r "attribute_name" app/

# Find class definitions and initialization
grep -r "class ClassName" app/

# Look for similar patterns that work
grep -r "similar_functionality" app/
```

### Step 3: Identify Fix Strategy
Based on the MealGenie architecture:
- **Missing ViewModel attributes**: Check if ViewModels are properly initialized
- **Navigation errors**: Verify route registration and view initialization
- **Qt object deletion**: Check for proper cleanup and signal disconnection
- **Import issues**: Ensure proper layer separation (UI ↔ Core boundaries)

### Step 4: Implement Solution
- Make targeted fixes to resolve the immediate error
- Ensure changes follow MVVM architecture patterns
- Add proper error handling and validation
- Update any related initialization code

### Step 5: Verification
- Test the fix by reproducing the original error scenario
- Verify no new errors are introduced
- Check that the solution follows project conventions

## Common MealGenie Error Patterns

### Recipe Data & MVVM Boundary Violations
Often caused by:
- Views importing from `app.core.services.*` instead of using ViewModels
- Recipe business logic in UI components instead of `RecipeService`
- Missing DTO transformations between layers
- Incomplete ViewModel initialization in recipe Views

### Recipe Domain Specific Errors
Usually due to:
- Recipe ingredient parsing failures in forms
- Recipe scaling calculation errors in services
- Meal planning constraint violations
- Recipe image loading and path resolution issues
- Nutrition calculation errors in recipe displays

### Navigation & UI Component Failures  
Typically from:
- Recipe views not properly registered in navigation system
- Missing route definitions for recipe/meal planning views
- Circular import issues between recipe UI components
- RecipeCard or MealWidget lifecycle management problems

### Qt Object Lifecycle Issues in Recipe Context
Common in:
- Recipe card widgets being deleted during background recipe loading
- Improper signal/slot cleanup in meal planning calendar widgets
- Threading issues with recipe image loading and UI updates
- Memory leaks in recipe browser progressive loading

## Output Format

Provide:
1. **Root Cause Analysis**: What exactly is causing the error
2. **Immediate Fix**: Code changes needed to resolve the error
3. **File Locations**: Specific files and lines that need modification
4. **Testing Instructions**: How to verify the fix works
5. **Prevention Recommendations**: How to avoid similar issues

Focus on providing a complete solution that not only fixes the immediate error but also improves the robustness of the affected code.
