# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MealGenie is a PySide6-based meal planning application with a clean architecture using MVVM pattern. The application follows a layered architecture with clear separation between UI, business logic, and data access layers.

## Technology Stack

- **Frontend**: PySide6 (Qt6) with custom UI components
- **Backend**: SQLAlchemy ORM with SQLite database
- **Architecture**: MVVM (Model-View-ViewModel) pattern
- **Testing**: pytest, pytest-qt, factory-boy, faker
- **Database Migrations**: Alembic
- **Dependencies**: Defined in requirements.txt

## Architecture

```
app/
├── core/                    # Business logic layer
│   ├── database/           # Database configuration and migrations
│   ├── models/             # SQLAlchemy ORM models
│   ├── repositories/       # Data access layer
│   ├── services/           # Business logic services
│   ├── dtos/               # Data transfer objects
│   └── utils/              # Core utilities
├── ui/                     # Presentation layer
│   ├── main_window.py      # Main application window
│   ├── components/         # Reusable UI components
│   ├── views/              # Application views
│   ├── view_models/        # ViewModels for MVVM
│   ├── managers/           # UI managers (navigation, themes, etc.)
│   └── utils/              # UI utilities
├── style/                  # Theming and styling
└── config/                 # Configuration files
```

### Key Architecture Principles

- **MVVM Pattern**: Views bind to ViewModels, ViewModels interact with Services
- **Layer Separation**: UI components should not directly import core services
- **Repository Pattern**: Data access is abstracted through repository classes
- **Service Layer**: Business logic is centralized in service classes
- **Factory Pattern**: Use factory-boy for test data generation

## Import Guidelines

### Prohibited Imports
- UI components MUST NOT import from `app.core.services.*` directly
- Use ViewModels to mediate between UI and core services
- Views should only import: components, view_models, utils, and Qt modules

### Allowed Import Patterns
- ViewModels → Services (✓)
- Views → ViewModels (✓)  
- Views → Components (✓)
- Services → Repositories (✓)
- Any layer → `app.core.utils.*` (✓) - Global utilities available to all layers
- UI components → `app.ui.utils.*` (✓) - UI-specific utilities

### Utility Layer Guidelines
- **`app/core/utils/`**: Global utilities available to all application layers (UI, Core, etc.)
- **`app/ui/utils/`**: UI-specific utilities, only for use within the presentation layer
- UI components CAN import from `app/core/utils/` as these are general-purpose utilities
- Core components should NOT import from `app/ui/utils/` as these are UI-specific

## ViewModel Patterns

All ViewModels should:
- Inherit from `BaseViewModel` in `app/ui/view_models/base_view_model.py`
- Handle service interactions and emit signals for UI updates
- Implement business logic validation before calling services
- Use dependency injection pattern for service dependencies

Example structure:
```python
class ExampleViewModel(BaseViewModel):
    def __init__(self, service: ExampleService):
        super().__init__()
        self._service = service
```

## Navigation Patterns

### Route Usage
- Routes defined in `app/ui/managers/navigation/routes.py`
- Use NavigationService for programmatic navigation
- Route patterns: `/dashboard`, `/recipes/browse`, `/recipes/browse/selection`

### View Registration
- All views registered in `app/ui/managers/navigation/registry.py`
- Complex views have dedicated directories under `app/ui/views/`

## Common Pitfalls to Avoid

1. **Direct Service Imports in UI**: Never import services directly in views
2. **Missing ViewModel Mediation**: Always use ViewModels between Views and Services  
3. **Incorrect Route Patterns**: Use exact route strings from routes.py
4. **Test Marker Misuse**: Use appropriate pytest markers for each layer
5. **Database Direct Access**: Always use Repository pattern, never direct ORM calls in services

## Debugging Tools

### UI Debugging
```bash
# Keep Qt widgets open for inspection
pytest --qt-keep-widgets-open

# Debug specific UI components
python main.py --test
```

### Performance Profiling
```bash
# Run performance tests
pytest -m slow

# Database query analysis
python manage.py db status
```

## Common Development Commands

### Running the Application

```bash
# Standard run
python main.py

# Test mode with test harness
python main.py --test

# Import recipes from CSV
python main.py --import-recipes

# Reset application state
python main.py --reset
```

### Database Management

```bash
# Apply database migrations
python manage.py db migrate

# Seed database with mock data
python manage.py db seed --recipes 25 --clear --images

# Reset database completely
python manage.py db reset --confirm --seed

# Check database status
python manage.py db status
```

### Testing

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m ui            # UI tests only
pytest -m models        # Model layer tests
pytest -m repositories  # Repository layer tests
pytest -m services      # Service layer tests

# Run tests with coverage
pytest --cov=app --cov-report=html

# Run slow performance tests
pytest -m slow

# Skip UI tests (for CI/CD)
pytest --no-run-ui
```

### Development Tools

```bash
# Check Python version (requires 3.13+)
python --version

# Install dependencies
pip install -r requirements.txt

# Run single test file
pytest _tests/unit/core/models/test_recipe.py

# Debug UI tests with widgets kept open
pytest --qt-keep-widgets-open
```

## Important Files and Directories

- `main.py` - Application entry point with command-line options
- `manage.py` - Management CLI with database and development commands
- `alembic.ini` - Database migration configuration
- `pytest.ini` - Test configuration with markers and options
- `_tests/` - Comprehensive test suite with fixtures and factories
- `app/core/database/app_data.db` - SQLite database file
- `app/style/theme/` - Application theming and QSS stylesheets

## Development Workflow

1. **Database Setup**: Run migrations and seed data using `manage.py db` commands
2. **Testing**: Use pytest with appropriate markers for the layer being tested
3. **UI Development**: Follow MVVM pattern with ViewModels mediating between Views and Services
4. **Data Access**: Use Repository pattern for all database operations
5. **Business Logic**: Implement in Service classes, not in UI components

## Key Components

### Models (app/core/models/)
- `Recipe` - Core recipe entity with ingredients and metadata
- `Ingredient` - Ingredient master data
- `RecipeIngredient` - Many-to-many relationship with quantities
- `MealSelection` - Meal planning entries
- `ShoppingItem` - Shopping list management

### Services (app/core/services/)
- `RecipeService` - Recipe CRUD and business logic
- `IngredientService` - Ingredient management
- `PlannerService` - Meal planning functionality
- `ShoppingService` - Shopping list management

### UI Views (app/ui/views/)
- Each complex view has its own directory with related components
- Views follow MVVM pattern with corresponding ViewModels
- Navigation is managed through the navigation service

## Testing Guidelines

- Use factory-boy factories for test data creation
- Mark tests with appropriate pytest markers
- UI tests require `qtbot` and `qapp` fixtures
- Database tests use `db_session` fixture with automatic rollback
- Mock external dependencies in service tests
- Follow AAA pattern (Arrange, Act, Assert)

## Navigation System

The application uses a centralized navigation system:
- Routes are defined in `app/ui/managers/navigation/routes.py`
- Views are registered in `app/ui/managers/navigation/registry.py`
- Navigation service manages view transitions and history

## Performance Considerations

- Recipe browsing uses optimized repositories for large datasets
- UI components implement progressive rendering for performance
- Database queries use appropriate indexing and eager loading
- Test suite includes performance tests marked with `@pytest.mark.slow`