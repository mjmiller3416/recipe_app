# Recipe App Advanced Filter & Sort System Implementation

## Context & Requirements

I need you to implement a comprehensive filtering and sorting system for my recipe application. The app uses Python, PySide6, SQLite, SQLAlchemy, Pydantic with MVVM architecture.

### Current Architecture
- **Framework**: PySide6 with MVVM pattern
- **Database**: SQLite with SQLAlchemy ORM
- **Models**: Pydantic for data validation
- **Migration**: Alembic for schema changes
- **Settings**: JSON-based user settings persistence

### Recipe Model Structure
```python
class Recipe(Base):
    __tablename__ = "recipe"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    recipe_name: Mapped[str] = mapped_column(String, nullable=False)
    recipe_category: Mapped[str] = mapped_column(String, nullable=False)
    meal_type: Mapped[str] = mapped_column(String, default="Dinner", nullable=False)
    diet_pref: Mapped[Optional[str]] = mapped_column(String, default="None", nullable=True)
    total_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    servings: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    directions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reference_image_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    banner_image_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)
```

## Feature Requirements

### 1. Filter System
**Filter Categories:**
- Recipe Category (multi-select)
- Meal Type (multi-select)
- Diet Preferences (multi-select)
- Total Time (range slider: 0-240 minutes)
- Servings (range slider: 1-20 servings)
- Favorites (toggle)

**Filter Behavior:**
- All filters use AND logic (stacked/combined)
- Filters persist across sessions via `user_settings.json`
- "Reset all filters" functionality
- Filter pills display active filters with remove capability
- Instant application when filters change

### 2. Sort System
**Sort Options:**
- Recipe Name (A-Z / Z-A)
- Date Added (Newest ⬆️ / Oldest ⬇️)
- Favorites (toggle to show only favorites)

**Sort Behavior:**
- Default: Recipe name A-Z
- Instant application when changed
- Persists across sessions
- Ascending/descending options

### 3. UI Design
**Top Bar Layout:**
- "Filter" button (expands sidebar filter panel)
- Sort dropdown/controls
- Active filter pills with remove buttons

**Filter Sidebar:**
- Fly-out panel design
- Collapsible sections for each filter category
- Range sliders for numeric values
- Multi-select checkboxes for categories
- "Reset All" button

### 4. Performance Requirements
**Critical Performance Goals:**
- Current issue: 50+ recipes take 30+ seconds to load
- Target: Optimize for 100+ recipes
- Eliminate UI tear-down/rebuild pattern
- Implement efficient data loading and filtering

**Performance Strategies Required:**
- Database-level filtering (SQLAlchemy queries)
- UI virtualization/lazy loading if needed
- Efficient data binding patterns
- Caching strategies for filter options

### 5. Settings Persistence
**User Settings Structure (user_settings.json):**
```json
{
  "view_recipes": {
    "filters": {
      "recipe_category": [],
      "meal_type": [],
      "diet_pref": [],
      "total_time": {"min": 0, "max": 240},
      "servings": {"min": 1, "max": 20},
      "favorites_only": false
    },
    "sort": {
      "field": "recipe_name",
      "order": "asc"
    }
  }
}
```

## Implementation Instructions

### 1. Architecture Compliance
- Follow existing MVVM pattern strictly
- Create appropriate ViewModels for filter/sort logic
- Use existing repository pattern for data access
- Maintain separation of concerns

### 2. Database Optimization
- Implement efficient SQLAlchemy queries
- Use database-level filtering instead of Python filtering
- Create indexes if necessary for performance
- Implement query result caching where appropriate

### 3. UI Components Needed
- FilterSidebar component (fly-out panel)
- FilterPill component (removable filter indicators)
- RangeSlider component (for time/servings)
- MultiSelectFilter component (for categories)
- SortControls component

### 4. File Structure Integration
Place new files following the existing structure:
- ViewModels: `app/ui/view_models/`
- Components: `app/ui/components/`
- Services: `app/core/services/`
- Models/DTOs: `app/core/dtos/`

### 5. Key Integration Points
- Integrate with existing `view_recipes` view
- Update existing RecipeRepository for filtering
- Extend user settings management
- Connect to existing recipe data flow

### 6. Testing Requirements
- Unit tests for filter logic
- Integration tests for database queries
- UI tests for component interactions
- Performance tests for large recipe sets

## Specific Technical Requests

1. **Create a comprehensive FilterService** that handles all filter logic and persistence
2. **Implement efficient database queries** that combine all active filters
3. **Design reusable UI components** following existing patterns
4. **Optimize data loading** to eliminate the current performance bottleneck
5. **Ensure proper error handling** and edge cases
6. **Implement proper data validation** using existing Pydantic patterns

## Success Criteria

- ✅ Filters apply instantly without UI rebuild
- ✅ 100+ recipes load and filter in under 3 seconds
- ✅ All filter states persist across app restarts
- ✅ UI matches existing design patterns
- ✅ Code follows existing architecture conventions
- ✅ Comprehensive test coverage
- ✅ Clean, maintainable, well-documented code

Please analyze the existing codebase structure, implement this filter/sort system with proper performance optimization, and ensure it integrates seamlessly with the current MVVM architecture. Focus heavily on the performance requirements as this is a critical pain point.
