# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start Commands

### Application Launch
- `python main.py` - Launch the main application
- `python main.py --test` - Launch in test mode
- `python main.py --import-recipes` - Import recipes from CSV

### Essential Development Workflow
```bash
# Database setup/reset
python manage.py db migrate

# Run tests before changes
pytest

# Development with live reload
python main.py --test

# Code quality check
isort .
```

## Development Commands

### Database Management (via manage.py)
- `python manage.py db migrate` - Apply database migrations
- `python manage.py db seed` - Populate with mock data
- `python manage.py db reset` - Reset database completely
- `python manage.py db status` - Show database status

### Testing Commands
- `pytest` - Run all tests with default configuration
- `pytest _tests/unit/` - Run only unit tests
- `pytest _tests/integration/` - Run integration tests
- `pytest _tests/ui/` - Run UI tests (requires Qt application)
- `pytest -m "not slow"` - Skip slow tests for quick feedback
- `pytest -v --tb=short` - Verbose output with short tracebacks
- `pytest --durations=10` - Show slowest 10 tests

### Test Markers (defined in pytest.ini)
- `@pytest.mark.unit` - Unit tests for isolated components
- `@pytest.mark.integration` - Integration tests between layers
- `@pytest.mark.ui` - UI tests requiring Qt application
- `@pytest.mark.slow` - Tests that take longer than normal
- `@pytest.mark.database` - Tests requiring database setup

### Automation Scripts (`_scripts/`)
- `python _scripts/package_automation.py` - Automate package management
- `python _scripts/create_test_app.py` - Create test application instance
- `python _scripts/ui_converter.py` - Convert Qt Designer UI files to Python
- `python _scripts/mock_data.py` - Generate mock data for testing
- `python _scripts/modernize_database.py` - Update database schema
- `python _scripts/automatic_init.py` - Automated initialization
- `python _scripts/clear_pycache.py` - Clear Python cache files

### Development Tools
- `C:/Qt/6.8.2/msvc2022_64/bin/designer.exe` - Launch Qt Designer for UI design

### Code Quality
- `isort .` - Sort imports (configured in `.isort.cfg`)
- **Note**: Always run `isort .` before committing changes

## Architecture Overview

**MealGenie** is a Python desktop recipe management application built with **PySide6** (Qt6) and **SQLAlchemy 2.0**, following a layered clean architecture pattern with strict separation of concerns.

### 🏗️ Core Architecture Principles

1. **Layered Architecture**: Core → UI with clear dependency direction
2. **Separation of Concerns**: Business logic separated from UI presentation
3. **Repository Pattern**: Data access abstraction layer
4. **View-Model Pattern**: UI data binding and presentation logic
5. **Manager Pattern**: Complex UI state management and coordination

### 📁 Project Structure
```
app/
├── core/              # 🔧 Business Logic Layer
│   ├── models/        # SQLAlchemy ORM models (Recipe, Ingredient, etc.)
│   ├── repositories/  # Data access layer (Repository pattern)
│   ├── services/      # Business logic services
│   ├── dtos/          # Data transfer objects
│   ├── database/      # Database config, migrations (Alembic)
│   └── utils/         # Core utilities and helpers
├── ui/                # 🎨 User Interface Layer  
│   ├── views/         # Application pages/screens (Dashboard, AddRecipes, etc.)
│   ├── components/    # Reusable UI components (buttons, cards, dialogs)
│   ├── managers/      # UI state management and complex operations
│   ├── view_models/   # Data binding and presentation logic
│   └── utils/         # UI utilities and helpers
├── style/             # 🎨 Theming system with Material Design 3
│   ├── theme/         # QSS stylesheets and theme definitions
│   └── icon/          # Icon management and utilities
├── config/            # ⚙️ Application configuration
│   └── paths/         # Path utilities and constants
└── assets/            # 📁 Static resources
    ├── icons/         # SVG icons and graphics
    ├── fonts/         # Custom fonts (Roboto, Montserrat, etc.)
    └── images/        # Application images

# Support Directories
_scripts/              # 🔧 Automation and utility scripts
_dev_tools/           # 🛠️ Development debugging tools
_data_files/          # 📊 User data, settings, generated assets
_tests/               # 🧪 Test suites (unit, integration, UI)
_docs/                # 📚 Documentation and project notes
```

### 🗄️ Database Architecture
- **SQLite** database at `app/core/database/app_data.db`
- **Alembic** migrations in `app/core/database/migrations/`
- Environment variables configured in `.env`
- **Core entities**: Recipe, Ingredient, RecipeIngredient, MealSelection, ShoppingItem
- **Factory-Boy** for test data generation with realistic faker data

