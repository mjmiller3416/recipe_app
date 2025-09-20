# Dashboard Development Prompt for Recipe App

## Context

I'm developing a Dashboard view for my Recipe App. The application is built with PySide6 and follows an established architecture with existing components and services. The Dashboard should serve as the main hub, providing quick access to core features and displaying relevant information about meal planning, recipes, and shopping lists.

## Current Application Structure

- **Base View**: All views inherit from `BaseView` with scrollable content
- **Components Available**: `Card`, `ActionCard`, `RecipeCard` (Small/Medium/Large), `Button`, `ToolButton`
- **Services Available**: `RecipeService`, `PlannerService`, `ShoppingService`, `SettingsService`
- **Navigation**: Handled through `NavigationService` with `switch_to()` method
- **Database Models**: `Recipe`, `MealSelection`, `ShoppingItem`

## Development Requirements

### Step 1: Update Dashboard Base Structure

First, update `app/ui/views/dashboard/dashboard.py` to remove the placeholder content and prepare for the new dashboard features. Keep the existing imports and add necessary ones for the new components.

### Step 2: Implement Quick Actions Section

Create a Quick Actions card with 4 primary action buttons:

- "Plan This Week" → Navigate to `meal_planner`
- "Add Recipe" → Navigate to `add_recipe`
- "Shopping List" → Navigate to `shopping_list`
- "Browse Recipes" → Navigate to `browse_recipes`

**Requirements:**

- Use `ActionCard` or `Card` with custom buttons
- Each button should have an icon and text
- Buttons should use the existing navigation service
- Layout buttons in a 2x2 grid or horizontal row
- Apply proper spacing and styling

### Step 3: Implement This Week's Meal Plan Preview

Create a preview section showing the current week's planned meals:

**Requirements:**

- Use `PlannerService` to load saved meal IDs
- Display up to 3-5 meals using `SmallRecipeCard`
- Show day labels (e.g., "Monday", "Tuesday")
- Include "View Full Plan" button to navigate to `meal_planner`
- Handle empty state when no meals are planned
- Use horizontal layout with `FlowLayout` if needed

### Step 4: Implement Shopping List Summary

Create a summary card showing shopping list status:

**Requirements:**

- Use `ShoppingService` to get shopping list data
- Show total item count
- Display 3-5 categories with item counts
- Include "View Full List" button
- Show "List is empty" state when appropriate
- Consider using mini `CollapsibleCategory` or simple list

### Step 5: Implement Recent Recipes Section

Create a carousel/grid of recently added recipes:

**Requirements:**

- Use `RecipeService.list_filtered()` with sort by `created_at`
- Display 4-6 recipes using `MediumRecipeCard`
- Include "View All" button that navigates to `browse_recipes`
- Use `FlowLayout` for responsive grid
- Handle empty state for new users

### Step 6: Implement Statistics Cards

Create informational cards showing recipe collection stats:

**Requirements:**

- Total recipes count
- Favorites count
- Recipes added this week
- Average cooking time
- Use `InfoCard` or create mini stat cards
- Layout in horizontal row
- Pull data from `RecipeService`

### Step 7: Layout Composition

Arrange all sections using existing layout utilities:

**Requirements:**

- Use `create_two_column_layout` where appropriate
- Follow spacing patterns from other views
- Ensure responsive behavior
- Maintain visual hierarchy (most important at top)

**Suggested layout structure:**

```python
def _build_ui(self):
    # Quick Actions (full width)
    # Stats Cards (full width)
    # Two columns: Meal Preview | Shopping Summary
    # Recent Recipes (full width)
```

### Step 8: Connect Services and Handle State

Implement data loading and state management:

**Requirements:**

- Load data in `__init__` or `showEvent`
- Handle loading states gracefully
- Implement refresh mechanism when returning to dashboard
- Add error handling for service calls
- Cache data where appropriate to improve performance

### Step 9: Polish and Optimize

Final improvements:

**Requirements:**

- Add loading indicators if data fetching is slow
- Implement smooth transitions/animations using `Animator`
- Ensure consistent styling with other views
- Add tooltips for additional context
- Test with empty states (no recipes, no meals, etc.)

## Code Style Guidelines

- Follow existing patterns in the codebase
- Use existing utility functions from `app/ui/utils`
- Maintain consistent naming conventions (e.g., `_create_*` for UI building methods)
- Add debug logging using `DebugLogger`
- Handle exceptions gracefully
- Add docstrings for new methods

## Testing Checklist

- [ ] Dashboard loads without errors
- [ ] All buttons navigate correctly
- [ ] Data displays accurately from services
- [ ] Empty states show appropriate messages
- [ ] Layout responds well to window resizing
- [ ] No memory leaks or performance issues
- [ ] Consistent styling with rest of application

## Example Code Structure to Follow

```python
class Dashboard(BaseView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Dashboard")

        # Initialize services
        self.recipe_service = RecipeService()
        self.planner_service = PlannerService()
        self.shopping_service = ShoppingService()

        # Initialize data
        self._load_dashboard_data()

        # Build UI
        self._build_ui()

    def _build_ui(self):
        self._create_quick_actions()
        self._create_stats_section()
        self._create_main_content()
        # etc...

    def _load_dashboard_data(self):
        """Load all necessary data for dashboard display"""
        pass

    def showEvent(self, event):
        """Refresh dashboard when shown"""
        super().showEvent(event)
        self._refresh_dashboard()
```

## Deliverables

- Updated `dashboard.py` with all new features
- Any new utility functions needed
- Documentation of any new patterns introduced
- List of any additional dependencies or imports needed

Please develop this Dashboard view step by step, ensuring each feature is properly integrated with the existing application architecture. Start with Step 1 and proceed through each step sequentially.
