# AGENTS.md

## Project Title

MealGenie

## Project Overview

MealGenie is a cross-platform desktop application built with PySide6 for planning weekly meals, managing and viewing recipes, and creating dynamic shopping lists. It aims to simplify household meal management by combining structured planning with rich UI features. A central Dashboard will eventually serve as the user’s command center.

## Tech Stack

* **Frontend**: PySide6 (QWidgets), QSS (custom theming)
* **Backend**: Python service layer (PlannerService, ShoppingService, RecipeService)
* **Database**: SQLite, using Pydantic models for validation
* **Deployment**: In development; future packaging planned via PyInstaller or MSI
* **Other Tools**: pytest, colorlog, Qt Designer (formerly), Codex AI agent support

## Project Structure

```
recipe_app/
├── app/
│   ├── core/
│   │   ├── data/            # SQLite interface + CRUD utilities
│   │   ├── services/        # Business logic layer
│   ├── ui/
│   │   ├── components/      # Custom widgets
│   │   ├── pages/           # Feature views (AddRecipe, ShoppingList, etc.)
│   │   ├── layout/          # Reusable layout containers
│   ├── style_manager/       # ThemeController, QSS injection, styling tools
├── data_files/              # Bundled assets (images, icons, fonts)
├── docs/                    # Project documentation
├── tests/                   # pytest-based unit tests
├── scripts/                 # CLI setup, test, and reset tools
├── main.py                  # App entry point
└── setup.sh                 # Dev environment bootstrap
```

## Development Guidelines

### Code Style

* Follow PEP 8 and Google Python Style Guide
* Use structured docstrings and emoji-based comment tags (⚠️, 🔹, ✅, etc.)
* Group imports by standard, third-party, local

### Naming Conventions

* Files: `snake_case.py`
* Classes: `PascalCase`
* Functions: `snake_case()`
* Constants: `ALL_CAPS`
* Widgets: Prefer `ComponentTypeWidgetName` (e.g., `RecipeCard`, `MealWidget`)

### Git Workflow

* Branches:

  * `feature/*` — new features
  * `bugfix/*` — bug fixes
  * `refactor/*` — restructuring or cleanup
* Use descriptive commit messages
* Rebase before PRs when possible
* Prefer squash + merge for clean history

## Environment Setup

### Development Requirements

* Python 3.11+
* Git
* Bash-compatible terminal
* Linux: `libegl1`, `libgl1` for UI support

### Installation Steps

```bash
# 1. Clone the project
git clone [repo-url]

# 2. Enter the directory
cd recipe_app

# 3. Run setup script
bash setup.sh

# 4. Run app
python main.py
```

## Core Feature Implementation

### Recipe Management

* Add, edit, and delete recipes with structured data
* Uses Pydantic models and `RecipeService`

### Shopping List

* Aggregates ingredient quantities across planned meals
* Handles unit conversions and merges manual ingredients

### Meal Planner

* Assign recipes to specific days
* Tabs persist across sessions via `PlannerService`

### Full Recipe Dialog

* Displays all recipe details (image, steps, metadata) in a scrollable dialog
* Powered by `RecipeDialogBuilder`

### Custom Theming

* Supports brandable themes via QSS placeholders and a `ThemeController`
* Auto-refreshes icons, borders, backgrounds on theme change

### Dashboard (Upcoming)

* Central hub showing weekly overview, quick actions, and status widgets
* Will support drag-drop, micro-widgets, and theme-aware visuals

## Testing Strategy

### Unit Testing

* Framework: `pytest`
* Covers: core services, models, and key utilities
* Structure: mirrors `app/` hierarchy in `tests/`

### Integration Testing (Planned)

* Will validate end-to-end data flow across service layers

### GUI / E2E Testing (Future)

* Potential use of tools like `pytest-qt` or `squish` for automated GUI checks

## Deployment Guide (Future)

### Packaging Targets

* Windows: `.exe` or `.msi` via PyInstaller
* macOS: `.app` bundle
* Linux: AppImage or Flatpak TBD

### Build Process (planned)

* Strip dev-only files
* Bundle assets from `data_files/`
* Set environment vars as needed

## Security Considerations

* Pydantic validation used for all incoming recipe/ingredient data
* SQLite is local only; no remote API access at this time

## Common Issues

### Issue 1: PySide6 errors on test run (e.g. libEGL)

**Solution**: Run `sudo apt-get install libegl1 libgl1` on Debian/Ubuntu

### Issue 2: Dark mode styles not applying

**Solution**: Ensure `QT_STYLE_OVERRIDE=windowsvista` is set before launch

## Reference Resources

* [PySide6 Docs](https://doc.qt.io/qtforpython/)
* [Pydantic Docs](https://docs.pydantic.dev/)
* [Python Style Guide](https://google.github.io/styleguide/pyguide.html)
* [QSS Cheat Sheet](https://doc.qt.io/qt-6/stylesheet-reference.html)

## Changelog

### v1.0.0 (2025-06-25)

* Initial planning doc + refactored file structure
* Setup script created
* Theme system and RecipeService implemented
