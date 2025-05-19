# Meal Planner Package Documentation

This document provides a detailed overview of the Meal Planner package, its components, and their interactions.

## Overview

The Meal Planner package is responsible for allowing users to create, view, and manage meal plans. It consists of several key components:

-   **`MealPlanner` (QWidget)**: The main UI container for the meal planning interface. It uses a `QTabWidget` to manage multiple meal tabs.
-   **`MealWidget` (QWidget)**: Represents a single meal, containing a main dish and up to three side dishes. Each dish is represented by a `RecipeWidget`.
-   **`PlannerService`**: Handles the business logic for loading and saving the state of the meal planner, such as which meal tabs are open.
-   **`MealService` (from `services` package)**: Handles CRUD operations for individual `MealSelection` objects (the data model for a meal).

## File Structure

```
views/meal_planner/
├── __init__.py                 # Initializes the package
├── meal_planner.py             # Contains the MealPlanner class (main UI)
├── meal_widget.py              # Contains the MealWidget class (single meal UI)
├── planner_service.py          # Service for managing planner state
└── meal_planner_docs.md        # This documentation file
```

## Core Components

### 1. `MealPlanner` (`meal_planner.py`)

The `MealPlanner` class is the central UI component for this package.

-   **Purpose**: To provide a tabbed interface where each tab can represent a `MealWidget` for planning a specific meal.
-   **Key Features**:
    -   Uses `QTabWidget` to display multiple meal tabs.
    -   A special "+" tab allows users to add new meal tabs.
    -   Manages a `tab_map` dictionary to keep track of `MealWidget` instances associated with each tab.
    -   Interacts with `PlannerService` to load and save the list of active meal IDs (which tabs were open).
    -   Handles tab clicks, specifically for the "+" tab to trigger the creation of a new meal.
-   **Initialization (`init_ui`)**:
    -   Creates the "+" tab.
    -   Loads previously saved meal IDs using `PlannerService.load_saved_meal_ids()`.
    -   For each loaded meal ID, it calls `add_meal_tab()` to create and populate a tab.
    -   If no meals were saved, it opens one new empty meal tab by default.
-   **Adding a Meal Tab (`add_meal_tab`)**:
    -   Creates a new `MealWidget`.
    -   If a `meal_id` is provided, it loads the corresponding meal data into the `MealWidget`.
    -   Adds the `MealWidget` to a new tab in the `QTabWidget`.
    -   Updates the `tab_map`.
-   **Saving (`save_meal_plan`)**:
    -   Iterates through all `MealWidget` instances in `tab_map` and calls their `save_meal()` method.
    -   Retrieves the list of currently active (and valid) meal IDs.
    -   Calls `PlannerService.save_active_meal_ids()` to persist this list.

### 2. `MealWidget` (`meal_widget.py`)

The `MealWidget` class represents the UI for a single meal.

-   **Purpose**: To display and manage the selection of a main recipe and up to three side recipes for a meal.
-   **Key Features**:
    -   Contains one `RecipeWidget` for the main dish (medium size) and three `RecipeWidget` instances for side dishes (small size).
    -   Side dish `RecipeWidget`s are initially disabled and enabled only after a main dish is selected.
    -   Holds an internal `_meal_model` (an instance of `MealSelection` from `database.models`) which stores the data for the current meal.
    -   Connects signals from its child `RecipeWidget`s to update its `_meal_model` when a recipe is selected or changed.
-   **UI Setup (`_setup_ui`)**:
    -   Arranges `RecipeWidget`s in a horizontal layout (main dish on the left, side dishes stacked vertically on the right).
-   **Loading a Meal (`load_meal`)**:
    -   Takes a `meal_id`.
    -   Uses `MealService.load_meal()` to fetch the `MealSelection` data.
    -   Populates its main and side dish `RecipeWidget`s with the recipes from the loaded `_meal_model`.
