---
description: Generate comprehensive test cases for a file
argument-hint: @<file-path>
---

# Suggest Tests: $ARGUMENTS

Please analyze $ARGUMENTS and suggest comprehensive test cases:

## Test Categories to Cover

### 1. Unit Tests
- Test each public method/function individually
- Test with valid inputs (happy path)
- Test edge cases and boundary conditions
- Test invalid inputs and error handling

### 2. Integration Points
- Test interactions between classes/modules
- Test database operations (if applicable)
- Test external dependencies (mocked appropriately)

### 3. Edge Cases & Error Conditions
- Empty inputs, null values, zero values
- Maximum/minimum boundary values
- Invalid data types
- Network failures or timeouts (if applicable)
- Permission/access errors

### 4. Business Logic Tests
- Verify core business rules are enforced
- Test complex workflows end-to-end
- Validate data transformations

## Output Format
Provide:
1. **Test structure**: Recommended test file organization
2. **Test cases**: Specific test methods with descriptions
3. **Mock requirements**: What external dependencies need mocking
4. **Test data**: Sample data needed for testing
5. **Priority**: Which tests are most critical to implement first

Focus on practical, maintainable tests that provide real value.

---
