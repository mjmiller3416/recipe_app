MealGenie Application Architecture Summary

## Overview

MealGenie is a desktop recipe management and meal planning application built with PySide6 and SQLAlchemy 2.0, following a layered clean architecture pattern with strict separation of concerns and MVVM design patterns.

## Core Architecture Layers

### 🏗️ Core Layer (app/core/)

**Business Logic Layer** - Framework-agnostic domain logic with clean separation

- **Database (database/)** - SQLite database with Alembic migrations
  - `base.py` - Database configuration and session management
  - `db.py` - Database initialization and connection handling
  - `migrations/` - Alembic migration files and version control
- **Models (models/)** - SQLAlchemy ORM entities representing domain objects
  - `Recipe` - Core recipe entity with ingredients and metadata
  - `Ingredient` - Master ingredient catalog
  - `RecipeIngredient` - Many-to-many relationship with quantities
  - `MealSelection` - Meal planning and scheduling
  - `ShoppingItem` - Shopping list items and categorization
  - Additional models for recipe history, saved states, and shopping management
- **Repositories (repositories/)** - Data access abstraction layer
  - `recipe_repo.py` & `recipe_repo_optimized.py` - Recipe data access
  - `ingredient_repo.py` - Ingredient management
  - `planner_repo.py` - Meal planning data operations
  - `shopping_repo.py` - Shopping list data management
- **Services (services/)** - Business logic orchestration and domain rules
  - `recipe_service.py` - Recipe CRUD and business logic
  - `ingredient_service.py` - Ingredient management services
  - `planner_service.py` - Meal planning business logic
  - `shopping_service.py` - Shopping list management
  - `settings_service.py` - Application settings management
  - `ai_gen/` - AI-powered recipe generation services
  - `session_manager.py` - Application session state management
- **DTOs (dtos/)** - Data transfer objects for clean layer communication
  - Structured data containers for Recipe, Ingredient, Planner, and Shopping domains
- **Utils (utils/)** - Framework-agnostic shared utilities
  - Format, conversion, validation, image processing, and error handling utilities

### 🎨 UI Layer (app/ui/)

**Presentation Layer** - PySide6-based user interface following MVVM architecture

- **Views (views/)** - Application pages and screens organized by feature
  - `main_window.py` - Primary application window and layout
  - `dashboard.py` - Application home/dashboard view
  - `settings.py` - Application settings and preferences
  - `full_recipe.py` - Detailed recipe display view
  - `add_recipes/` - Recipe creation and editing workflows
  - `recipe_browser/` - Recipe browsing with advanced features like card pooling and progressive rendering
  - `meal_planner/` - Meal planning interface with calendar integration
  - `shopping_list/` - Shopping list management with categorization
- **Components (components/)** - Reusable UI widgets organized by functional type
  - `composite/` - Complex multi-widget components (recipe cards, info panels, browser components)
  - `inputs/` - Form controls and input widgets (search bars, smart line edits, toggle switches)
  - `navigation/` - Navigation components (sidebar, title bar)
  - `widgets/` - Basic UI building blocks (buttons, dropdowns, tags, checkboxes)
  - `dialogs/` - Modal dialogs and pop-up components (crop dialogs, dialog windows)
  - `images/` - Image display and manipulation (avatar loaders, image components, cropping tools)
  - `layout/` - Layout management (cards, collapsible sections, flow layouts, separators)
- **ViewModels (view_models/)** - MVVM pattern implementation for data binding and business logic separation
  - Mediates between Views and Core services
  - Handles UI state management and data transformation
  - Includes specialized ViewModels for recipes, ingredients, meal planning, and shopping
- **Managers (managers/)** - UI orchestration and coordination services
  - `navigation/` - Centralized routing, page management, and view registry
  - `tab_manager.py` - Tab-based interface management
  - Additional manager infrastructure for dialogs, notifications, and theming
- **Utils (utils/)** - UI-specific helper functions
  - Form utilities, layout helpers, widget utilities, image processing, and event handling

### 🎭 Style Layer (app/style/)

**Styling & Theming** - Visual presentation and design system

- **Theme (theme/)** - Comprehensive theming system
  - Material Design-inspired color schemes and typography
  - `qss/` - Qt Style Sheets for component styling (buttons, sidebars, cards, etc.)
- **Icon (icon/)** - Icon management and theming system
  - SVG-based icon system with dynamic theming support
- **Animation** - Window and widget animations (future expansion)
- **Effects** - Visual effects and transitions (future expansion)

## Supporting Structure

