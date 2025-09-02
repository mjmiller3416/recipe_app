# MealGenie Project Architecture Guide

This document defines the architectural structure, responsibilities, and boundaries within the **MealGenie** codebase.
It serves two purposes:
1. Acts as a **developer reference** for where code belongs and how layers interact.
2. Provides **Claude Code CLI** with rules to maintain consistency across refactors.

---

## **1. High-Level Project Structure**

```
└── 📁app
    ├── 📁assets
    ├── 📁config
    ├── 📁core
    │   ├── 📁database
    │   ├── 📁dtos
    │   ├── 📁models
    │   ├── 📁repositories
    │   ├── 📁services
    │   └── 📁utils
    ├── 📁style
    │   ├── 📁animation
    │   ├── 📁effects
    │   ├── 📁icon
    │   └── 📁theme
    └── 📁ui
        ├── 📁components
        │   ├── 📁composite
        │   ├── 📁dialogs
        │   ├── 📁images
        │   ├── 📁inputs
        │   ├── 📁navigation
        │   └── 📁widgets
        ├── 📁models
        ├── 📁services
        ├── 📁utils
        ├── 📁views
        ├── constants.py
        └── main_window.py
└── main.py
```

---

## **2. Folder Responsibilities**

### **📁app/assets**
Static resources (images, fonts, icons, templates). No logic — read-only assets.

### **📁app/config**
Central configuration and environment handling. Stores paths, feature flags, and user preferences.

### **📁app/core** *(Business Logic Layer)*
Contains the **domain logic** and should **never depend on UI**.

- **`database/`** → SQLAlchemy engine, Alembic migrations, session management, schema definitions.
- **`dtos/`** → Data Transfer Objects for moving structured data between Core, Services, and UI ViewModels.
- **`models/`** → SQLAlchemy ORM models representing persisted entities.
- **`repositories/`** → Encapsulates data access logic. Talks directly to database models.
- **`services/`** → Business services. Orchestrates repositories and returns DTOs to ViewModels.
- **`utils/`** → Core-only helpers for data handling, serialization, caching, etc.

### **📁app/style** *(Styling & Themes)*
Handles **QSS, theming, and animations**.

- **`animation/`** → Shared easing curves, transitions, QPropertyAnimations.
- **`effects/`** → Drop shadows, elevation, glows, and reusable effects.
- **`icon/`** → IconKit system, SVG registry, dynamic recoloring.
- **`theme/`** → Material3-inspired theme definitions, QSS variables, and global theme controller.

### **📁app/ui** *(Presentation Layer)*
Everything UI-related: widgets, dialogs, view models, and UI services.

#### **`components/`**
Reusable widgets and building blocks:
- **composite/** → Higher-order widgets composed of smaller components.
- **dialogs/** → Modal and non-modal dialogs.
- **images/** → Specialized components for image rendering and manipulation.
- **inputs/** → Custom SmartComboBoxes, styled checkboxes, validators.
- **navigation/** → Sidebar, breadcrumbs, navigation bars.
- **widgets/** → General reusable visual components (buttons, cards, toolbars).

#### **`models/`**
Lightweight **UI models** for temporary state, separate from Core models.

#### **`services/`**
UI-scoped services for **shared behaviors** across multiple views:
- `DialogService` → Manages modal dialogs.
- `NavigationService` → Handles view switching.
- `ThemeService` → Applies global QSS themes.

> **Rule:** UI services **never** import from `app.core`.

#### **`utils/`**
Utility functions for UI:
- `pure_formatting.py` → Presentation-only helpers.
- `qt_models.py` → Proxy/list models for Qt views.
- `qt_workers.py` → QThread/QThreadPool helpers.
- `qt_validation.py` → Custom QValidator implementations.

#### **`views/`**
Actual **screens/pages** the user interacts with.
- Manages widgets, layouts, and signals only.
- Delegates all business logic to **ViewModels**.

#### **constants.py**
UI constants like spacing, typography, sizes, icon scales, and colors.

#### **main_window.py**
Top-level window that orchestrates sidebar, header, stacked views, and injects UI services.

---

## **3. Import & Dependency Rules**

### **Allowed Directions** ✅
- `ui/views` → `ui/models`, `ui/services`, `ui/components`, `ui/utils`
- `ui/models` → `app.core.services`, `app.core.dtos`, `ui/utils`
- `ui/services` → `ui/components`, `style/*`, `ui/utils`
- `ui/utils` → Can import Qt or be pure; never Core

### **Forbidden Directions** ❌
- `ui/views` → **cannot import** `app.core.*`
- `ui/services` → **cannot import** `app.core.*`
- `app/core/*` → **cannot import** anything from `ui/*`

---

## **4. Naming Conventions **

- **Core/Services:** `recipe_service.py`
- **Core/Repositories:** `recipe_repository.py`
- **Core/DTOs:** `recipe_dto.py`
- **Core/Models:** `recipe_model.py`
- **UI/Views:** `add_recipe.py`
- **UI/Models:** `add_recipe_vm.py`
- **UI/Services:** `dialog_service.py`
- **UI/Dialogs:** `recipe_dialog.py`
- **UI/Utils:** `qt_workers.py` or `pure_formatting.py`

- **All Files:**
    - snake_case for files
    - PascalCase for classes/constants
    - snake_case w/ leading underscores for private functions
    - camelCase for public APIs.

---

## **5. Workflow Guidelines**

### **Extract to UI/Model When:**
- View needs Core services or repositories.
- Complex validation or transformation is required.
- Async/long-running logic needs to avoid blocking UI.
- View file exceeds **400 lines**.

### **Keep in View When:**
- Manipulating widgets or layouts.
- Applying styles or object names.
- Wiring signals to ViewModel methods.

### **UI Services Are For:**
- Cross-view coordination.
- Global UI state and theme changes.
- Centralized dialogs, navigation, toasts.

### **Utils Are For:**
- Reusable, small helper functions.
- Separated into **pure** helpers and **Qt-specific** helpers.

### **Core/Models Are For:**
- Business logic and validation.
- Data transformation and mapping.
- Interfacing with external APIs or databases.

### **Core/Repositories Are For:**
- Data access and persistence.
- Querying and saving domain objects.
- Managing database connections and sessions.

### **Core/Services Are For:**
- Business logic and validation.
- Data transformation and mapping.
- Interfacing with external APIs or databases.

### **Core/DTOs Are For:**
- Data transfer objects for API requests/responses.
- Simplifying data structures for UI consumption.
- Validating and serializing data between layers.

---

## **6. Refactor Red Flags** 🚩

- View imports `app.core.*` → **move to ViewModel**.
- Duplicate dialog logic across 3+ views → **create a UI Service**.
- Complex `if/else` shaping data in View → **move to ViewModel**.
- Direct database queries from UI → **forbidden**.

---

## **7. Entry Point**

**`main.py`** initializes:
- Core database engine + services
- UI services + main window
- Launches app

---

## **8. Summary**

- Views = dumb widgets.
- ViewModels = smart orchestrators.
- Core = business rules + persistence.
- UI Services = shared presentation flows.
- Utils = small helpers, separated by Qt vs pure.

By following this guide, we enforce **separation of concerns**, keep the UI layer maintainable, and ensure Claude Code CLI refactors stay consistent.
