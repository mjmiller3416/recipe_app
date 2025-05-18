
# 🧩 Service Layer Overview

This document outlines the responsibilities and functions defined in the `services/` package of the MealGenie application. These service modules coordinate multi-step logic, wrap model transactions, and provide higher-level access to application features.

---

## 📄 `recipe_service.py`

**Purpose**: This module exposes high-level helper functions for querying and writing recipe data, abstracting away raw database handling.

### 🔍 Query Helpers

#### `list_all()`
Returns all recipes ordered by `created_at DESC`.
```python
recipes = list_all()
```

#### `get(recipe_id: int)`
Returns a single `Recipe` by ID, or `None` if not found.

#### `recent(days: int = 30)`
Returns all recipes created in the last `n` days using raw SQL.

---

### 🔁 Transactional Logic

#### `create_recipe_with_ingredients(recipe_data, ingredients)`
Creates a new `Recipe` and all associated `Ingredient` links in a **single transaction**.

**Steps:**
1. Validates and saves `Recipe`.
2. For each ingredient:
   - Attempts to find existing `Ingredient` by name/category.
   - If not found, creates new `Ingredient`.
   - Creates a `RecipeIngredient` link with quantity/unit if provided.
3. Commits the full transaction on success.

**Returns:** Newly created `Recipe` instance.

**Why it matters:** Ensures referential integrity and reduces the risk of partial saves or orphaned records.

---

## 📄 `shopping_service.py`

**Purpose**: Generates a complete shopping list from selected recipes and manual additions.

### 🔁 Core Logic

#### `generate_shopping_list(recipe_ids: List[int])`
Aggregates ingredients from both:
- `recipe_ingredients` for selected recipes
- manual entries from the `shopping_lists` table

Returns a unified list of dictionaries with:
- `ingredient_name`, `quantity`, `unit`, `category`, `source`, and `have`

Each item is flagged with:
- `source = "recipe"` if pulled from recipe ingredients
- `source = "manual"` if added manually

#### `_convert_qty(name, qty, unit)`
Applies conversion logic (e.g. butter sticks ↔ tablespoons) using a `_CONVERSIONS` dictionary.
- Falls back to base unit if no perfect conversion is found.
- Used when aggregating quantities from multiple recipes.

**Why it matters:** This logic ensures ingredient quantities are intelligently summed, deduplicated, and presented in a format that makes sense to the user.

---

## 📄 planner_service.py

**Purpose**: Orchestrates loading, saving, and updating meals in the planner. Replaces the legacy meal_helpers.py logic and interacts directly with the MealSelection model.

## 🔧 Core Methods

`load_saved_meal_ids() -> list[int]`

- Fetches a list of previously saved meal IDs (from DB or other persistent source).

`get_meal_by_id(meal_id: int) -> dict[str, Optional[int]]`

- Returns the structured {main, side1, side2, side3} dictionary for a given meal ID.

`save_meal(data: dict[str, Optional[int]]) -> int`

- Creates a new meal in the MealSelection table and returns its ID.

`update_meal(meal_id: int, data: dict[str, Optional[int]])`

- Updates an existing meal using the given recipe IDs.

`delete_meal(meal_id: int)`

- Deletes the specified meal selection by ID.

## 📋 To-Do: Future Service Modules

These service modules are not yet implemented but are strongly recommended based on existing architecture and schema:

### 🗓️ `planner_service.py`
Handles meal selection, weekly scheduling, and completion tracking.
- `suggest_meals(limit: int)`
- `schedule_weekly_menu(selection_ids: list[int])`
- `log_meal_completion(meal_id: int)`

### 🧂 `ingredient_service.py`
Centralizes ingredient deduplication, creation, and normalization.
- `find_or_create_ingredient(name, category)`
- `clean_unit(unit)`
- `normalize_ingredient_name(name)`

### 📆 `weekly_menu_service.py`
Automates weekly menu generation, resets, and batch management.
- `generate_menu(seed=None)`
- `clear_menu(preserve_today=True)`

### 🕰️ `history_service.py`
Wraps logic for meal log and recipe history tracking.
- `track_recipe_cooked(recipe_id)`
- `get_recently_cooked(limit=10)`
- `get_version_log()`

### 🛍️ `shopping_optimizer_service.py`
Future-focused module for smart batching and store optimization.
- Brand preferences
- Unit bundling
- Store-based separation

---

Next section: `init_db.py` setup logic or begin scaffolding these service modules? 🧠🛠️