-   **Saving a Meal (`save_meal`)**:
    -   If the `_meal_model` does not have an ID (i.e., it's a new meal), it calls `MealService.create_meal()` to save it to the database and updates `_meal_model` with the returned instance (which now has an ID).
    -   If the `_meal_model` already has an ID, it calls `MealService.update_meal()` to save any changes.
-   **Recipe Selection (`update_recipe_selection`)**:
    -   Called when a `RecipeWidget` within the `MealWidget` signals a recipe change.
    -   Updates the corresponding field in its `_meal_model` (e.g., `main_recipe_id`, `side_recipe_1`).

### 3. `PlannerService` (`planner_service.py`)

The `PlannerService` class handles the persistence of the Meal Planner's overall state.

-   **Purpose**: To save and load which meals are currently open in the `MealPlanner` tabs, without dealing with the content of the meals themselves.
-   **Key Features**:
    -   **`load_saved_meal_ids() -> list[int]`**:
        -   Retrieves all entries from the `SavedMealState` database table.
        -   Returns a list of `meal_id`s.
    -   **`save_active_meal_ids(meal_ids: list[int]) -> None`**:
        -   Clears all existing entries in the `SavedMealState` table.
        -   For each `meal_id` in the provided list, creates and saves a new `SavedMealState` entry.
    -   **`clear_planner_state() -> None`**:
        -   Deletes all entries from the `SavedMealState` table, effectively resetting the saved planner state.
    -   **`validate_meal_ids(meal_ids: list[int]) -> list[int]`**:
        -   Checks each `meal_id` in the input list against the `MealSelection` table to ensure it corresponds to an existing meal.
        -   Returns a list containing only the valid `meal_id`s.

### 4. `MealService` (Located in `services/meal_service.py`)

While not part of the `views/meal_planner` directory, `MealService` is crucial for the functioning of the Meal Planner.

-   **Purpose**: To provide CRUD (Create, Read, Update, Delete) operations for `MealSelection` objects.
-   **Key Methods Used by Meal Planner**:
    -   **`create_meal(meal: MealSelection) -> MealSelection`**: Saves a new `MealSelection` instance to the database and returns it with an assigned ID.
    -   **`update_meal(meal: MealSelection) -> None`**: Updates an existing `MealSelection` record in the database.
    -   **`load_meal(meal_id: int) -> Optional[MealSelection]`**: Retrieves a `MealSelection` record from the database by its ID.

## Data Models Involved

-   **`MealSelection` (`database/models/meal_selection.py`)**:
    -   Represents a single meal.
    -   Fields: `id`, `meal_name`, `main_recipe_id`, `side_recipe_1`, `side_recipe_2`, `side_recipe_3`.
    -   Provides methods like `get_main_recipe()`, `get_side_recipes()`, `get_all_recipes()`.
-   **`SavedMealState` (`database/models/saved_meal_state.py`)**:
    -   Represents a single meal ID that was active in the planner.
    -   Fields: `id`, `meal_id`. Used by `PlannerService` to persist the set of open meal tabs.
-   **`Recipe` (`database/models/recipe.py`)**:
    -   Represents a recipe. Referenced by `MealSelection`.

## Workflow Example: Loading the Meal Planner

1.  The application starts, and the main window initializes `MealPlanner`.
2.  `MealPlanner.__init__` calls `MealPlanner.init_ui()`.
3.  `init_ui` calls `PlannerService.load_saved_meal_ids()` to get a list of meal IDs that were open in the last session.
4.  For each `meal_id` returned:
    a.  `MealPlanner.add_meal_tab(meal_id)` is called.
    b.  `add_meal_tab` creates a new `MealWidget`.
    c.  The new `MealWidget` calls its `load_meal(meal_id)` method.
    d.  `MealWidget.load_meal()` calls `MealService.load_meal(meal_id)` to fetch the `MealSelection` data.
    e.  The `MealSelection` data is used to populate the `_meal_model` of the `MealWidget`.
    f.  The `RecipeWidget`s within the `MealWidget` are updated to display the main and side recipes based on the IDs in `_meal_model`.
5.  The `MealPlanner` displays the tabs, each populated with the corresponding meal information.

## Workflow Example: Saving a Meal

1.  A user modifies a recipe selection in a `MealWidget`.
2.  The `RecipeWidget` signals the change.
3.  `MealWidget.update_recipe_selection()` updates its internal `_meal_model` with the new `recipe_id`.
4.  When the application is about to close or when a save action is triggered, `MealPlanner.save_meal_plan()` is called.
5.  `save_meal_plan()` iterates through each `MealWidget` in its `tab_map`:
    a.  It calls `MealWidget.save_meal()`.
    b.  `MealWidget.save_meal()` checks if its `_meal_model.id` is `None`.
        i.  If `None` (new meal): Calls `MealService.create_meal(self._meal_model)`. The returned `MealSelection` (with an ID) updates `self._meal_model`.
        ii. If an ID exists (existing meal): Calls `MealService.update_meal(self._meal_model)`.
6.  After all `MealWidget`s have saved their state, `MealPlanner.save_meal_plan()` calls `PlannerService.save_active_meal_ids()` with the list of current meal IDs to save the tab configuration.

This documentation provides a comprehensive guide to the Meal Planner package.
