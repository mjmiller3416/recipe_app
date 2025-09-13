# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## MealGenie - Recipe Management Desktop Application

A PySide6-based desktop application for meal planning, recipe management, and shopping list generation.

## Common Development Commands

### Database Management
```bash
# Apply database migrations
python manage.py db migrate

# Seed database with mock data (25 recipes with images by default)
python manage.py db seed

# Reset database (clear all data)
python manage.py db reset --confirm

# Check database status
python manage.py db status
```

### Running the Application
```bash
# Main application
python main.py

# Test mode with development harness
python main.py --test

# Import recipes from CSV
python main.py --import-recipes
```

### Code Quality
```bash
# Run isort for import formatting
isort app/

# Run ruff linter (if installed)
ruff check app/

# Run tests (when implemented)
pytest
```

## Architecture Overview

### Core Structure
The application follows a layered architecture with clear separation of concerns:

- **`app/core/`**: Business logic layer
  - `models/`: SQLAlchemy ORM models (Recipe, Ingredient, MealSelection, ShoppingItem, etc.)
  - `repositories/`: Data access layer providing CRUD operations
  - `services/`: Business logic services coordinating between repos and UI
  - `dtos/`: Data transfer objects for clean data passing between layers
  - `utils/`: Shared utilities (image_utils, format_utils, validation_utils, etc.)
  - `database/`: Database configuration and Alembic migrations

- **`app/ui/`**: PySide6 presentation layer
  - `main_window/`: Main application window with title bar and navigation
  - `pages/`: Application pages (recipes, planner, shopping, settings)
  - `components/`: Reusable UI components
  - `services/`: UI-specific services (navigation, state management)
  - `dialogs/`: Modal dialogs for user interactions

- **`app/style/`**: Theming and styling
  - Material theme system with dark/light mode support
  - Custom QSS styles with placeholders
  - Theme controller for dynamic theming

### Database Architecture
- SQLAlchemy ORM with SQLite backend
- Alembic for migrations (configured in `alembic.ini`)
- Session management via `DatabaseSession` context manager
- Models use relationships for Recipe ↔ Ingredient ↔ RecipeIngredient associations

### Service Layer Pattern
Services coordinate between repositories and UI:
- `RecipeService`: Recipe CRUD, search, filtering
- `PlannerService`: Meal planning and selection management
- `ShoppingService`: Shopping list generation and management
- `IngredientService`: Ingredient management and parsing
- `SessionManager`: Application-wide state management

### UI Component Hierarchy
- `MainWindow` contains navigation and page stack
- Pages inherit from base classes providing common functionality
- Components use signals/slots for communication
- Navigation handled by `NavigationService` singleton

## Key Design Patterns

1. **Repository Pattern**: Clean data access abstraction
2. **Service Layer**: Business logic isolation from UI
3. **DTO Pattern**: Clean data contracts between layers
4. **Singleton Pattern**: For app-wide services (Navigation, Session)
5. **Context Managers**: For database session management

## Development Guidelines

### Error Handling Philosophy
- **Fail fast** for internal logic errors - raise exceptions immediately
- **Boundary-only** try/except for external operations (DB, I/O, API calls)
- Log errors centrally rather than scattered try/except blocks

### Code Style
- Follow PEP 8 with 110 character line length
- Use isort configuration in `.isort.cfg`
- Prefer explicit over clever code
- Names should be self-documenting

### Utility Usage
Always check `app/core/utils/` for existing helpers before implementing new functionality:
- `image_utils.py`: Image loading, caching, placeholder generation
- `format_utils.py`: Text formatting, measurements, ingredient parsing
- `validation_utils.py`: Input validation helpers
- `conversion_utils.py`: Unit conversions
- `text_utils.py`: Text processing utilities

### QSS and Theming
- Use placeholder syntax for dynamic theming: `{{primary}}`, `{{surface}}`, etc.
- Material theme colors defined in `app/style/theme/material-theme.json`
- Components should respect theme changes via signals

## Safety Rails

1. **Database Operations**: Always use context managers for sessions
2. **Image Loading**: Use cached image utilities to prevent memory issues
3. **Error States**: Provide meaningful user feedback, not stack traces
4. **State Management**: Use SessionManager for app-wide state consistency
5. **Navigation**: Always use NavigationService for page transitions

## Testing Approach
- Test harness available via `python main.py --test`
- Mock data generation in `_scripts/mock_data.py`
- Database can be reset to clean state for testing
- QSS inspector available for UI debugging (`_dev_tools/qss_inspector.py`)