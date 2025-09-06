---
description: Create new features following MealGenie MVVM architecture with proper file structure, naming conventions, and integration patterns
argument-hint: <feature-name> - <feature-description>
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# Create Feature: $ARGUMENTS

Please create a new feature for the MealGenie application following the established MVVM architecture patterns and project conventions.

## Feature Analysis

### 1. Parse Feature Requirements
Extract from the command arguments:
- **Feature Name**: The main identifier (e.g., "Notification Manager")
- **Feature Description**: Purpose and scope (e.g., "manage toast notifications across various views")
- **Feature Type**: Determine the category:
  - **UI Component**: Reusable UI elements (components, widgets, dialogs)
  - **Manager/Service**: Cross-cutting concerns (notifications, navigation, data)
  - **View Feature**: New views or major view enhancements
  - **Core Business Logic**: Models, repositories, services for business rules
  - **Utility**: Helper functions and utilities

### 2. Architecture Planning
Based on the MealGenie structure, plan file locations:
- **UI Components**: `app/ui/components/` or `app/ui/managers/`
- **ViewModels**: `app/ui/view_models/`
- **Views**: `app/ui/views/`
- **Core Services**: `app/core/services/`
- **Core Models**: `app/core/models/`
- **Repositories**: `app/core/repositories/`
- **DTOs**: `app/core/dtos/`
- **Utilities**: `app/core/utils/` or `app/ui/utils/`

## Implementation Strategy

### 3. File Structure Creation
Create the appropriate files based on feature type:

**For Manager/Service Features (like Notification Manager):**
```
app/ui/managers/notifications/
├── __init__.py
├── notification_manager.py
├── notification_types.py
└── toast_widget.py
```

**For View Features:**
```
app/ui/views/feature_name/
├── __init__.py
├── feature_name_view.py
└── components/
    └── feature_specific_component.py
app/ui/view_models/
└── feature_name_view_model.py
```

**For Core Business Features:**
```
app/core/models/
└── feature_model.py
app/core/dtos/
└── feature_dto.py
app/core/services/
└── feature_service.py
app/core/repositories/
└── feature_repository.py
```

### 4. Code Generation Guidelines

**Follow MealGenie Patterns:**
- Use established naming conventions (snake_case files, PascalCase classes)
- Apply proper header comments with the dash style
- Implement MVVM separation (Views ↔ ViewModels ↔ Core Services)
- Respect import boundaries (UI never imports app.core directly except through ViewModels)
- Use existing base classes where appropriate (ScrollableNavView, Card, etc.)

**Standard Imports Structure:**
```python
# ── Imports ────────────────────────────────────────────────────────────────────────────────────────────────────────────────
# Standard library imports
from typing import Optional, Dict, List

# PySide6 imports
from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtWidgets import QWidget

# Project imports
from app.style import Theme, Qss
from app.ui.components.base import BaseComponent
# ... other project imports
```

**Class Structure Template:**
```python
class FeatureName(BaseClass):
    """Brief description of the feature's purpose.

    Longer description explaining the feature's role in the application,
    its main responsibilities, and how it integrates with other components.
    """

    # ── Signals ────────────────────────────────────────────────────────────────────────────────────────────────────────────
    feature_signal = Signal(str)

    # ── Initialization ─────────────────────────────────────────────────────────────────────────────────────────────────────
    def __init__(self, parent=None):
        super().__init__(parent)
        self._initialize_feature()

    # ── Public Interface ───────────────────────────────────────────────────────────────────────────────────────────────────
    def public_method(self):
        """Public method following established patterns."""
        pass

    # ── Private Implementation ─────────────────────────────────────────────────────────────────────────────────────────────
    def _private_method(self):
        """Private implementation details."""
        pass
```

### 5. Integration Requirements

**Register with Theme System:**
```python
# Register with Theme API for Material3 styling
Theme.register_widget(self, Qss.FEATURE_NAME)
```

**Connect to Existing Systems:**
- Navigation integration (if applicable)
- Signal/slot connections to existing managers
- Service registration in dependency injection
- Database model registration (if applicable)

**Error Handling:**
```python
from app.core.utils.error_utils import log_and_handle_exception

try:
    # Feature logic
    pass
except Exception as e:
    log_and_handle_exception(e, context="FeatureName")
```

### 6. Documentation Requirements

**Add Comprehensive Docstrings:**
- Class-level documentation explaining purpose and integration
- Method documentation with parameters, returns, and examples
- Signal documentation explaining when they're emitted
- Property documentation for complex properties

**Integration Documentation:**
Create or update relevant documentation:
- Add usage examples in docstrings
- Document any new configuration requirements
- Note integration points with existing features

## Implementation Process

### Step 1: Feature Analysis and Planning
1. Parse the feature name and description
2. Determine the appropriate feature type and architecture layer
3. Plan file structure and integration points
4. Identify existing patterns to follow

### Step 2: File Generation
1. Create directory structure if needed
2. Generate base files with proper imports and class structure
3. Implement core functionality following MealGenie patterns
4. Add proper error handling and logging

### Step 3: Integration and Testing
1. Register with appropriate systems (Theme, Navigation, DI)
2. Create integration points with existing features
3. Add proper signal connections
4. Implement initialization and cleanup

### Step 4: Documentation and Polish
1. Add comprehensive docstrings
2. Include usage examples
3. Document integration requirements
4. Apply consistent formatting and style

## Output Requirements

Provide:
1. **Complete file structure** with all necessary files
2. **Fully implemented code** following MealGenie patterns
3. **Proper integration** with existing systems
4. **Comprehensive documentation** with docstrings and comments
5. **Usage instructions** for integrating the feature

The generated feature should be production-ready and follow all established architectural patterns, naming conventions, and coding standards of the MealGenie project.
