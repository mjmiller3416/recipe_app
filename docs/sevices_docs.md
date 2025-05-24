# 📦 Services Package Overview

This section documents the structure and functionality of the services package for the MealGenie application. This package provides a higher-level API for interacting with the application\'s data, encapsulating business logic and data manipulation tasks.

---

## 📂 File Structure

```
└── 📁services
    ├── __init__.py
    ├── ingredient_service.py
    ├── meal_service.py
    ├── planner_service.py
    ├── recipe_service.py
    └── shopping_service.py
```

---

## 📄 ingredient_service.py

**Path:** ingredient_service.py

### 📝 Purpose

This module provides service methods for managing `Ingredient` entities. It includes functions for listing, finding, and creating ingredients, often with transactional support to ensure data integrity.

### ⚙️ Core Class: `IngredientService`

This class provides static methods to interact with `Ingredient` data.

#### Methods

-   **`list_all_ingredient_names(connection: Optional[sqlite3.Connection] = None) -> list[str]`**:
    -   Retrieves a list of all distinct ingredient names from the `ingredients` table.
    -   Can optionally use an existing database `connection`.

-   **`find_matching_ingredients(query: str, connection: Optional[sqlite3.Connection] = None) -> list[Ingredient]`**:
    -   Searches for ingredients whose names match the given `query` (case-insensitive, partial match).
    -   Returns a list of `Ingredient` model instances.
    -   Can optionally use an existing database `connection`.

-   **`get_or_create_ingredient(name: str, category: str, connection: Optional[sqlite3.Connection] = None) -> Ingredient`**:
    -   Attempts to find an existing ingredient by `name` and `category`.
    -   If found, returns the existing `Ingredient` instance.
    -   If not found, creates a new `Ingredient` with the given details and returns it.
    -   This operation is transactional: if no `connection` is provided, it creates one to ensure atomicity.

-   **`build_payload_from_widget(widget) -> dict`**:
    -   A utility method designed to extract ingredient data from a UI widget (presumably an `IngredientWidget`).
    -   It formats this data into a dictionary (payload) suitable for use with other service methods, such as `RecipeService.create_recipe_with_ingredients()`.
    -   The payload includes `ingredient_name`, `ingredient_category`, `unit`, and `quantity`.

---

## 📄 recipe_service.py

**Path:** recipe_service.py

### 📝 Purpose

This module provides functions to interact with the recipe-related tables in the database. It offers methods for querying and creating recipes along with their associated ingredients.

### ⚙️ Core Functions

#### Query Helpers

-   **`list_all() -> list[Recipe]`**:
    -   Returns a list of all `Recipe` objects from the database.
    -   Recipes are ordered by their creation date in descending order (`created_at DESC`).

-   **`get(recipe_id: int) -> Recipe | None`**:
    -   Fetches a single `Recipe` object by its primary key (`recipe_id`).
    -   Returns the `Recipe` object if found, otherwise `None`.

-   **`recent(days: int = 30) -> list[Recipe]`**:
    -   Retrieves recipes created within the last `days` (default is 30).
    -   Uses a raw SQL query to filter recipes based on their `created_at` timestamp.
    -   Results are ordered by creation date in descending order.

#### Transactional Helpers

-   **`create_recipe_with_ingredients(recipe_data: dict, ingredients: List[dict]) -> Recipe`**:
    -   Atomically creates a new recipe and links it to a list of ingredients within a single database transaction.
    -   Takes `recipe_data` (a dictionary conforming to the `Recipe` model) and `ingredients` (a list of dictionaries, each representing an ingredient and its details for the recipe).
    -   For each ingredient:
        -   It first checks if the ingredient (by name and category) already exists in the `ingredients` table.
        -   If it exists, its ID is used.
        -   If not, a new `Ingredient` record is created and its ID is used.
        -   A `RecipeIngredient` record is then created to link the recipe and the ingredient, including quantity and unit if provided.
    -   The entire operation is wrapped in a database connection context manager (`get_connection`) to ensure that it either fully completes (commits) or fully fails (rolls back).
    -   Returns the newly created `Recipe` object.

---

## 📄 meal_service.py

**Path:** meal_service.py

### 📝 Purpose

This module handles CRUD (Create, Read, Update, Delete) operations for `MealSelection` entries. It provides a structured way to manage meal selections, which consist of a main recipe and optional side recipes.

### ⚙️ Core Class: `MealService`

This class provides static methods to interact with `MealSelection` data.

#### Methods

-   **`create_meal(meal: MealSelection) -> MealSelection`**:
    -   Creates and persists a new `MealSelection` to the database.
    -   Expects an unsaved `MealSelection` model instance (i.e., `meal.id` should be `None`).
    -   Raises a `ValueError` if the provided meal object already has an ID.
    -   Saves the meal and returns the saved instance, now with an assigned ID.
    -   Logs the creation event using `DebugLogger`.

-   **`update_meal(meal: MealSelection) -> None`**:
    -   Updates an existing `MealSelection` in the database.
    -   Expects a `MealSelection` model instance with a valid ID.
    -   Raises a `ValueError` if the meal object does not have an ID.
    -   Uses the `MealSelection.update()` class method to modify the record with the provided attributes (`meal_name`, `main_recipe_id`, `side_recipe_1`, `side_recipe_2`, `side_recipe_3`).
    -   Logs the update event.

-   **`load_meal(meal_id: int) -> Optional[MealSelection]`**:
    -   Loads a `MealSelection` from the database using its `meal_id`.
    -   Returns the `MealSelection` object if found.
    -   If no meal is found with the given ID, it logs a warning and returns `None`.
    -   Logs the load event.

