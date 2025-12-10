# AGENTS.md

This file provides guidance when working with code in this repository.

## Project Overview
MealGenie is a meal planning desktop application built with PySide6 (Qt) and the Fluent design system. It provides recipe management, meal planning, and shopping list features.

## Development Commands

### Application
```bash
# Run the main application
python main.py

# Run in test mode (launches test harness)
python main.py --test

# Import recipes from CSV
python main.py --import-recipes
```

### Database Management
```bash
# Apply database migrations
python manage.py db migrate

# Seed database with mock data
python manage.py db seed                    # 25 recipes with images
python manage.py db seed --recipes 50       # 50 recipes
python manage.py db seed --no-images        # Without images
python manage.py db seed --clear            # Clear existing recipes first

# Reset database
python manage.py db reset --confirm         # Skip confirmation
python manage.py db reset --seed --images   # Reset and add sample data

# Check database status
python manage.py db status
```

### Testing
```bash
# Run tests (note: tests directory doesn't currently exist)
pytest
```

## Architecture Overview

### Core Structure
The application follows a layered architecture with clear separation of concerns:

- **UI Layer** (`app/ui/`): PySide6/Qt-based GUI components
  - `main_window/`: Main application window with custom titlebar and sidebar
  - `views/`: Application pages (meal planner, shopping list, etc.)
  - `components/`: Reusable UI components (buttons, dialogs, widgets)
  - `services/`: UI-specific services (navigation, state management)

- **Core Layer** (`app/core/`):
  - `models/`: SQLAlchemy ORM models (Recipe, Ingredient, MealSelection, etc.)
  - `repositories/`: Data access layer for database operations
  - `services/`: Business logic (recipe_service, planner_service, shopping_service)
  - `dtos/`: Data transfer objects for passing data between layers
  - `utils/`: Shared utilities (conversion, formatting, validation)

- **Style System** (`app/style/`):
  - Custom theme controller supporting Material Design color system
  - Animation system for window and component animations
  - Icon management with SVG support
  - QSS-based styling with theme variables

### Database
- SQLite database at `app/core/database/app_data.db`
- Alembic for migrations (`app/core/database/migrations/`)
- Session management via `DatabaseSession` context manager

### Key Design Patterns
- **Repository Pattern**: All database operations go through repository classes
- **Service Layer**: Business logic separated from UI and data access
- **DTO Pattern**: Clean data transfer between layers
- **Singleton Services**: Settings and session management use singleton pattern
- **Navigation Service**: Centralized page routing and management

## Development Guidelines

### Error Handling Philosophy
- **Fail fast** for internal logic errors - raise exceptions immediately
- Use try/except **only** at boundaries (I/O, database, API calls, user input)
- Centralized logging via `DebugLogger` instead of scattered try/except blocks

### Code Style
- Prefer simplicity over cleverness
- Explicit, predictable code over "smart" solutions
- Meaningful names that make sense at 11 PM
- Reuse existing utilities from `app/core/utils/` or services
- Follow existing patterns in nearby code

### UI Development
- Components inherit from Fluent widgets (e.g., `FluentWindow`, `CardWidget`)
- Use `Theme` controller for consistent styling
- Animations handled via `WindowAnimator` and component animators
- Custom widgets go in `app/ui/components/widgets/`
- Complex composite widgets in `app/ui/components/composite/`

### Testing Approach
- Test harness available via `python main.py --test`
- Mock data generation via `manage.py db seed`
- Development tools in `_dev_tools/` (QSS inspector, debug logger, performance tracker)

## Common Tasks

### Adding a New View/Page
1. Create view class in `app/ui/views/<view_name>/`
2. Register with `NavigationService`
3. Add sidebar navigation item if needed
4. Follow existing view patterns for state management

### Working with Recipes
- Recipe model includes relationships to ingredients, history, and meal selections
- Use `RecipeService` for CRUD operations
- Images stored in `recipe_images/` directory
- Dual image path system (reference and user paths)

### Database Changes
1. Modify models in `app/core/models/`
2. Create migration: `alembic revision --autogenerate -m "description"`
3. Apply migration: `python manage.py db migrate`

## Review Standards
Refer to `review_guide.md` for detailed code review guidelines focusing on:
1. Bug fixes and conflict resolution
2. Boundary-only error handling
3. Reusing existing utilities
4. Maintaining clarity over premature optimization
