# AI Agents Guide

**Purpose:** This document is a guide for AI agents (like OpenAI Codex) assisting with the MealGenie project. It explains the app’s architecture, coding conventions, and expected behaviors when generating, editing, or refactoring code.

## 📦 Project Overview

MealGenie is a PySide6 desktop app designed to help users plan meals, store recipes, generate shopping lists, and manage a weekly meal planner.

The app is structured around a modular, layered architecture with clear separations of concerns. It prioritizes maintainability, scalability, and theme-aware UI design.

## 🧠 General AI Behavior Expectations

When interacting with the codebase:

- ✅ Follow the project’s architecture (see Architecture Layering).
- ✅ Place new code in the appropriate module/folder.
- ✅ Use consistent naming and theming conventions.
- ✅ Include Google-style docstrings and inline emoji-tagged comments (see Commenting Style).
- ✅ Propose minimal changes at a time unless otherwise instructed.
- ✅ Move reusable logic to the correct helper file when reviewing.

## 🔁 Refactor & Helper File Rules

When reviewing or modifying files:

- ✅ Move shared logic to helper modules:
  - `db_helpers.py` for database utilities.
  - `ui_helpers.py` for layout/styling utilities.
  - `widget_helpers.py` for widget behaviors.
- ✅ Keep UI classes minimal; delegate complex logic to services or helpers.
- ❌ Don’t duplicate logic between services and repositories.
- ✅ Use Pydantic models for cross-layer data validation.
- ✅ Log using `DebugLogger` (never print/raise unless debugging).

## 📁 Key Folder Structure (Simplified)

```text
recipe_app/
├── app/
│   ├── core/
│   │   ├── controllers/   # Flow control (theme, dialogs)
│   │   ├── database/      # SQLAlchemy setup, migrations
│   │   ├── services/      # Business logic
│   │   └── data/          # User-generated content, cache
│   ├── ui/
│   │   ├── components/    # Custom widgets
│   │   ├── pages/         # Main views
│   │   ├── dialogs/       # QDialogs
│   │   └── layout/        # Containers
│   ├── style_manager/     # QSS, theme system
│   └── main.py            # Entry point
├── tests/                 # Pytest-based tests
├── docs/                  # Documentation
├── scripts/               # Dev scripts
├── data_files/            # Resources (icons, images)
└── setup.sh               # Environment setup
```

## 🧱 Architecture Layering & Roles

| Layer         | Purpose                                    |
|---------------|--------------------------------------------|
| `models/`        | SQLAlchemy ORM + Pydantic models         |
| `repositories/`  | Database queries and persistence         |
| `services/`      | Business logic and validation            |
| `controllers/`   | App-wide managers (theme, navigation)    |
| `ui/`            | UI: pages, widgets, layout, dialogs      |
| `tests/`         | Unit tests for each layer                |

## 🖼️ UI & Styling Rules

- All styling is controlled via the theme dictionary and QSS files.
- Use the IconKit system for all icon usage.
- Custom widgets (e.g., `SmartComboBox`, `IngredientWidget`) live in `ui/components/`.
- Avoid hardcoding colors or fonts—use `{COLORS.*}` and `{FONTS.*}` placeholders.

## 🧠 Commenting Style

Use Google-style docstrings and inline emoji-tagged comments for clarity.

**Example:**

```python
def format_recipe_data(raw_data: dict) -> dict:
    """
    Convert raw input dictionary to properly formatted recipe data.

    Args:
        raw_data (dict): Input from UI form.

    Returns:
        dict: Cleaned and formatted recipe data.
    """
    # 🔹 Clean input data from form
    name = raw_data["name"].strip()
    return {"name": name}
```

## ✅ Approved Conventions

| Thing         | Convention                         |
|---------------|------------------------------------|
| Files         | `snake_case.py`                    |
| Classes       | `CamelCase`                        |
| Variables     | `snake_case`                       |
| Signals/Slots | Prefixed with `on_` or `handle_`   |
| UI Methods    | Grouped by widget type (e.g., `setup_buttons`) |
| Debug Code    | Use `DebugLogger.debug("Message")` |

## ❌ Things to Avoid

- ❌ Don’t use Qt Designer `.ui` files (converted `.py` used instead).
- ❌ Don’t bypass the theme dictionary.
- ❌ Don’t access database session outside of the repository layer.
- ❌ Don’t put business logic in UI classes.

## 💬 Special AI Instructions

- When creating a new view, place it in `app/ui/pages/<view_name>.py`.
- When generating test files, place them under `tests/core/<layer>/`.
- When unsure where to put logic: prefer services > helpers > UI.
- If breaking conventions, ask for PR approval first.
- When generating mock data, use Pydantic models (e.g., `RecipeDTO`).

