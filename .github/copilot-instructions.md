# MealGenie AI Development Guide

## Project Architecture

**MealGenie** is a PySide6/Qt desktop recipe management application using the Fluent design system with a layered architecture. The codebase follows strict separation of concerns:

### Core Layers
- **UI Layer** (`app/ui/`): PySide6 views, components, and navigation
- **Core Layer** (`app/core/`): Business logic, database models, repositories, services
- **Style System** (`app/style/`): Theme controller with Material Design 3 theming

### Key Components
- **Navigation**: Centralized via `NavigationService` - all page routing goes through this singleton
- **Database**: SQLAlchemy with session management via `session_scope()` context manager in `session_manager.py`
- **Theming**: `Theme` singleton controller handles dynamic light/dark mode switching with Material Design colors
- **Development Tools**: `_dev_tools/` provides debug logging, test harness, and performance monitoring

## Essential Development Patterns

### Database Operations
```python
# ALWAYS use session_scope() context manager
from app.core.services.session_manager import session_scope
with session_scope() as session:
    recipe = session.query(Recipe).filter_by(id=recipe_id).first()
    # session commits automatically on success, rolls back on error
```

### Error Handling Philosophy
- **Fail fast** for internal logic errors - raise exceptions immediately
- Use try/except **only** at boundaries (I/O, database, API calls, user input)
- Centralized logging via `DebugLogger` instead of scattered try/except blocks

### UI Component Patterns
```python
# All views inherit from BaseView which provides scroll layout
class MyView(BaseView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()        # Required override
        self._connect_signals() # Optional override

# Use existing components from app/ui/components/widgets/
from app.ui.components.widgets.button import Button
button = Button("Save", Type.PRIMARY, Name.SAVE)
```

### Service Layer Usage
- Business logic lives in services (`app/core/services/`)
- Services use repositories for data access
- DTOs handle data transfer between layers
- Example: `RecipeService.create_recipe(recipe_dto)` → `RecipeRepo.save()`

## Development Workflows

### Running the Application
```bash
# Main application
python main.py

# Test mode with harness
python main.py --test

# Import recipes from CSV
python main.py --import-recipes
```

### Database Management
```bash
# Apply migrations
python manage.py db migrate

# Seed with mock data (25 recipes with images)
python manage.py db seed

# Custom seed options
python manage.py db seed --recipes 50 --no-images --clear

# Reset database with confirmation
python manage.py db reset --confirm --seed --images
```

### Development Tools
- **Test Harness**: `python main.py --test` launches interactive widget testing
- **Debug Logging**: Use `DebugLogger.log("message", "info")` throughout codebase
- **UI Converter**: `python _scripts/ui_converter.py` converts .ui files to Python
- **Qt Designer**: Available via VS Code task "Run QtDesigner"

## Project-Specific Conventions

### File Organization
- Private modules prefixed with `_` (e.g., `_dev_tools/`, `_scripts/`)
- UI views in `app/ui/views/` with supporting files like `_theme_settings_category.py`
- DTOs use Pydantic models with validation
- Utils in `app/core/utils/` follow strict dependency rules (no UI/service imports)

### Naming Conventions
- Database models: PascalCase classes, snake_case table names
- DTOs: Suffix with `DTO` (e.g., `RecipeCreateDTO`)
- Services: Suffix with `Service` (e.g., `RecipeService`)
- Repositories: Suffix with `Repo` (e.g., `RecipeRepo`)

### Theme System Integration
```python
# Components automatically inherit theme via QSS
from app.style.theme_controller import Theme
theme = Theme.instance()  # Singleton access
theme.theme_refresh.connect(self._on_theme_changed)  # React to theme changes
```

### State Management
- Settings handled via `SettingsService` singleton
- Navigation state managed by `NavigationService`
- Database sessions are stateless - always use `session_scope()`

## Integration Points

### External Dependencies
- **qfluentwidgets**: Fluent design components (use sparingly, prefer custom widgets)
- **SQLAlchemy**: ORM with Alembic migrations in `app/core/database/migrations/`
- **Pydantic**: DTO validation and serialization
- **Typer**: CLI interface in `manage.py`

### Cross-Component Communication
- Views communicate via `NavigationService.navigate_to(page_name)`
- Services emit signals when needed, but prefer direct method calls
- Use DTOs for data passing between layers (never pass SQLAlchemy models to UI)

## Key Files for Reference
- `app/ui/services/navigation_service.py` - Page routing and navigation
- `app/core/services/session_manager.py` - Database session management
- `app/style/theme_controller.py` - Theme and styling system
- `_dev_tools/debug_logger.py` - Centralized logging
- `app/ui/views/base.py` - Base view pattern for all pages
- `app/core/utils/README.md` - Utility module guidelines
