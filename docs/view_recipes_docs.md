# ViewRecipes Package Documentation

The `ViewRecipes` package is located in `views/view_recipes/` and is responsible for displaying a list of recipes to the user. It allows for filtering, sorting, and selecting recipes.

## Files

*   `__init__.py`: Initializes the Python package.
*   `view_recipes.py`: Contains the main logic and UI for displaying recipes.

## `view_recipes.py`

This file defines the `ViewRecipes` class, which is the primary component for viewing recipes.

### `ViewRecipes` Class

**Inherits from:** `PySide6.QtWidgets.QWidget`

**Purpose:**
The `ViewRecipes` class dynamically displays recipes in a responsive and scrollable layout. It uses `RecipeCard` instances to represent individual recipes. Users can filter recipes by category, sort them (e.g., A-Z), and toggle a "Show Favorites Only" view. It also supports a "meal selection" mode where clicking a recipe emits a signal, useful for integrating with features like a meal planner.

**Signals:**

*   `recipe_selected = Signal(int)`:
    *   Emitted when a recipe is clicked, primarily when `meal_selection` mode is enabled.
    *   The signal carries the `id` (integer) of the selected recipe.

**Key Attributes:**

*   `meal_selection (bool)`: If `True`, enables a selection mode where clicking a recipe card triggers the `recipe_selected` signal.
*   `main_layout (QVBoxLayout)`: The main vertical layout for the widget.
*   `lyt_cb (QHBoxLayout)`: Horizontal layout for filter and sort controls.
*   `cb_filter (ComboBox)`: Combobox for selecting a recipe category to filter by.
*   `cb_sort (ComboBox)`: Combobox for selecting the sort order.
*   `chk_favorites (QCheckBox)`: Checkbox to toggle display of only favorite recipes.
*   `scroll_area (QScrollArea)`: The area that allows scrolling through the recipe widgets.
*   `scroll_container (QWidget)`: The widget placed inside the `scroll_area` that contains the `flow_layout`.
*   `flow_layout (FlowLayout)`: A custom layout (defined as an inner class) that arranges recipe widgets in a flowing, responsive manner.
*   `recipes_loaded (bool)`: Flag to track if recipes have been initially loaded.

**Methods:**

*   `__init__(self, parent=None, meal_selection=False)`:
    *   Initializes the `ViewRecipes` widget.
    *   Sets up the UI by calling `build_ui()`.
    *   Sets the `meal_selection` mode.
    *   Initializes `recipes_loaded` to `False`. Recipes are loaded the first
        time the page is shown.
    *   `parent`: The parent widget.
    *   `meal_selection`: Boolean indicating if the widget is in recipe selection mode.

*   `build_ui(self)`:
    *   Creates and configures the main layout and all UI elements:
        *   Filter `ComboBox` (`cb_filter`) populated with `RECIPE_CATEGORIES`.
        *   Sort `ComboBox` (`cb_sort`) populated with `SORT_OPTIONS`.
        *   "Show Favorites Only" `QCheckBox` (`chk_favorites`).
        *   `QScrollArea` (`scroll_area`) for recipe display.
        *   `QWidget` (`scroll_container`) and the custom `FlowLayout` (`flow_layout`) to hold `RecipeCard` instances.
    *   Connects signals from `cb_filter`, `cb_sort`, and `chk_favorites` to their respective handler methods (`handle_filter_change`, `handle_sort_change`, `load_filtered_sorted_recipes`).

*   `handle_filter_change(self, selected_category: str)`:
    *   Slot that is called when the text in `cb_filter` (filter combobox) changes.
    *   Triggers `load_filtered_sorted_recipes()` to update the displayed recipes based on the new filter.
    *   `selected_category`: The category string selected in the combobox.

*   `handle_sort_change(self, selected_sort: str)`:
    *   Slot that is called when the text in `cb_sort` (sort combobox) changes.
    *   Triggers `load_filtered_sorted_recipes()` to update the displayed recipes based on the new sort order.
    *   `selected_sort`: The sort option string selected in the combobox.

