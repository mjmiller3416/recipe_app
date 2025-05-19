# 🛍️ Shopping List Package Documentation

This document provides a comprehensive overview of the Shopping List package in the MealGenie application. It covers the user interface, business logic, data models, and key workflows involved in generating and managing shopping lists.

## 🎯 Overview

The Shopping List package allows users to:
- Generate a consolidated list of ingredients required for selected recipes.
- Manually add custom items to the shopping list.
- Track acquired items by checking them off.
- Persist the checked state of items across application sessions and list refreshes.

The system is designed to be intelligent, remembering item states and attempting to normalize units for a cleaner user experience.

## 📂 File Structure

The Shopping List functionality is primarily implemented across the following key files and directories:

-   **UI Layer**:
    -   `views/shopping_list/shopping_list.py`: Contains the `ShoppingList` QWidget, which is the main user interface for displaying and interacting with the shopping list.
    -   `views/shopping_list/__init__.py`: Package initializer.
-   **Service Layer**:
    -   `services/shopping_service.py`: Houses the `ShoppingService` class, responsible for all business logic related to shopping lists (generation, aggregation, manual item management, state persistence).
-   **Data Layer (Models)**:
    -   `database/models/shopping_list.py`: Defines the `ShoppingList` SQLAlchemy model, representing items manually added to the shopping list and stored in the `shopping_list` table.
    -   `database/models/shopping_item.py`: Defines the `ShoppingItem` Pydantic model, a structured data object used to represent a single ingredient in the shopping list, whether derived from a recipe or added manually. This model is primarily for in-memory operations and UI display.
    -   `database/models/shopping_state.py`: Defines the `ShoppingState` SQLAlchemy model, used to persist the 'checked' status, quantity, and unit of ingredients (primarily from recipes) in the `shopping_states` table. This allows the application to remember user interactions.
-   **Database Migrations**:
    -   `database/migrations/005_shopping_state.sql`: SQL script for creating the `shopping_states` table.

## 🧩 Core Components

### 1. UI: `ShoppingList` (QWidget)
   - **Path**: `views/shopping_list/shopping_list.py`
   - **Purpose**: Provides the graphical interface for the shopping list.
   - **Key Features**:
     - Displays ingredients grouped by category (e.g., "Produce", "Dairy", "Manual Entries").
     - Allows users to manually add items with quantity, unit, and name.
     - Presents each item with a checkbox to mark it as "have" or "don't have".
     - Interacts with `ShoppingService` to load the list and to signal changes in item states or manual additions.
     - Clears and re-renders the list when new recipe selections are made or manual items are modified.
     - Organizes items into two columns for better readability on wider screens.

### 2. Service: `ShoppingService`
   - **Path**: `services/shopping_service.py`
   - **Purpose**: Encapsulates all business logic for shopping list management. It acts as an intermediary between the UI and the database.
   - **Key Functionality**:
     - **Shopping List Generation (`generate_shopping_list`)**:
       - Takes a list of `recipe_ids`.
       - Aggregates all necessary ingredients from these recipes using `_aggregate_recipe_ingredients`.
       - For each aggregated ingredient, it retrieves any persisted `ShoppingState` (e.g., if it was previously checked off) and applies this state.
       - Appends any manually added items (from the `ShoppingList` table) to the final list.
       - Returns a list of `ShoppingItem` Pydantic models.
     - **Ingredient Aggregation (`_aggregate_recipe_ingredients`)**:
       - Collects `RecipeIngredient` entries for the given `recipe_ids`.
       - Sums quantities for identical ingredients.
       - Attempts unit conversion to standardize units (e.g., "stick of butter" to "tbsp") using `_convert_qty`.
       - Creates `ShoppingItem` objects, applying `ShoppingState` if available.
     - **Unit Conversion (`_convert_qty`)**:
       - A private static method that uses a predefined `_CONVERSIONS` dictionary to normalize ingredient quantities to base units or more common larger units.
     - **Recipe ID Retrieval (`get_recipe_ids_from_meals`)**:
       - Fetches all `recipe_ids` associated with a given list of `meal_ids` by interacting with `MealService`.
     - **Manual Item Management**:
       - `add_manual_item(name: str, qty: float, unit: str)`: Creates and saves a new `ShoppingList` record for a manually entered item.
       - `clear_manual_items()`: Deletes all records from the `ShoppingList` table (i.e., all manual items).
       - `toggle_have_status(item_name: str)`: Toggles the `have` status of a manually added item in the `ShoppingList` table. *(Note: This is distinct from toggling recipe-derived items, which uses `ShoppingState`).*
     - **State Persistence**: Implicitly handles state by creating `ShoppingItem` objects that reflect `ShoppingState` and by providing data that the UI uses to update `ShoppingState`.

