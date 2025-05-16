
# 📁 Database Module Overview

This section documents the structure and functionality of the `database/` folder for the MealGenie application. Each file is explained in detail with its purpose, behavior, and how it interacts with other components of the application.

---

## 📂 File Structure

```
└── 📁database
    └── 📁migrations
        └── 001_initial.sql
        └── 002_create_meal_logs.sql
        └── 003_create_recipe_history.sql
    └── 📁models
        └── __init__.py
        └── ingredient.py
        └── meal_log.py
        └── meal_selection.py
        └── recipe_history.py
        └── recipe_ingredient_detail.py
        └── recipe_ingredient.py
        └── recipe.py
        └── schema_version.py
        └── shopping_list.py
        └── weekly_menu.py
    └── __init__.py
    └── app_data.db
    └── base_model.py
    └── db_reset.py
    └── db.py
    └── init_db.py
```

---

## 📄 `db.py`

**Path:** `database/db.py`

### 📝 Purpose

This file provides a **database connection manager** for interacting with the `SQLite` database (`app_data.db`). It centralizes connection logic to ensure transactions are handled cleanly and consistently.

### ⚙️ Functionality

- Defines the `DB_PATH` pointing to the `app_data.db` file.
- Exposes a `get_connection()` context manager to safely connect to the database.

### 📌 `get_connection()`

```python
@contextlib.contextmanager
def get_connection():
```

- **Yields** a `sqlite3.Connection` object.
- Automatically sets `row_factory = sqlite3.Row` so rows can be accessed as dictionaries.
- **On success**: commits the transaction.
- **On failure**: rolls back the transaction.
- **Always**: closes the connection to avoid leaks.

### 🔄 Usage Pattern

This function is used throughout the application for read/write operations:

```python
from database.db import get_connection

with get_connection() as conn:
    cursor = conn.execute("SELECT * FROM recipes")
    data = cursor.fetchall()
```

---

## 📄 `base_model.py`

**Path:** `database/base_model.py`

### 📝 Purpose

Defines `ModelBase`, the **abstract base class** for all database-bound models. It extends `PydanticBaseModel` to provide standardized CRUD operations.

### ⚙️ Functionality

- Provides automatic `table_name()` generation from the class name (CamelCase → snake_case).
- Wraps common ORM-like operations (`all`, `get`, `update`, `save`, `delete`, `exists`).

### 🧱 Core Methods

#### `table_name()`

Automatically infers a table name from the model class.

- `Recipe` → `recipes`
- `Category` → `categories`

#### `all()`

Fetches all rows from the associated table.

```python
rows = conn.execute("SELECT * FROM recipes").fetchall()
```

#### `get(id)`

Fetches a row by primary key.

```python
Recipe.get(1)
```

#### `update(id, **fields)`

Updates the fields of a record and re-saves it.

#### `exists(**fields)`

Returns `True` if a row exists with the given field match(es).

#### `save()`

- Inserts or replaces the current instance in the table.
- Automatically assigns `lastrowid` to `self.id`.

#### `delete()`

Deletes the record from the database, raising an error if it hasn’t been saved (`id is None`).

### 🧠 Notes

- All operations use `get_connection()` from `db.py`.
- Provides a reusable, DRY interface for managing persistent data.

---

## 📄 `db_reset.py`

**Path:** `database/db_reset.py`

### 📝 Purpose

Provides a **reset utility** for wiping and rebuilding the SQLite database from migration scripts.

### ⚙️ Functionality

- Deletes the `app_data.db` file if it exists.
- Calls `init_db()` to reinitialize the schema via migration scripts.
- Uses `DebugLogger` to log warnings, success, and info-level messages.
- Exits the script automatically once completed (via `sys.exit(0)`).

### 🧪 Usage Scenario

This script is typically used during development/testing to quickly rebuild the schema:

```bash
python -m database.db_reset
```

### 🔄 Steps in `reset_database()`

1. **Delete Existing DB**:
   - Checks if `app_data.db` exists → deletes it if so.
2. **Reinitialize DB**:
   - Calls `init_db()` to replay migration files.
3. **Exit Program**:
   - Ends the process with a clean exit once reset is complete.

### 🧠 Notes

- Intended for development use only — not safe for production.
- `DebugLogger` usage ensures consistent structured logs.

---

## 📄 Migration Scripts

### 📜 `001_initial.sql`

**Creates the following tables:**

