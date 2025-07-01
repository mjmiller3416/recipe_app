# SQLAlchemy 2.0 Migration Prompts for Codex

This document contains a series of Codex-optimized prompts designed to guide an AI developer (like Codex) through the process of converting a legacy database layer to SQLAlchemy 2.0 ORM using modern best practices. Each task includes a scoped preamble, checklist, inline comment guidance, and clear file path expectations.

---

## ✨ Preamble (Paste at the Top of Every Prompt)

```
You are Codex, an expert Python developer.

You are assisting with the migration of the `MealGenie` desktop application to use SQLAlchemy 2.0 ORM.
Your task is to convert legacy database code into modern, typed SQLAlchemy models and services using DeclarativeBase.

Follow these global rules:
- Use `DeclarativeBase` as the base class for all models.
- Use `Mapped[...]` for type-annotated attributes.
- Use `mapped_column(...)` to define fields.
- Use `relationship(...)` with proper `Mapped[...]` typing.
- Keep models in: `app/core/data/models/`
- Services operate on SQLAlchemy `Session` objects.
- Do not summarize or explain unless requested.
- Generate full, production-ready code.

Each phase will be delivered as a separate task. Complete *only the current phase*. Wait for the next before continuing.
```

---

## Phase 1: Create Declarative Base

```
### Task: Create the Declarative Base Class

Checklist:
- [x] Create a new file: `app/core/data/sqlalchemy_base.py`
- [x] Define a `Base` class using `DeclarativeBase`
- [x] Add docstring explaining purpose
- [x] Add a shared timestamp column (commented out for now)

# File: app/core/data/sqlalchemy_base.py
# TODO: Define the declarative base for all ORM models
```

---

## Phase 2: Convert Core Models

```
### Task: Convert the following models to SQLAlchemy 2.0 ORM syntax

Checklist:
- [x] Recipe (with ingredients relationship)
- [x] Ingredient (with recipes relationship)
- [x] RecipeIngredient (association table)

Place each model in its own file:
- `app/core/data/models/recipe.py`
- `app/core/data/models/ingredient.py`
- `app/core/data/models/recipe_ingredient.py`

Use the following rules:
- Use `Mapped[...]` and `mapped_column(...)`
- Use `__tablename__`
- Add full type hints
- Define relationships using `Mapped[List[...]]` and `relationship()`
- For RecipeIngredient, define a composite primary key

# TODO: Start with Recipe model in recipe.py
# TODO: Include id, name, instructions, and ingredients relationship
# TODO: Use back_populates="recipe" for relationships

# TODO: Next, define Ingredient with id, name, and recipes relationship
# TODO: Use back_populates="ingredient"

# TODO: Define RecipeIngredient with composite key, quantity, and links to Recipe and Ingredient
```

---

## Phase 3: Refactor Services to Use Sessions

```
### Task: Refactor RecipeService to Use SQLAlchemy ORM and Sessions

Checklist:
- [x] Create method: `create_recipe_with_ingredients`
- [x] Accept a `Session` as the first argument
- [x] Use `session.add`, `session.commit`, and `session.refresh`
- [x] Use new Recipe, Ingredient, and RecipeIngredient models
- [x] Assume IngredientService has a method `get_or_create(db, name)`

File: `app/core/services/recipe_service.py`

# TODO: Replace raw SQL with SQLAlchemy ORM pattern
# TODO: Associate RecipeIngredient to Recipe using `.ingredients.append()`
# TODO: Refresh and return the created recipe object
```

---

## Phase 4: Create Pytest Test Fixtures

```
### Task: Create a pytest fixture for an in-memory database

Checklist:
- [x] Use in-memory SQLite for isolation
- [x] Create and drop all tables per test
- [x] Return a `Session` for use in tests

File: `tests/conftest.py`

# TODO: Use `Base.metadata.create_all()` and `drop_all()`
# TODO: Yield a SQLAlchemy `Session` instance
```

---

## Phase 5: Configure Alembic and Generate Initial Migration

```
### Task: Set up Alembic to work with the new SQLAlchemy models

Checklist:
- [x] Edit `alembic.ini` and `env.py`
- [x] Set `target_metadata = Base.metadata`
- [x] Import all models to ensure discovery

File: `app/core/data/migrations/env.py`

# TODO: Import Base from `sqlalchemy_base.py`
# TODO: Import all models to register with metadata

# After config, run this command to autogenerate:
# alembic revision --autogenerate -m "Initial migration"
```

---

## Phase 6: Create Data Migration Script

```
### Task: Create a script to migrate legacy data to new ORM schema

Checklist:
- [x] Read data from old DB
- [x] Write to new DB using ORM models
- [x] Handle both independent and dependent tables
- [x] Commit in safe batches

File: `scripts/migrate_legacy_data.py`

# TODO: Connect to both old and new databases
# TODO: Migrate Ingredients first
# TODO: Then migrate Recipes and RecipeIngredients
# TODO: Resolve FK relationships by name match
# TODO: Use SQLAlchemy Session for writes
```

---

## Phase 7: Cleanup

```
### Task: Remove legacy database code

Checklist:
- [x] Delete old base models, utilities, or raw SQL files
- [x] Remove obsolete imports or config
- [x] Archive legacy migrations (if any)
- [x] Update README with new setup instructions

# TODO: Search for any use of old DB methods
# TODO: Replace with SQLAlchemy or delete
```

---

Let me know if you'd like me to generate **Codex input files**, **Codex task runner scripts**, or a pre-filled `README.md` section for dev onboarding with SQLAlchemy 2.0!
