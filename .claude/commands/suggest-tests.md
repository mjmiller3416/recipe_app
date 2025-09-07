---
description: Generate comprehensive MealGenie test cases focusing on recipe domain workflows and MVVM architectural boundaries
argument-hint: @<file-path>
allowed-tools: Read, Write, Edit, Task
---

# Suggest MealGenie Tests: $ARGUMENTS

**AGENT COORDINATION**: Use **test-recipe-specialist** for comprehensive recipe domain test coverage and **architecture-reviewer** for MVVM boundary validation tests.

Please analyze $ARGUMENTS and suggest comprehensive test cases optimized for MealGenie's recipe management workflows:

## Test Categories to Cover

### 1. Unit Tests
- Test each public method/function individually
- Test with valid inputs (happy path)
- Test edge cases and boundary conditions
- Test invalid inputs and error handling

### 2. Recipe Domain Integration Tests
- Test interactions between RecipeService and IngredientService
- Test recipe database operations and ingredient relationship handling
- Test meal planning service coordination with recipe services
- Test shopping list generation from recipe data

### 3. MealGenie Edge Cases & Error Conditions  
- Empty recipe ingredient lists, zero serving sizes
- Invalid recipe scaling factors (negative, zero, extremely large)
- Malformed ingredient parsing inputs
- Recipe image loading failures and missing image paths
- Meal planning constraint violations and dietary restriction conflicts
- Shopping list generation with no recipes selected

### 4. Recipe Business Logic Tests
- Verify recipe scaling mathematics preserve ingredient ratios
- Test meal planning algorithms respect dietary restrictions
- Validate nutrition calculation accuracy across recipe modifications
- Test ingredient parsing from natural language input
- Verify shopping list consolidation logic and quantity calculations

## Output Format
Provide:
1. **Test structure**: Recommended test file organization
2. **Test cases**: Specific test methods with descriptions
3. **Mock requirements**: What external dependencies need mocking
4. **Test data**: Sample data needed for testing
5. **Priority**: Which tests are most critical to implement first

Focus on practical, maintainable tests that provide real value.

---