### 🖥️ UI Framework Stack
- **Frameless window** using `qframelesswindow` for modern appearance
- **Component-based UI** with `PySide6-Fluent-Widgets` for enhanced components
- **Material Design 3** theming system with dynamic color schemes
- **Custom QSS stylesheets** for consistent visual design
- **Main application views**: 
  - Dashboard (overview and quick actions)
  - Add Recipes (recipe creation and editing)
  - View Recipes (recipe browsing and management)
  - Meal Planner (weekly meal planning)
  - Shopping List (generated from meal plans)
  - Settings (application preferences)

## 🏛️ Key Design Patterns

### 📊 Repository Pattern
- **Data Access Abstraction**: All database operations go through repository classes in `app/core/repositories/`
- **Service Coordination**: Services in `app/core/services/` orchestrate business logic and coordinate multiple repositories
- **Clean Separation**: UI layer never directly accesses database models

### 🎯 UI Architecture Patterns

#### **View-Model Pattern**
- **View Models** (`app/ui/view_models/`) handle data binding and presentation logic
- Separate UI concerns from business logic
- Transform core DTOs into UI-friendly formats

#### **Manager Pattern**
- **Managers** (`app/ui/managers/`) handle complex UI state management
- Coordinate operations across multiple components
- Manage application-wide UI state (navigation, themes, etc.)

#### **Component Composition**
- `MainWindow` orchestrates the application shell with title bar and sidebar
- Views managed via `QStackedWidget` for smooth page transitions
- Custom components extend base Qt widgets with consistent styling
- Reusable components in `app/ui/components/` promote DRY principles

### 🧪 Testing Strategy
```
_tests/
├── unit/           # Isolated component tests
├── integration/    # Cross-layer integration tests  
├── ui/            # Qt widget and UI interaction tests
├── core/
│   ├── models/    # ORM model tests
│   ├── repositories/ # Data access layer tests
│   └── services/  # Business logic tests
├── conftest.py    # Shared fixtures and test configuration
└── factories/     # Factory-Boy test data factories
```

**Key Testing Features:**
- **pytest-qt** for UI widget testing with Qt application context
- **In-memory SQLite** for fast, isolated database tests
- **Factory-Boy + Faker** for realistic test data generation
- **Comprehensive markers** for test categorization and selective execution

## 🛠️ Development Workflows

### 🗄️ Database Changes Workflow
```bash
# 1. Modify models in app/core/models/
# 2. Generate migration with descriptive message
alembic revision --autogenerate -m "add recipe rating system"

# 3. Review generated migration in app/core/database/migrations/versions/
# 4. Apply migration
python manage.py db migrate

# 5. Verify database status
python manage.py db status
```

### 🎨 UI Development Workflow
```bash
# 1. Design UI mockup (optional)
C:/Qt/6.8.2/msvc2022_64/bin/designer.exe

# 2. Convert any .ui files to Python
python _scripts/ui_converter.py

# 3. Follow the UI architecture layers:
```

**UI Development Steps:**
1. **Component Layer** (`app/ui/components/`) - Create reusable UI components
2. **View Model Layer** (`app/ui/view_models/`) - Handle data binding and presentation logic
3. **Manager Layer** (`app/ui/managers/`) - Manage complex UI state and operations
4. **View Layer** (`app/ui/views/`) - Integrate components into application screens
5. **Testing** - Write UI tests in `_tests/ui/` using pytest-qt

### 🚀 Feature Development Workflow
```bash
# 1. Plan the feature architecture
# - Identify required models, DTOs, repositories, services
# - Plan UI components and views needed

# 2. Core Layer (bottom-up approach)
# - Create/modify models in app/core/models/
# - Create DTOs in app/core/dtos/
# - Implement repository methods in app/core/repositories/
# - Add business logic in app/core/services/

# 3. UI Layer
# - Create UI components in app/ui/components/
# - Implement view models in app/ui/view_models/
# - Create managers if needed in app/ui/managers/
# - Integrate into views in app/ui/views/

# 4. Testing (write tests for each layer)
pytest _tests/core/models/     # Test new models
pytest _tests/core/repositories/  # Test repository methods
pytest _tests/core/services/   # Test business logic
pytest _tests/ui/             # Test UI components

# 5. Integration testing
pytest _tests/integration/    # Test cross-layer functionality
```

### 🏁 Pre-commit Quality Workflow
```bash
# Always run before committing:
isort .                    # Sort imports
pytest                     # Run all tests
python manage.py db status # Verify database state

# For comprehensive checks:
pytest -v --durations=10   # Detailed test results
pytest --tb=short         # Short error traces
```

