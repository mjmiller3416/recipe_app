---
description: Reorganize Python files with proper header comments, logical grouping, docstrings, and code documentation
argument-hint: @<file-path>
allowed-tools: Read, Edit
---

# Organize File: $ARGUMENTS

Please reorganize and improve the Python file $ARGUMENTS by applying consistent structure, header comments, docstrings, and inline documentation.

## Organization Strategy

### 1. File Structure Analysis
- Read and understand the current file structure and purpose
- Identify the main classes, functions, and logical groupings
- Determine the appropriate organization pattern based on file type:
  - **Views/UI Components**: Imports → Form Classes → Container Classes → Main View → Event Handlers → Utility Methods
  - **ViewModels**: Imports → Class Definition → Initialization → Public Methods → Private Methods → Event Handlers
  - **Services**: Imports → Class Definition → Public Interface → Private Implementation → Utility Methods
  - **Models**: Imports → Class Definition → Properties → Methods → Validation → Serialization

### 2. Header Comment Style
Apply consistent header comments using the style from add_recipes.py:
```python
# ── Section Name ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
```

**Standard Section Headers:**
- `# ── Imports ──` (for import statements)
- `# ── Constants ──` (for module-level constants)
- `# ── Forms ──` (for form classes in UI files)
- `# ── Containers ──` (for container/layout classes)
- `# ── View ──` (for main view class)
- `# ── ViewModels ──` (for ViewModel classes)
- `# ── Services ──` (for service classes)
- `# ── Models ──` (for data model classes)
- `# ── UI Components ──` (for UI helper methods)
- `# ── Event Handlers ──` (for signal/event handling methods)
- `# ── Business Logic ──` (for core business methods)
- `# ── Validation ──` (for validation methods)
- `# ── Data Processing ──` (for data transformation methods)
- `# ── Utility Methods ──` (for helper/utility functions)
- `# ── Properties ──` (for property definitions)
- `# ── Lifecycle Methods ──` (for init, cleanup, etc.)

### 3. Method Organization Within Classes
Group methods logically with sub-headers:
```python
    # ── Initialization ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    def __init__(self):
        pass

    # ── Public Interface ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    def public_method(self):
        pass

    # ── Event Handlers ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    def _on_event(self):
        pass

    # ── Private Implementation ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    def _private_method(self):
        pass
```

## Documentation Improvements

### 4. Add Missing Docstrings
Add comprehensive docstrings following Google style to:
- All public classes and methods
- Complex private methods
- Methods with non-obvious behavior
- Methods with parameters or return values

**Docstring Format:**
```python
def method_name(self, param1: str, param2: int = None) -> bool:
    """Brief description of what the method does.

    Longer description if needed, explaining complex behavior,
    side effects, or important implementation details.

    Args:
        param1: Description of first parameter
        param2: Description of second parameter with default

    Returns:
        Description of return value and type

    Raises:
        SpecificException: When this specific error occurs

    Example:
        Basic usage example if helpful
    """
```

### 5. Add Inline Comments
Add helpful comments for:
- Complex logic or algorithms
- Non-obvious code sections
- Business rule implementations
- Qt-specific patterns or workarounds
- Performance optimizations
- Architecture decisions

**Comment Style:**
```python
# Performance optimization: lazy load to avoid startup delay
if not self._cache_loaded:
    self._load_data()

# Qt workaround: force style refresh after state change
self.style().unpolish(widget)
self.style().polish(widget)

# Business rule: always maintain at least one ingredient
if len(self.ingredients) <= 1:
    return
```

## Implementation Guidelines

### 6. Preserve Functionality
- **NEVER** change the actual logic or behavior of methods
- **NEVER** modify import statements unless they need to be grouped better
- **NEVER** change method signatures or class interfaces
- **NEVER** alter signal connections or Qt-specific code

### 7. Maintain MealGenie Architecture
- Respect the MVVM pattern and layer boundaries
- Keep UI concerns separate from business logic
- Maintain proper import hierarchy (UI never imports Core directly)
- Preserve existing architectural patterns

### 8. Code Quality Standards
- Ensure proper line length (under 88-100 characters when possible)
- Maintain consistent indentation and spacing
- Group related methods together logically
- Keep similar functionality near each other

## Organization Process

### Step 1: Structure Analysis
1. Read the entire file and understand its purpose
2. Identify main classes and their responsibilities
3. Map out the logical groupings needed
4. Plan the reorganization sequence

### Step 2: Apply Organization
1. Group imports and add header
2. Organize classes by logical hierarchy (forms → containers → main classes)
3. Within each class, group methods by purpose
4. Add appropriate header comments for each section

### Step 3: Add Documentation
1. Add docstrings to all public methods and classes
2. Add docstrings to complex private methods
3. Add inline comments for complex logic
4. Ensure all parameters and return values are documented

### Step 4: Final Review
1. Verify all functionality is preserved
2. Check that organization follows MealGenie patterns
3. Ensure consistent formatting throughout
4. Validate that docstrings are complete and helpful

## Output Requirements

Provide the complete reorganized file with:
- Clear section headers using the established comment style
- Logical grouping of all classes and methods
- Comprehensive docstrings for all applicable functions
- Helpful inline comments for complex code
- Preserved functionality and interfaces
- Consistent formatting and style

Focus on making the code more maintainable and self-documenting while preserving all existing functionality.
