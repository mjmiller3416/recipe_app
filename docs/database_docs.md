# 📁 Database Module Overview

This section documents the structure and functionality of the database folder for the MealGenie application. Each file is explained in detail with its purpose, behavior, and how it interacts with other components of the application.

---

## 📂 File Structure

```
└── 📁database
    ├── __init__.py
    ├── app_data.db
    ├── base_model.py
    ├── db_reset.py
    ├── db.py
    ├── init_db.py
    ├── 📁migrations
    │   ├── 001_initial.sql
    │   ├── 002_meal_logs.sql
    │   ├── 003_recipe_history.sql
    │   ├── 004_saved_meal_state.sql
    │   ├── 005_shopping_state.sql
    │   ├── 006_add_created_at.sql
    │   └── 007_add_favorites.sql
    └── 📁models
        ├── __init__.py
        ├── ingredient.py
        ├── meal_log.py
        ├── meal_selection.py
        ├── recipe_history.py
        ├── recipe_ingredient_detail.py
        ├── recipe_ingredient.py
        ├── recipe.py
        ├── saved_meal_state.py
        ├── schema_version.py
        ├── shopping_item.py
        ├── shopping_list.py
        ├── shopping_state.py
        └── weekly_menu.py
```

---

## 📄 `db.py`

**Path:** db.py

### 📝 Purpose

This file provides a **database connection manager** for interacting with the `SQLite` database (`app_data.db`). It centralizes connection logic to ensure transactions are handled cleanly and consistently.

### ⚙️ Functionality

-   Defines the `DB_PATH` pointing to the `app_data.db` file.
-   Exposes a `get_connection()` context manager to safely connect to the database.

### 📌 `get_connection()`

```python
@contextlib.contextmanager
def get_connection():
```

-   **Yields** a `sqlite3.Connection` object.
-   Automatically sets `row_factory = sqlite3.Row` so rows can be accessed as dictionaries.
-   **On success**: commits the transaction.
-   **On failure**: rolls back the transaction.
-   **Always**: closes the connection to avoid leaks.

### 🔄 Usage Pattern

This function is used throughout the application for read/write operations:

```python
// ...existing code...
from database.db import get_connection

with get_connection() as conn:
    cursor = conn.execute("SELECT * FROM recipes")
    data = cursor.fetchall()
// ...existing code...
```

---

## 📄 `base_model.py`

**Path:** base_model.py

### 📝 Purpose

Defines `ModelBase`, the **abstract base class** for all database-bound models. It extends `PydanticBaseModel` to provide standardized CRUD operations.

### ⚙️ Functionality

-   Provides automatic `table_name()` generation from the class name (CamelCase → snake_case).
-   Wraps common ORM-like operations (`all`, `get`, `update`, `save`, `delete`, `exists`).

### 🧱 Core Methods

#### `table_name()`

Automatically infers a table name from the model class.
-   `Recipe` → `recipes`

#### `all()`

Fetches all rows from the associated table.

#### `get(id)`

Fetches a row by primary key.

#### `update(id, **fields)`

Updates the fields of a record and re-saves it.

#### `exists(**fields)`

Returns `True` if a row exists with the given field match(es).

#### `save()`

-   Inserts or replaces the current instance in the table.
-   Automatically assigns `lastrowid` to `self.id`.

#### `delete()`

Deletes the record from the database, raising an error if it hasn’t been saved (`id is None`).

### 🧠 Notes

-   All operations use `get_connection()` from db.py.
-   Provides a reusable, DRY interface for managing persistent data.

---

## 📄 init_db.py

**Path:** init_db.py

### 📝 Purpose
This script initializes the database by creating tables and applying migrations. It ensures the database schema is up-to-date.

### ⚙️ Functionality
-   Connects to the SQLite database.
-   Reads SQL migration files from the migrations directory in order.
-   Executes each migration script to create or alter tables.
-   Tracks applied migrations in the `schema_version` table to prevent re-applying them.
-   The `init_db()` function is the main entry point.

---

## 📄 db_reset.py

**Path:** db_reset.py

### 📝 Purpose

Provides a **reset utility** for wiping and rebuilding the SQLite database from migration scripts.

### ⚙️ Functionality