### 🔧 Environment Setup (First Time)
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env       # Copy and configure .env file
# Edit .env with your database URL and API keys

# 3. Initialize database
python manage.py db migrate

# 4. Seed with test data (optional)
python manage.py db seed

# 5. Run setup script
./setup.sh                # Windows: setup.sh

# 6. Verify installation
python main.py --test
```

## 📁 Project Directory Reference

### 🎯 Key Directories
| Directory | Purpose | Key Contents |
|-----------|---------|--------------|
| `_scripts/` | Automation and utility scripts | `ui_converter.py`, `mock_data.py`, `clear_pycache.py` |
| `_dev_tools/` | Development debugging tools | Development utilities and debugging helpers |
| `_data_files/` | User data and generated assets | Settings, cached data, user-generated content |
| `_tests/` | Comprehensive test suites | Unit, integration, UI tests with pytest configuration |
| `_docs/` | Documentation and project notes | Architecture docs, development notes, guides |
| `app/` | Main application code | Core business logic and UI implementation |
| `.claude/` | Claude Code specific configuration | AI assistant configuration and settings |

### ⚙️ Configuration Files Reference
| File | Purpose | Key Settings |
|------|---------|--------------|
| `alembic.ini` | Database migration config | SQLAlchemy connection, migration paths |
| `pytest.ini` | Test framework config | Test markers, paths, pytest-qt settings |
| `.isort.cfg` | Import sorting rules | Code style consistency for imports |
| `.editorconfig` | Editor formatting standards | Indentation, line endings, encoding |
| `qt.conf` | Qt framework configuration | Qt library paths and settings |
| `requirements.txt` | Python dependencies | PySide6, SQLAlchemy, pytest, and all packages |
| `.env` | Environment variables | Database URLs, API keys (not in git) |

## 🤖 Claude Code Guidance

### 🏗️ Architecture Rules (CRITICAL)
1. **STRICT LAYER SEPARATION**: Core ↔ UI layers must not cross inappropriately
   - ❌ **NEVER** import UI modules in core layer
   - ✅ UI layer can import core (models, DTOs, services)
   - ✅ Use repositories for all data access
   - ✅ Use services to coordinate business logic

2. **UI PATTERN COMPLIANCE**:
   - Use **Managers** (`app/ui/managers/`) for complex UI state management
   - Use **View Models** (`app/ui/view_models/`) for data binding and presentation logic
   - Create reusable **Components** (`app/ui/components/`) following existing patterns

3. **TESTING REQUIREMENTS**: 
   - ✅ All new features must have tests at each layer
   - ✅ Use appropriate pytest markers (`@pytest.mark.unit`, `@pytest.mark.ui`, etc.)
   - ✅ Repository tests should use in-memory database
   - ✅ UI tests should use pytest-qt fixtures

### 🔧 Development Best Practices

#### **Before Starting Any Task:**
```bash
# Check current state
python manage.py db status
pytest -x --tb=short      # Quick test to ensure nothing is broken
```

#### **For New Features:**
1. **Plan Architecture**: Identify models, DTOs, repositories, services, UI components needed
2. **Bottom-Up Development**: Start with core layer, then UI layer
3. **Test Each Layer**: Write and run tests as you develop each component
4. **Integration Testing**: Test cross-layer functionality

#### **Code Quality Checklist:**
- [ ] Run `isort .` before committing
- [ ] All tests pass (`pytest`)  
- [ ] Follow existing code patterns and naming conventions
- [ ] UI components use consistent styling (QSS classes, Material Design colors)
- [ ] Database changes include migrations
- [ ] Documentation updated if API changes

#### **Use Available Tools:**
- **Scripts**: Leverage `_scripts/` for common tasks (UI conversion, mock data, etc.)
- **Dev Tools**: Use `_dev_tools/` for debugging and development assistance  
- **Documentation**: Check `_docs/` for project-specific patterns and decisions
- **Agents**: Delegate complex, multi-step tasks to specialized agents when appropriate

#### **Common Patterns to Follow:**
- **Error Handling**: Use consistent error handling patterns across layers
- **Logging**: Follow existing logging patterns for debugging
- **Configuration**: Use `app/config/` for app-wide configuration
- **Styling**: Use existing QSS classes and Material Design color schemes
- **Icons**: Use SVG icons from `app/assets/icons/` with consistent sizing

### 🚨 Critical Reminders
- **NEVER** create direct database connections in UI layer
- **ALWAYS** use DTOs for data transfer between layers  
- **MAINTAIN** consistent code style and import organization
- **TEST** thoroughly before considering any task complete
- **DOCUMENT** significant architectural decisions in `_docs/`