### 3. Data Model: `ShoppingItem` (Pydantic Model)
   - **Path**: `database/models/shopping_item.py`
   - **Purpose**: A Pydantic `BaseModel` that serves as a unified, in-memory representation of a shopping list item. It's used by `ShoppingService` to process and return data to the UI.
   - **Key Attributes**:
     - `ingredient_name: str`
     - `quantity: float`
     - `unit: Optional[str]`
     - `category: Optional[str]`
     - `source: Literal["recipe", "manual"]`: Indicates if the item came from a recipe or was manually added.
     - `have: bool`: Whether the item is checked off.
   - **Key Methods**:
     - `label()`: Returns a formatted string for UI display (e.g., "2 cups • Flour").
     - `toggle_have()`: Flips the `have` status.
     - `key()`: Generates a normalized key (name + unit) used for grouping and for `ShoppingState` lookups.
     - `to_model()`: Converts a `ShoppingItem` (if `source` is "manual") back to a `ShoppingList` DB model for saving.

### 4. Data Model: `ShoppingList` (SQLAlchemy Model)
   - **Path**: `database/models/shopping_list.py`
   - **Purpose**: Represents an item manually added to the shopping list by the user. These are stored in the `shopping_list` database table.
   - **Key Attributes (Columns)**:
     - `id: Optional[int]` (Primary Key)
     - `ingredient_name: str`
     - `quantity: float`
     - `unit: str`
     - `have: bool`
   - **Key Methods**:
     - `label()`: Returns a checklist-style label for UI.
     - `to_item()`: Converts the database model instance into a `ShoppingItem` Pydantic model for consistent handling in the service and UI.

### 5. Data Model: `ShoppingState` (SQLAlchemy Model)
   - **Path**: `database/models/shopping_state.py`
   - **Purpose**: Persists the user's interaction with recipe-derived shopping list items, specifically their "checked" status, last known quantity, and unit. This is stored in the `shopping_states` table.
   - **Key Attributes (Columns)**:
     - `id: INTEGER` (Primary Key)
     - `key: TEXT NOT NULL UNIQUE`: A normalized key (e.g., "flour::cup") to uniquely identify an ingredient and its unit.
     - `quantity: REAL NOT NULL`: The quantity of the item when its state was last saved.
     - `unit: TEXT NOT NULL`: The unit of the item when its state was last saved.
     - `checked: BOOLEAN NOT NULL DEFAULT 0`: Whether the item was marked as "have".
   - **Key Methods**:
     - `get_state(key: str)`: Fetches the saved state for a given item key.
     - `update_state(key: str, quantity: float, unit: str, checked: bool)`: Adds or updates the state for an item. This is crucial for remembering if an item was checked, even if its required quantity changes due to recipe modifications.

## ⚙️ Key Workflows

### 1. Generating and Displaying the Shopping List
   1. **Trigger**: User navigates to the Shopping List view or updates selected recipes/meals that feed into the list.
   2. **UI (`ShoppingList.load_shopping_list`)**:
      - Receives a list of `recipe_ids`.
      - Clears any currently displayed list.
      - Calls `ShoppingService.generate_shopping_list(recipe_ids)`.
   3. **Service (`ShoppingService.generate_shopping_list`)**:
      - Aggregates ingredients from the recipes (handling duplicates, summing quantities, converting units).
      - For each aggregated recipe ingredient, it calls `ShoppingState.get_state(item.key())` to see if there's a persisted "checked" status and applies it to the `ShoppingItem.have` attribute.
      - Retrieves all manually added items from the `ShoppingList` table (converting them to `ShoppingItem` objects).
      - Returns a combined list of `ShoppingItem` objects.
   4. **UI (`ShoppingList._render_category_columns`)**:
      - Groups the received `ShoppingItem`s by category.
      - Renders each category as a section with a header.
      - For each `ShoppingItem`, creates a `QCheckBox` displaying `item.label()` and sets its checked state based on `item.have`.
      - Connects the `stateChanged` signal of each checkbox to a handler.