-   Deletes the `app_data.db` file if it exists.
-   Calls `init_db()` to reinitialize the schema via migration scripts.
-   Uses `DebugLogger` to log warnings, success, and info-level messages.
-   Exits the script automatically once completed (via `sys.exit(0)`).

### 🧪 Usage Scenario

This script is typically used during development/testing to quickly rebuild the schema:

```bash
python -m database.db_reset
```

### 🔄 Steps in `reset_database()`

1.  **Delete Existing DB**:
    -   Checks if `DB_PATH` (from `database/db.py`) exists → deletes it if so.
2.  **Reinitialize DB**:
    -   Calls `init_db()` to replay migration files.
3.  **Exit Program**:
    -   Ends the process with a clean exit once reset is complete.

### 🧠 Notes

-   Intended for development use only — not safe for production.
-   `DebugLogger` usage ensures consistent structured logs.

---

## 📄 Migration Scripts

**Path:** migrations

Migration scripts are SQL files that define changes to the database schema. They are applied in order by `init_db.py`.

### 📜 `001_initial.sql`

Creates the initial set of tables:
-   `recipes`: stores core recipe metadata.
-   `ingredients`: stores all ingredients with categories.
-   `meal_selections`: defines meal groups with up to three sides.
-   `shopping_lists`: total list of ingredients fetched from MealPlanner.
-   `meal_logs`: (deprecated by `002_meal_logs.sql`)
-   `recipe_ingredients`: maps many-to-many recipes ↔ ingredients.
-   `schema_versions`: stores applied migration history.

### 📜 `002_meal_logs.sql`

Replaces `meal_logs` with a more accurate structure, linking to `meal_selections`.

### 📜 `003_recipe_history.sql`

Adds the `recipe_histories` table to track when a specific recipe was cooked.

### 📜 `004_saved_meal_state.sql`

Adds a `meal_state` table to store the state of saved meals in the database. 

### 📜 `005_shopping_state.sql`

Creates the `shopping_states` table to persist checkbox state for ingredients, including `key`, `quantity`, `unit`, and `checked` status.
The purpose of this table is to store the existing state of the ShoppingList (e.g., if an ingredient is 'checked' or not). Additionally, its `quantity` and `unit` fields are used when the ShoppingList is refreshed. This helps determine if a previously 'checked' item should remain checked or be unchecked if, for example, a new recipe alters the total required quantity of that ingredient.

### 📜 `006_add_created_at.sql`

Adds a `created_at` column to the `recipes` table with a default timestamp value.

### 📜 `007_add_favorites.sql`

Adds an `is_favorite` boolean column to the `recipes` table to track favorite recipes.

> All migrations typically use `IF NOT EXISTS` to prevent duplicate table creation.

---

# 📦 Database Models Overview

**Path:** models

This section documents each Pydantic-backed model in the models directory. These models define the structure, validation, and behavior for interacting with the MealGenie database schema. They inherit from `ModelBase`.

---

## 📄 `saved_meal_state.py`

**Path:** saved_meal_state.py
**Represents**: Tracks which meals are currently active/selected in the meal planner.

-   🔸 `meal_id`: int (foreign key to `MealSelection`).
-   🔹 `all()` — Fetches all saved meal states with debug logging.
-   🔹 `clear_all()` — Deletes all entries from the saved meal state table.

---

## 📄 `shopping_item.py`

**Path:** shopping_item.py
**Represents**: A unified data model for shopping list items that combines ingredients from recipes and manual entries.

-   🔸 `ingredient_name`: required string.
-   🔸 `quantity`: float (must be >= 0).
-   🔸 `unit`: optional string.
-   🔸 `category`: optional string.
-   🔸 `source`: literal "recipe" or "manual".
-   🔸 `have`: boolean (default False).
-   🔹 `label()` — Returns formatted display label (e.g., "2 cups • Flour").
-   🔹 `toggle_have()` — Toggles the 'have' status for checkbox state.
-   🔹 `key()` — Returns normalized key for grouping ingredients (name + unit).
-   🔹 `to_model()` — Converts to `ShoppingList` DB model (manual items only).

---

## 📄 `shopping_state.py`

