# RecipeCard Package Documentation

The `RecipeCard` package is a UI component designed to display recipe information in various states and formats within a Qt-based application. It provides a flexible and interactive way for users to view recipe cards, full recipe details, and manage recipe selections.

## Core Components

### 1. `RecipeCard` (recipe_card.py)

The main class of the package. It acts as a container that can display different frames based on the current state:

-   **Empty State**: Shown when no recipe is loaded. Displays an "Add Meal" button to allow users to select a recipe.
-   **Recipe State**: Displays a recipe card (small, medium, or large) when a recipe is loaded.
-   **Error State**: Shown if there's an issue loading or displaying a recipe.

**Key Features:**

-   Manages a `QStackedWidget` to switch between different state frames.
-   Uses `FrameFactory` to build the appropriate frame for each state.
-   Emits signals for user interactions:
    -   `add_meal_clicked`: When the "Add Meal" button in the empty state is clicked.
    -   `card_clicked(Recipe)`: When a populated recipe card is clicked.
    -   `delete_clicked(int)`: (Reserved for future use) When a delete action is triggered.
    -   `recipe_selected(int)`: When a recipe is successfully loaded into the widget.
-   Handles recipe selection through `RecipeSelectionDialog`.
-   Displays full recipe details using the `FullRecipe` dialog when a card is clicked.

**Initialization:**

```python
from recipe_card import RecipeCard
from recipe_card.constants import LayoutSize

# Create a medium-sized recipe widget
recipe_card = RecipeCard(size=LayoutSize.MEDIUM)
```

**Usage:**

```python
from app.core.data.models.recipe import Recipe

# Assuming 'my_recipe' is an instance of the Recipe model
recipe_card.set_recipe(my_recipe)

# To clear the widget and show the empty state
recipe_card.set_recipe(None)

# Connect to signals
recipe_card.add_meal_clicked.connect(my_add_meal_handler)
recipe_card.card_clicked.connect(my_card_click_handler)
```

### 2. `FrameFactory` (frame_factory.py)

A factory class responsible for creating and returning the appropriate `QFrame` for a given state (`"recipe"`, `"empty"`, `"error"`) and size (`LayoutSize`). It delegates the actual frame building to specific builder classes.

**Usage:**

```python
from recipe_card.frame_factory import FrameFactory
from recipe_card.constants import LayoutSize
from app.core.data.models.recipe import Recipe

# Get an empty state frame
empty_frame = FrameFactory.make("empty", LayoutSize.SMALL)

# Get a recipe card frame
# Assuming 'a_recipe' is an instance of the Recipe model
recipe_frame = FrameFactory.make("recipe", LayoutSize.MEDIUM, recipe=a_recipe)
```

### 3. `constants.py`

Defines constants and enumerations used throughout the `RecipeCard` package.

-   `LAYOUT_SIZE`: A dictionary mapping layout size names (e.g., "small") to `QSize` objects.
-   `ICON_COLOR`: Default color for icons within the widget.
-   `LayoutSize (Enum)`: An enumeration (`SMALL`, `MEDIUM`, `LARGE`) defining the target sizes for recipe cards.

## Builders (`recipe_card/builders/`)

This sub-package contains classes responsible for constructing the specific `QFrame` layouts for different states and views.

### 1. `RecipeCard` (recipe_card.py)

Builds the visual representation of a recipe card. It supports different layouts based on the `LayoutSize` (small, medium). The large layout is not yet implemented.

-   **Small Layout**: Displays the recipe image and recipe name horizontally.
-   **Medium Layout**: Displays the recipe image, recipe name, and metadata (servings, total time) vertically.

### 2. `EmptyState` (empty_state.py)

Builds the frame displayed when no recipe is loaded. It primarily consists of an "Add Meal" button.

### 3. `ErrorState` (error_state.py)

Builds the frame displayed when an error occurs (e.g., failing to load or render a recipe). It shows an error message.

### 4. `FullRecipe` (full_recipe.py)

This class is a `DialogWindow` that displays the complete details of a recipe. It's not just a frame builder but a fully functional dialog.

**Key Features:**

-   Displays recipe name, image, metadata (servings, time, category).
-   Shows a list of ingredients.
-   Shows step-by-step cooking directions.
-   Organized into a header and two columns (left: image & ingredients; right: metadata & directions).

## Dialogs (`recipe_card/dialogs/`)

### 1. `RecipeSelectionDialog` (recipe_selection_dialog.py)

A `DialogWindow` that allows users to select a recipe from a list of available recipes.

**Key Features:**

-   Populates a `QListWidget` with recipe names.
-   Allows single recipe selection.
-   Returns the selected `Recipe` object.
-   Triggered by the `RecipeCard` when the "Add Meal" button is clicked in the empty state.

## How It Works

1.  A `RecipeCard` is initialized with a specific `LayoutSize`.
2.  Initially, it displays the "empty" state frame, built by `EmptyState` via `FrameFactory`.
3.  If the user clicks the "Add Meal" button on the empty state:
    a.  The `_handle_add_meal_click` method in `RecipeCard` is called.
    b.  It fetches all recipes from the database.
    c.  A `RecipeSelectionDialog` is shown.
    d.  If the user selects a recipe and confirms, `RecipeCard.set_recipe()` is called with the chosen recipe.
4.  When `RecipeCard.set_recipe(recipe)` is called:
    a.  If `recipe` is `None`, the widget switches to the "empty" state.
    b.  If `recipe` is a `Recipe` object:
        i.  `FrameFactory.make("recipe", self._size, recipe)` is called.
        ii. `RecipeCard` constructs the recipe card frame based on the widget's size and the provided recipe data.
        iii. The `RecipeCard` replaces its current recipe frame with the new one and switches the `QStackedWidget` to display it.
        iv. The `recipe_selected` signal is emitted.
5.  If the user clicks on a displayed recipe card:
    a.  The `_emit_card_clicked` method in `RecipeCard` is called.
    b.  The `card_clicked` signal is emitted.
    c.  A `FullRecipe` dialog is instantiated with the clicked recipe and displayed modally.
6.  If any error occurs during recipe card building, the `RecipeCard` switches to the "error" state frame, built by `ErrorState`.

## Styling

-   The components make use of Qt StyleSheets for appearance.
-   Object names (e.g., `"RecipeCard"`, `"EmptyStateFrame"`, `"AddMealButton"`) are set on widgets to allow for targeted styling.
-   Custom properties (e.g., `"layout_size"`, `"title_text"`) are used on widgets, potentially for styling or logic.
-   Icons are managed via the `ui.iconkit` module.

## Dependencies

-   `PySide6`: For Qt GUI elements.
-   `core.helpers.DebugLogger`: For logging.
-   `database.models.recipe.Recipe`: The data model for recipes.
-   `config`: For application-level configurations (e.g., icon paths, theme colors).
-   `ui.components`: For shared UI elements like `Separator`, `RoundedImage`, `DialogWindow`.
-   `ui.iconkit`: For icon management.
-   `ui.styles`: For theming.
-   `ui.tools.layout_debugger`: For debugging layout issues.

This documentation provides an overview of the `RecipeCard` package, its components, and their interactions. For more specific details, refer to the source code and docstrings within each file.