### 2. Adding a Manual Item
   1. **Trigger**: User fills in the quantity, unit, and name in the manual input fields in the `ShoppingList` UI and clicks "Add".
   2. **UI (`ShoppingList._on_add_manual`)**:
      - Reads the input values.
      - Calls `ShoppingService.add_manual_item(name, qty, unit)`.
   3. **Service (`ShoppingService.add_manual_item`)**:
      - Creates a new `ShoppingList` model instance with the provided details (`have` defaults to `False`).
      - Saves the new instance to the database.
   4. **UI**: Clears the input fields and calls `load_shopping_list` again to refresh the displayed list, including the new manual item.

### 3. Toggling Item "Have" Status
   1. **Trigger**: User clicks the checkbox next to an item in the `ShoppingList` UI.
   2. **UI (Checkbox `stateChanged` handler in `_build_category_section`)**:
      - The handler receives the `ShoppingItem` associated with the checkbox.
      - It calls `item.toggle_have()` to update the Pydantic model's state in memory.
      - **If the item is manual (`item.source == "manual"`)**:
         - It calls `item.to_model().save()` to persist the change directly to the `ShoppingList` table entry.
      - **If the item is from a recipe (`item.source == "recipe"`)**:
         - It calls `ShoppingState.update_state(key=item.key(), quantity=item.quantity, unit=item.unit or "", checked=item.have)`. This saves or updates the record in the `shopping_states` table, remembering that this specific ingredient (e.g., "flour by cup") is now checked or unchecked.

### 4. Clearing Manual Items
   1. **Trigger**: (Assuming a button or action exists for this, though not explicitly detailed in provided snippets for the UI, the service method exists).
   2. **Service (`ShoppingService.clear_manual_items`)**:
      - Fetches all records from the `ShoppingList` table.
      - Deletes each record.
   3. **UI**: Would need to call `load_shopping_list` to refresh and show that manual items are gone.

## 💾 Database Interaction

-   **`shopping_list` Table**:
    -   Stores items manually added by the user.
    -   Directly managed by `ShoppingService` methods like `add_manual_item`, `clear_manual_items`, and implicitly when a manual item's `have` status is toggled via the UI (which saves the `ShoppingList` model).
-   **`shopping_states` Table**:
    -   Stores the `checked` status, last known `quantity`, and `unit` for ingredients, primarily those derived from recipes.
    -   `ShoppingService.generate_shopping_list` reads from this table (via `ShoppingState.get_state`) to apply persisted states to newly generated lists.
    -   The UI, when an item from a recipe is checked/unchecked, triggers an update to this table via `ShoppingState.update_state`. This ensures that if a recipe changes, and an ingredient's quantity is altered, the system can intelligently decide if it should remain checked (e.g., if the user previously had enough and checked it).

## 💡 Notes and Considerations

-   **Unit Conversion**: The `_CONVERSIONS` dictionary in `ShoppingService` is a key part of standardizing ingredient units. It's designed to be extendable.
-   **State Persistence Logic**: The separation of `ShoppingList` (for manual items) and `ShoppingState` (for recipe item states) is important. `ShoppingState` allows the "checked" status to be remembered even if the underlying recipe requirements change, as it keys off the ingredient name and unit.
-   **Circular Imports**: Local imports are used in some model and service methods (e.g., `ShoppingItem` importing `ShoppingList` within a method, or services importing models within methods) to avoid circular dependency issues at module load time.
-   **Debugging**: `DebugLogger` is used within the services and models for logging operations, which is helpful for development and troubleshooting.

This documentation should provide a solid understanding of the Shopping List package.
