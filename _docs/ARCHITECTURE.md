Recipe App Application Architecture Summary

## Overview

Recipe App is a desktop recipe management application built with PySide6 and SQLAlchemy 2.0, following a layered clean architecture pattern with strict separation of concerns.

## Core Architecture Layers

### 🏗️ Core Layer (app/core/)

- Business Logic Layer - Framework-agnostic domain logic
- Database (database/) - SQLite with Alembic migrations
- Models (models/) - SQLAlchemy ORM entities (Recipe, Ingredient, etc.)
- Repositories (repositories/) - Data access abstraction
- Services (services/) - Business logic orchestration
- DTOs (dtos/) - Data transfer objects for layer communication
- Utils (utils/) - Framework-agnostic shared utilities

## 🎨 UI Layer (app/ui/)

- Presentation Layer - PySide6-based user interface
- Views (views/) - Application pages/screens
- Components (components/) - Reusable UI widgets organized by type:
  - composite/ - Complex multi-widget components
  - inputs/ - Form controls and input widgets
  - navigation/ - Menu, sidebar, navigation components
  - widgets/ - Basic UI building blocks
  - dialogs/ - Modal and dialog components
  - images/ - Image display and manipulation components
  - layout/ - Layout management components
- ViewModels (view_models/) - MVVM pattern implementation for data binding
- Managers (managers/) - UI orchestration services:
  - navigation/ - Routing and page management
  - dialogs/ - Modal dialog management
  - notifications/ - User notification system
  - theme/ - Theme and styling management
- Utils (utils/) - UI-specific helper functions

### 🎭 Style Layer (app/style/)

- Styling & Theming - Visual presentation system
- Theme (theme/) - Material Design color schemes
- Animation (animation/) - Window and widget animations
- Effects (effects/) - Visual effects and transitions
- Icon (icon/) - Icon management and theming

## Supporting Structure

### 🧪 Testing (_tests/)
- Unit Tests - Layer-specific testing mirroring app structure
- Integration Tests - Cross-layer functionality testing
- UI Tests - pytest-qt widget testing
- Fixtures - Shared test data and mock objects

### 🛠️ Development Tools
- Dev Tools (_dev_tools/) - Development utilities and debugging tools
- Scripts (_scripts/) - Build, deployment, and maintenance automation scripts
- Data Files (_data_files/) - User data, settings, and generated assets
- Documentation (_docs/) - Technical documentation and guides

## Key Architectural Principles

### Dependency Flow

```
UI Layer → Core Layer ← Style Layer
    ↓         ↓
  Utils ← Shared Utils
```

### Layer Boundaries

- UI imports from Core (business logic access)
- Core never imports from UI (framework independence)
- Style integrates with UI (presentation concerns)
- Utils accessible by all layers (shared functionality)

### Domain Entities

- Recipe - Core recipe data and metadata
- Ingredient - Ingredient catalog and nutritional data
- MealSelection - Meal planning and scheduling
- ShoppingItem - Shopping list generation from meal plans

## UI Architecture

- Frameless Window using qframelesswindow for native look
- Component-Based Design with PySide6-Fluent-Widgets
- MVVM Pattern separating view logic from presentation
- Navigation Service for routing and page transitions
- Material Design theming with custom color schemes

This architecture ensures maintainability, testability, and clear separation of concerns while supporting Recipe App's recipe management, meal planning, and shopping list functionality.