### 🧪 Testing (_tests/)
**Comprehensive test suite** with clear architectural boundaries

- **Unit Tests** - Layer-specific testing mirroring application structure
  - `unit/core/models/` - Model layer validation and business rules
  - `unit/core/repositories/` - Data access layer testing
  - `unit/core/services/` - Business logic validation
  - `unit/ui/view_models/` - ViewModel behavior and data binding
  - `unit/ui/components/` - UI component functionality
- **Integration Tests** - Cross-layer functionality and workflow testing
  - Database integration with real SQLite instances
  - Full feature workflow testing (recipe CRUD, meal planning)
  - UI integration tests combining multiple components
- **UI Tests** - pytest-qt widget testing for user interactions
  - Navigation flow testing
  - Recipe creation and editing workflows
  - Meal planning user scenarios
- **Test Infrastructure**
  - `fixtures/` - Shared test data and mock objects using factory-boy
  - `conftest.py` - Pytest configuration and shared fixtures

### 🛠️ Development Tools
**Development ecosystem** supporting debugging, automation, and data management

- **Dev Tools (_dev_tools/)** - Development utilities and debugging aids
  - Performance tracking and startup timing
  - Debug logging and filtering systems
  - UI debugging tools (layout debugger, QSS inspector, focus tracker)
  - Test harness for development workflow
- **Scripts (_scripts/)** - Build, deployment, and maintenance automation
  - Database management and modernization scripts
  - Mock data generation and CSV processing
  - Performance profiling and comparison tools
  - Build automation and package management
- **Data Files (_data_files/)** - User data, settings, and application assets
  - `recipe_images/` - Recipe photography and banner images
  - `user_profile/` - User avatar and profile data
  - `temp_crops/` - Temporary image processing files
  - `user_settings.json` - Application configuration and preferences
- **Assets (app/assets/)** - Application resources and media
  - `icons/` - SVG icon library for UI components
  - `fonts/` - Typography resources (Fira Code, Montserrat, Roboto)
- **Config (app/config/)** - Application configuration management
  - Path management, logging configuration, and application settings
- **Documentation (_docs/)** - Technical documentation and architectural guides

## Key Architectural Principles

### Dependency Flow

```
UI Layer → Core Layer ← Style Layer
    ↓         ↓
  Utils ← Shared Utils
```

### Layer Boundaries & Import Rules

**Strict dependency flow ensures maintainability and testability**

- **UI → Core**: UI layer imports from Core for business logic access
- **Core ← UI**: Core layer never imports from UI (maintains framework independence)
- **Style ↔ UI**: Style layer integrates with UI for presentation concerns
- **Utils**: Accessible by all layers for shared functionality
- **Config**: Available to all layers for configuration management
- **Assets**: Accessible primarily by UI and Style layers

### Domain Entities & Business Objects

**Core business entities representing the meal planning domain**

- **Recipe** - Central entity with ingredients, instructions, metadata, and image management
- **Ingredient** - Master ingredient catalog with nutritional information and categorization
- **RecipeIngredient** - Junction entity managing ingredient quantities and recipe relationships
- **MealSelection** - Meal planning entries with scheduling and portion management
- **ShoppingItem** - Shopping list items with categorization and completion tracking
- **RecipeHistory** - Recipe usage tracking and analytics
- **SavedMealState** & **ShoppingState** - Application state persistence entities

## UI Architecture & Design Patterns

**Modern desktop application interface with clean architectural boundaries**

- **Window Management** - Custom title bar and window controls for consistent cross-platform experience
- **Component-Based Design** - Modular, reusable UI components with clear hierarchical organization
- **MVVM Pattern** - Strict separation of concerns with ViewModels mediating between Views and Services
- **Navigation System** - Centralized routing with view registry and navigation history management
- **Progressive Rendering** - Optimized performance for large datasets (recipe browsing with card pooling)
- **Material Design Integration** - Custom theming system with QSS stylesheets and dynamic color schemes
- **Responsive Layout** - Adaptive interfaces that work across different window sizes and orientations

## Architecture Benefits

This layered architecture ensures:

- **Maintainability** - Clear separation of concerns with well-defined boundaries
- **Testability** - Each layer can be tested independently with appropriate mocking
- **Scalability** - Modular design supports feature expansion without architectural debt
- **Framework Independence** - Core business logic remains decoupled from UI framework
- **Performance** - Optimized data access patterns and UI rendering strategies

The architecture successfully supports MealGenie's comprehensive feature set including recipe management, meal planning, shopping list generation, and AI-powered recipe assistance.