**Path:** shopping_state.py
**Represents**: Persists the checked state and quantities of shopping list items across sessions.

-   🔸 `key`: string (normalized identifier for grouping).
-   🔸 `quantity`: float.
-   🔸 `unit`: string.
-   🔸 `checked`: boolean (default False).
-   🔹 `get_state(key, connection=None)` — Fetches saved state by key.
-   🔹 `update_state(key, quantity, unit, checked, connection=None)` — Adds or updates checkbox state for a shopping item.

---

## 📄 `ingredient.py`

**Path:** ingredient.py
**Represents**: A single ingredient with name and category. Used in recipe mapping.

-   🔸 `ingredient_name`: required string.
-   🔸 `ingredient_category`: required string.
-   🔹 `display_label()` — Returns `"Carrot (Vegetable)"` style labels.
-   🔹 `get_recipes()` — Fetches all recipes using this ingredient.

---

## 📄 `meal_log.py`

**Path:** meal_log.py
**Represents**: An instance of a meal being selected.

-   🔸 `meal_selection_id`: foreign key to `MealSelection`.
-   🔸 `checked_at`: timestamp (default now).
-   🔹 `get_meal()` — Loads the related meal.

---

## 📄 `meal_selection.py`

**Path:** meal_selection.py
**Represents**: A meal group with main + optional sides.

-   🔸 `meal_name`: string.
-   🔸 `main_recipe_id`: int.
-   🔸 `side_recipe_1/2/3`: optional ints.
-   🔹 `get_main_recipe()` — Loads the primary recipe.
-   🔹 `get_side_recipes()` — Loads side dish recipes.

---

## 📄 recipe.py

**Path:** recipe.py
**Represents**: A complete recipe with metadata and logic.

-   🔸 `recipe_name`, `category`, `total_time`, `servings`, `directions`, `image_path`.
-   🔹 `formatted_time()` / `formatted_servings()` — For UI.
-   🔹 `get_ingredients()` — Resolved `Ingredient` list.
-   🔹 `last_cooked()` — Most recent cooked time.
-   🔹 `get_directions_list()` — Step list from text.
-   🔹 `get_ingredient_details()` — JOIN on recipe_ingredients + ingredients.

---

## 📄 `recipe_history.py`

**Path:** recipe_history.py
**Represents**: A record of when a recipe was last cooked.

-   🔸 `recipe_id`: FK to `Recipe`.
-   🔸 `cooked_at`: datetime (default now).
-   🔹 `get_recipe()` — Loads the associated recipe.

---

## 📄 `recipe_ingredient.py`

**Path:** recipe_ingredient.py
**Represents**: Join model for recipes ↔ ingredients.

-   🔸 `recipe_id`, `ingredient_id`: required.
-   🔸 `quantity`, `unit`: optional.
-   🔹 `table_name()` override — hardcoded as `recipe_ingredients`.

---

## 📄 `recipe_ingredient_detail.py`

**Path:** recipe_ingredient_detail.py
**Represents**: Flattened join result used for UI display.

-   🔸 `ingredient_name`, `ingredient_category`.
-   🔸 `quantity`, `unit`.

---

## 📄 `schema_version.py`

**Path:** schema_version.py
**Represents**: Tracks which migrations have been applied.

-   🔸 `version`: migration ID (e.g., `001_initial`).
-   🔸 `applied_on`: timestamp.

---

## 📄 shopping_list.py

**Path:** shopping_list.py
**Represents**: User-facing shopping checklist items.

-   🔸 `id`: Optional int.
-   🔸 `ingredient_name`: string.
-   🔸 `quantity`: float.
-   🔸 `unit`: string.
-   🔸 `have`: boolean.
-   🔹 `label()` — Returns a checklist label with ✔ or ✖ icon.
-   🔹 `to_item()` - Converts to a `ShoppingItem` for UI.
-   🔹 `strip_strings()` - Validator to strip whitespace.


---

## 📄 `weekly_menu.py`

**Path:** weekly_menu.py
**Represents**: Recipes added to the current week's menu.

-   🔸 `recipe_id`: FK to `Recipe`.
-   🔸 `added_at`: timestamp.
-   🔹 `get_recipe()` — Loads the linked recipe.

---