- `recipes`: stores core recipe metadata.
- `ingredients`: stores all ingredients with categories.
- `meal_selections`: defines meal groups with up to three sides.
- `shopping_lists`: temporary ingredient lists with quantities.
- `meal_logs`: links a recipe and timestamp of addition (deprecated by v002).
- `recipe_ingredients`: maps many-to-many recipes ↔ ingredients, with optional quantity/unit overrides.
- `schema_versions`: stores applied migration history.

### 📜 `002_create_meal_logs.sql`

**Replaces `meal_logs` with a more accurate structure:**

- `meal_logs`: logs instances of `meal_selections` being selected.
- Uses `meal_selection_id` instead of direct `recipe_id` for better historical tracking.

### 📜 `003_create_recipe_history.sql`

**Adds:**

- `recipe_histories`: tracks when a specific `recipe_id` was cooked.

> All migrations use `IF NOT EXISTS` to prevent duplicate table creation.

---


# 📦 Database Models Overview

This section documents each Pydantic-backed model in the `database/models/` directory. These models define the structure, validation, and behavior for interacting with the MealGenie database schema.

---

## 📄 `ingredient.py`
**Represents**: A single ingredient with name and category. Used in recipe mapping.

- 🔸 `ingredient_name`: required string.
- 🔸 `ingredient_category`: required string.
- 🔹 `display_label()` — Returns `"Carrot (Vegetable)"` style labels.
- 🔹 `get_recipes()` — Fetches all recipes using this ingredient.

---

## 📄 `meal_log.py`
**Represents**: An instance of a meal being selected.

- 🔸 `meal_selection_id`: foreign key to `MealSelection`.
- 🔸 `checked_at`: timestamp (default now).
- 🔹 `get_meal()` — Loads the related meal.

---

## 📄 `meal_selection.py`
**Represents**: A meal group with main + optional sides.

- 🔸 `meal_name`: string.
- 🔸 `main_recipe_id`: int.
- 🔸 `side_recipe_1/2/3`: optional ints.
- 🔹 `get_main_recipe()` — Loads the primary recipe.
- 🔹 `get_side_recipes()` — Loads side dish recipes.

---

## 📄 `recipe.py`
**Represents**: A complete recipe with metadata and logic.

- 🔸 `recipe_name`, `category`, `total_time`, `servings`, `directions`, `image_path`.
- 🔹 `suggest(days)` — Returns recipes not recently used.
- 🔹 `formatted_time()` / `formatted_servings()` — For UI.
- 🔹 `get_ingredients()` — Resolved `Ingredient` list.
- 🔹 `last_cooked()` — Most recent cooked time.
- 🔹 `get_directions_list()` — Step list from text.
- 🔹 `get_ingredient_details()` — JOIN on recipe_ingredients + ingredients.

---

## 📄 `recipe_history.py`
**Represents**: A record of when a recipe was last cooked.

- 🔸 `recipe_id`: FK to `Recipe`.
- 🔸 `cooked_at`: datetime (default now).
- 🔹 `get_recipe()` — Loads the associated recipe.

---

## 📄 `recipe_ingredient.py`
**Represents**: Join model for recipes ↔ ingredients.

- 🔸 `recipe_id`, `ingredient_id`: required.
- 🔸 `quantity`, `unit`: optional.
- 🔹 `table_name()` override — hardcoded as `recipe_ingredients`.
- 🔹 `__repr__()` — Developer-friendly display string.

---

## 📄 `recipe_ingredient_detail.py`
**Represents**: Flattened join result used for UI display.

- 🔸 `ingredient_name`, `ingredient_category`.
- 🔸 `quantity`, `unit`.

---

## 📄 `schema_version.py`
**Represents**: Tracks which migrations have been applied.

- 🔸 `version`: migration ID (e.g., `001_initial`).
- 🔸 `applied_on`: timestamp.

---

## 📄 `shopping_list.py`
**Represents**: User-facing shopping checklist items.

- 🔸 `ingredient_name`, `quantity`, `unit`, `have`.
- 🔹 `label()` — Returns a checklist label with ✔ or ✖ icon.

---

## 📄 `weekly_menu.py`
**Represents**: Recipes added to the current week's menu.

- 🔸 `recipe_id`: FK to `Recipe`.
- 🔸 `added_at`: timestamp.
- 🔹 `get_recipe()` — Loads the linked recipe.

---