*   `load_filtered_sorted_recipes(self)`:
    *   Retrieves the current filter category from `cb_filter`, sort option from `cb_sort`, and the state of `chk_favorites`.
    *   Calls `clear_recipe_display()` to remove existing recipe widgets.
    *   Fetches filtered and sorted recipes using `RecipeService.list_filtered()`, which loads recipes from a persistent cache file for fast access.
    *   For each fetched recipe, creates a `RecipeCard`, sets its recipe data, connects its `card_clicked` signal if in `meal_selection` mode, and adds it to the `flow_layout`.

*   `clear_recipe_display(self)`:
    *   Removes all recipe widgets currently displayed in the `flow_layout`.
    *   Ensures proper cleanup by calling `deleteLater()` on each widget.

*   `load_recipes(self)`:
    *   Fetches all recipes from the database using `Recipe.all()`.
    *   Clears the current display using `clear_recipe_display()`.
    *   Populates the `flow_layout` with `RecipeCard` instances for each recipe.
    *   If `meal_selection` is `True`, connects the `card_clicked` signal of each `RecipeCard` to `self.select_recipe`.
    *   Sets `self.recipes_loaded` to `True`.

*   `select_recipe(self, recipe_id: int)`:
    *   Emits the `recipe_selected` signal with the `recipe_id`.
    *   `recipe_id`: The ID of the recipe that was selected.

*   `refresh(self)`:
    *   Forces a complete refresh of the recipe display by clearing the current widgets and calling `load_filtered_sorted_recipes()`.
    *   Useful for updating the view after changes have been made elsewhere (e.g., adding/editing a recipe).

*   `showEvent(self, event: QShowEvent)`:
    *   Overrides the `QWidget.showEvent()`.
    *   Always reloads recipes by calling `load_filtered_sorted_recipes()` when the widget becomes visible. Recipe data is served from the cached file to avoid unnecessary database reads.
    *   `event`: The `QShowEvent` object.

*   `create_flow_layout(self, parent: QWidget) -> FlowLayout`:
    *   Factory method that creates and returns an instance of the inner `FlowLayout` class.
    *   `parent`: The parent widget for the `FlowLayout`.

### Inner Class: `FlowLayout`

**Inherits from:** `PySide6.QtWidgets.QLayout`

**Purpose:**
A custom layout manager that arranges child widgets (e.g., `RecipeCard` instances) in a flow. Widgets are added horizontally until the available width is exceeded, at which point they wrap to the next line. The layout attempts to center the items in each row.

**Key Methods (Overrides from `QLayout`):**

*   `__init__(self, parent=None, margin=0, spacing=45)`: Constructor.
*   `addItem(self, item: QLayoutItem)`: Adds an item to the layout's internal list.
*   `count(self) -> int`: Returns the number of items in the layout.
*   `itemAt(self, index: int) -> QLayoutItem`: Returns the item at the given index.
*   `takeAt(self, index: int) -> QLayoutItem`: Removes and returns the item at the given index.
*   `expandingDirections(self) -> Qt.Orientation`: Returns `Qt.Orientation(0)` (no expansion).
*   `hasHeightForWidth(self) -> bool`: Returns `True` as height depends on width for wrapping.
*   `heightForWidth(self, width: int) -> int`: Calculates the required height for a given width by simulating the layout.
*   `setGeometry(self, rect: QRect)`: Called when the layout's geometry is set. Triggers `doLayout`.
*   `sizeHint(self) -> QSize`: Returns the preferred size, which is the minimum size.
*   `minimumSize(self) -> QSize`: Calculates the minimum size required to display all items (without wrapping, typically).
*   `doLayout(self, rect: QRect, testOnly: bool) -> int`:
    *   The core logic for arranging items within the given `rect`.
    *   Iterates through items, placing them in rows. When a row is full, it moves to the next line.
    *   Calculates horizontal offsets to center the items within each row.
    *   If `testOnly` is `True`, it only calculates the height without actually moving widgets.
    *   Returns the height occupied by the laid-out items.

This documentation provides an overview of the `ViewRecipes` module, its main class, and the custom `FlowLayout` used for displaying recipe cards.