---

## 📄 planner_service.py

**Path:** planner_service.py

### 📝 Purpose

This module provides services for managing the state of the Meal Planner feature. It handles loading and saving the list of meal IDs that are currently active or selected in the planner.

### ⚙️ Core Class: `PlannerService`

This class uses static methods to manage the `SavedMealState` data.

#### Methods

-   **`load_saved_meal_ids(connection: Optional[sqlite3.Connection] = None) -> List[int]`**:
    -   Retrieves all `meal_id`s stored in the `SavedMealState` table.
    -   These represent the meals that were previously active in the meal planner.
    -   Returns a list of integers (meal IDs).
    -   Can optionally use an existing database `connection`.
    -   Logs the loaded IDs.

-   **`save_active_meal_ids(meal_ids: List[int], connection: Optional[sqlite3.Connection] = None) -> None`**:
    -   Saves a list of `meal_ids` as the current active state of the meal planner.
    -   This operation is atomic: it first deletes all existing entries in `SavedMealState` and then inserts the new `meal_ids`.
    -   If no `connection` is provided, it creates one to ensure the transactionality of clearing and saving.
    -   Logs the saved IDs.

-   **`clear_planner_state(connection: Optional[sqlite3.Connection] = None) -> None`**:
    -   Deletes all entries from the `SavedMealState` table, effectively clearing the saved state of the meal planner.
    -   If no `connection` is provided, it creates one for the transaction.
    -   Logs the clear event.

-   **`validate_meal_ids(meal_ids: List[int]) -> List[int]`**:
    -   Checks a list of `meal_ids` against the `MealSelection` table to ensure they correspond to existing meals.
    -   Returns a new list containing only the `meal_ids` that are valid (i.e., exist in the database).

---

## 📄 shopping_service.py

**Path:** shopping_service.py

### 📝 Purpose

This module provides a structured service for managing shopping lists. It combines ingredients from selected recipes and manually added items, handles unit conversions, and persists the "checked" state of shopping list items.

### ⚙️ Core Class: `ShoppingService`

This class uses static methods to manage shopping list generation and manipulation.

#### Key Functionality

-   **Unit Conversion (`_convert_qty`)**:
    -   A private static method `_convert_qty(name: str, qty: float, unit: str) -> tuple[float, str]` attempts to convert ingredient quantities to a base unit for consistency.
    -   It uses a predefined `_CONVERSIONS` dictionary (e.g., for butter, converting "stick" to "tbsp").
    -   If a conversion rule exists for an ingredient and its unit, it converts the quantity to the most appropriate larger unit or a base unit.

-   **Shopping List Generation (`generate_shopping_list`)**:
    -   **`generate_shopping_list(recipe_ids: List[int]) -> List[ShoppingItem]`**:
        -   Generates a comprehensive shopping list based on a list of `recipe_ids`.
        -   It first aggregates ingredients from all specified recipes using `_aggregate_recipe_ingredients()`.
        -   For each aggregated ingredient, it checks if a `ShoppingState` exists (persisted "checked" status and quantity/unit) and applies the `have` status accordingly.
        -   It then appends any manually added items (from the `ShoppingList` table) to the result.
        -   Returns a list of `ShoppingItem` objects.

-   **Ingredient Aggregation (`_aggregate_recipe_ingredients`)**:
    -   **`_aggregate_recipe_ingredients(recipe_ids: List[int]) -> List[ShoppingItem]`**:
        -   Collects all `RecipeIngredient` entries for the given `recipe_ids`.
        -   Aggregates quantities for identical ingredients (summing them up).
        -   Converts units using `_convert_qty()`.
        -   Creates `ShoppingItem` objects for each unique ingredient, and if a `ShoppingState` exists for an item, its `checked` status is applied.

-   **Recipe ID Retrieval (`get_recipe_ids_from_meals`)**:
    -   **`get_recipe_ids_from_meals(meal_ids: List[int]) -> List[int]`**:
        -   Takes a list of `meal_ids`.
        -   For each `meal_id`, it loads the `MealSelection` using `MealService.load_meal()`.
        -   Collects the `main_recipe_id` and any `side_recipe_id`s associated with these meals.
        -   Returns a flat list of all `recipe_ids` from the specified meals.

-   **Manual Item Management**:
    -   **`add_manual_item(name: str, qty: float, unit: str) -> None`**:
        -   Creates a new `ShoppingList` record for a manually added item and saves it to the database.
    -   **`clear_manual_items() -> None`**:
        -   Deletes all records from the `ShoppingList` table (i.e., all manually added items).
    -   **`toggle_have_status(item_name: str) -> None`**:
        -   Finds a manually added item in the `ShoppingList` table by its `item_name`.
        -   Toggles its `have` status (boolean) and saves the change.
        *Note: This method seems to operate on `ShoppingList` (manual items) and not on `ShoppingState` (which persists states for recipe-derived items as well). This distinction is important.*

### 🧠 Notes

-   The `ShoppingService` plays a crucial role in creating a user-friendly shopping experience by consolidating ingredients from various sources and remembering user interactions (like checking off items).
-   It uses `ShoppingState` to persist the `checked` status and original quantity/unit of ingredients, which is important for intelligently updating the list when recipes change.
-   Circular imports are handled locally within methods where necessary (e.g., importing `ShoppingState` inside `generate_shopping_list`).
-   `DebugLogger` is used for logging service operations.