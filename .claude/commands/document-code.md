# Document Code Command

**Description:** Add comprehensive docstrings and comments to Python files without changing any functional logic

**Argument Hint:** @<file-path>

**Allowed Tools:** Read, Edit

## Document Code: $ARGUMENTS

Please add comprehensive docstrings and inline comments to the Python file `$ARGUMENTS` while preserving all existing functionality exactly as it is.

## Documentation Requirements

### 1. Docstring Standards

Follow Google-style docstrings for all functions, classes, and methods:

```python
def method_name(self, param1: str, param2: int = None) -> bool:
    """Brief one-line description of what the method does.

    More detailed description if needed, explaining complex behavior,
    side effects, or important implementation details.

    Args:
        param1: Description of first parameter and its purpose
        param2: Description of second parameter with default value

    Returns:
        Description of return value and what it represents

    Raises:
        SpecificException: When this specific error condition occurs
        AnotherException: When this other condition happens

    Example:
        Basic usage example if the method is complex:

        >>> result = obj.method_name("hello", 42)
        >>> print(result)
        True
    """
```

### 2. Class Documentation

Document all classes with comprehensive information:

```python
class ClassName:
    """Brief description of the class purpose and main functionality.

    Longer description explaining the class role in the application,
    its main responsibilities, design patterns used, and how it
    integrates with other components.

    Attributes:
        attribute_name: Description of important instance attributes
        another_attr: Description of other key attributes

    Example:
        Basic usage pattern:

        >>> obj = ClassName(param1, param2)
        >>> result = obj.main_method()
    """
```

### 3. Inline Comments

Add helpful inline comments for:

#### Complex Logic:

```python
# Calculate compound interest using the formula: A = P(1 + r/n)^(nt)
final_amount = principal * (1 + rate / compounds_per_year) ** (compounds_per_year * years)
```

#### Business Rules:

```python
# Business rule: Recipe must have at least one ingredient to be valid
if len(ingredients) < 1:
    raise ValidationError("Recipe requires at least one ingredient")
```

#### Qt-Specific Patterns:

```python
# Qt workaround: Force style refresh after dynamic property change
widget.style().unpolish(widget)
widget.style().polish(widget)
```

#### Performance Optimizations:

```python
# Performance optimization: Cache expensive database query results
if not self._cache_loaded:
    self._ingredient_cache = self._load_ingredients_from_db()
    self._cache_loaded = True
```

#### Architecture Decisions:

```python
# MVVM pattern: Delegate business logic to ViewModel instead of handling in View
self.view_model.validate_and_save_recipe(form_data)
```

#### Non-Obvious Code:

```python
# Convert Qt enum to string for database storage
status_value = int(self.status_combo.currentData(Qt.UserRole))
```

### 4. Module-Level Documentation

Add or enhance module docstrings:

```python
"""Module for handling recipe creation and management in the MealGenie application.

This module contains the main UI components for the add recipe workflow,
including form validation, ingredient management, and integration with
the recipe service layer.

Classes:
    AddRecipes: Main view for recipe creation workflow
    RecipeForm: Form component for basic recipe information
    IngredientsCard: Container for managing recipe ingredients

Functions:
    helper_function: Brief description of standalone functions

Dependencies:
    - RecipeViewModel: Business logic coordination
    - RecipeService: Core recipe operations
    - IngredientService: Ingredient search and validation
"""
```

## Critical Preservation Rules

### 1. Functionality Preservation

- **NEVER** change any method signatures or class interfaces
- **NEVER** modify import statements or add new imports
- **NEVER** alter the logic flow or control structures
- **NEVER** change variable names or assignment patterns
- **NEVER** modify signal connections or Qt-specific code
- **NEVER** change exception handling or error recovery logic

### 2. Code Structure Preservation

- **NEVER** reorder methods or reorganize class structure
- **NEVER** change indentation levels or code formatting
- **NEVER** alter existing comments (only add new ones)
- **NEVER** modify existing docstrings (only add missing ones)
- **NEVER** change line breaks or whitespace patterns

### 3. MealGenie-Specific Preservation

- **NEVER** modify the MVVM architecture patterns
- **NEVER** change layer boundaries or import hierarchies
- **NEVER** alter existing error handling or validation logic
- **NEVER** modify signal/slot connections or UI event handling
- **NEVER** change database operations or service calls

## Documentation Focus Areas

### 1. Missing Docstrings

Identify and improve:

- Add docstrings to classes and methods that lack documentation
- Revise existing docstrings to meet Google-style standards
- Enhance existing comments to be more descriptive and helpful
- Standardize documentation format across the entire file
- Add missing inline comments for complex logic sections

### 2. Complex Logic Sections

Add comments to explain:

- Mathematical calculations or algorithms
- Complex conditional logic or nested statements
- Performance-critical code sections
- Workarounds or non-standard patterns
- Integration points between components

### 3. Business Logic

Document:

- Validation rules and business constraints
- Data transformation logic
- User workflow steps
- Domain-specific operations
- Error conditions and recovery strategies

### 4. Technical Implementation

Explain:

- Qt-specific patterns or workarounds
- Threading or asynchronous operations
- Resource management and cleanup
- Caching strategies
- Database query optimizations

## Quality Standards

### 1. Clarity and Accuracy

- Use clear, concise language
- Explain the "why" not just the "what"
- Include context about the broader system
- Provide examples for complex operations
- Use proper technical terminology

### 2. Completeness

- Document all parameters and return values
- List all possible exceptions
- Explain side effects and state changes
- Document dependencies and assumptions
- Include usage examples where helpful

### 3. Consistency

- Follow the same style throughout the file
- Use consistent terminology and phrasing
- Match the existing code's tone and style
- Align with MealGenie's domain language
- Maintain professional documentation standards

## Output Requirements

Provide the complete file with:

- All missing docstrings added using Google style
- Helpful inline comments for complex logic
- Enhanced module documentation
- Preserved functionality and structure
- Professional documentation quality

Focus on making the code self-documenting and easier for other developers to understand while maintaining the exact same functionality and behavior.
