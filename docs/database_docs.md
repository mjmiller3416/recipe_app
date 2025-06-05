# 📊 Database Package Overview

This section documents the structure and functionality of the database package for the MealGenie application. This package handles all database operations, model definitions, and data access patterns using a modern Pydantic-based ORM with SQLite.

---

## 📂 File Structure

```
└── 📁database
    ├── __init__.py
    ├── app_data.db
    ├── base_model.py
    ├── db.py
    ├── db_reset.py
    ├── init_db.py
    ├── 📁migrations
    │   ├── 001_initial.sql
    │   ├── 002_meal_logs.sql
    │   ├── 003_recipe_history.sql
    │   ├── 004_saved_meal_state.sql
    │   ├── 005_shopping_state.sql
    │   ├── 006_add_created_at.sql
    │   ├── 007_add_favorites.sql
    │   └── 008_add_meal_type.sql
    └── 📁models
        ├── __init__.py
        ├── ingredient.py
        ├── meal_log.py
        ├── meal_selection.py
        ├── recipe.py
        ├── recipe_history.py
        ├── recipe_ingredient.py
        ├── saved_meal_state.py
        ├── schema_version.py
        ├── shopping_item.py
        ├── shopping_list.py
        ├── shopping_state.py
        └── weekly_menu.py
```

---

## 📄 Core Database Files

### 📄 db.py

**Path:** database/db.py

#### 📝 Purpose
Main database connection manager for SQLite operations, providing context-managed connections with automatic transaction handling.

#### ⚙️ Core Components

**Constants:**
- `DB_PATH`: Path to the SQLite database file (`app_data.db`)

**Functions:**
- **`get_connection() -> sqlite3.Connection`**:
  - Context manager for SQLite database connections
  - Automatically sets `row_factory` to `sqlite3.Row` for dictionary-like access
  - Handles transaction management:
    - Commits on successful completion
    - Rolls back on exceptions
    - Always closes the connection
  - **Usage Example:**
    ```python
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM recipes")
        # Automatically commits on success
    ```

---

### 📄 base_model.py

**Path:** database/base_model.py

#### 📝 Purpose
Provides a Pydantic-based base class for all database models with generic CRUD operations and ORM-like functionality.

#### ⚙️ Core Class: `ModelBase`

**Inheritance:** Inherits from `pydantic.BaseModel`

**Base Attributes:**
- `id: Optional[int] = None` - Primary key for all models

**Class Methods:**
- **`table_name() -> str`**:
  - Automatically generates table names from class names
  - Converts CamelCase to snake_case with proper pluralization
  - Example: `RecipeIngredient` → `recipe_ingredients`

- **`all() -> List[T]`**:
  - Fetches all records from the table
  - Returns a list of model instances

- **`get(id: int) -> Optional[T]`**:
  - Fetches a single record by primary key
  - Returns the model instance or `None` if not found

- **`raw_query(sql: str, params: Tuple = (), connection: Optional[sqlite3.Connection] = None) -> List[T]`**:
  - Executes raw SQL queries and returns model instances
  - Supports parameterized queries for SQL injection prevention
  - Optional connection parameter for transaction management
  - Automatically converts `sqlite3.Row` objects to model instances

- **`update(id: int, connection: Optional[sqlite3.Connection] = None, **fields: Any) -> Optional[T]`**:
  - Updates specific fields on a record by ID
  - Returns the updated model instance or `None` if record not found
  - Supports transaction management through optional connection

- **`exists(**fields: Any) -> bool`**:
  - Checks if a record exists with given field-value pairs
  - Returns `True` if matching record exists, `False` otherwise

- **`filter(**filters: Any) -> List[T]`**:
  - Filters records based on field-value pairs
  - Builds SQL WHERE clauses automatically
  - Returns list of matching model instances

- **`first(**filters: Any) -> Optional[T]`**:
  - Returns the first record matching the filters
  - Convenience method for single-record queries

- **`get_by_field(**fields: Any) -> Optional[T]`**:
  - Alias for `first()` method
  - Returns single record matching field-value pairs

- **`join_query(join_clause: str, where_clause: str = "", params: Tuple = ()) -> List[T]`**:
  - Executes JOIN queries and returns model instances
  - Supports complex relational queries
  - Maintains model instance return type

**Instance Methods:**
- **`save(connection: Optional[sqlite3.Connection] = None) -> T`**:
  - Saves the model instance to the database using `INSERT OR REPLACE`
  - Sets the `id` field for new records
  - Supports transaction management through optional connection
  - Returns the saved instance

- **`delete(connection: Optional[sqlite3.Connection] = None) -> None`**:
  - Deletes the record from the database
  - Raises `ValueError` if record has no ID (unsaved record)
  - Supports transaction management

**Design Features:**
- **Pydantic Integration**: Full validation and serialization support
- **Transaction Management**: Optional connection parameters for atomic operations
- **Type Safety**: Generic type variables ensure proper return types
- **SQL Injection Prevention**: All queries use parameterized statements
- **Flexible Querying**: Support for raw SQL, filters, and joins

---

### 📄 init_db.py

**Path:** database/init_db.py

#### 📝 Purpose
Handles database initialization and migration management by applying SQL migration files sequentially.

#### ⚙️ Core Components

**Constants:**
- `MIGRATIONS_DIR`: Path to the migrations directory containing SQL files

**Functions:**
- **`init_db() -> None`**:
  - Initializes or migrates the database by applying pending SQL scripts
  - **Process:**
    1. Creates `schema_version` table if it doesn't exist
    2. Fetches list of already applied migrations
    3. Sorts and processes all `.sql` files in migrations directory
    4. Skips already applied migrations
    5. Executes new migration SQL scripts
    6. Records applied migrations in `schema_version` table
  - **Features:**
    - Idempotent operation (safe to run multiple times)
    - Sequential migration application
    - Automatic migration tracking
    - Console logging of applied migrations

**Usage:**
- Called automatically during application startup
- Can be run standalone: `python database/init_db.py`

---

### 📄 db_reset.py

**Path:** database/db_reset.py

#### 📝 Purpose
Provides database reset functionality for development and testing environments.

#### ⚙️ Core Functions

- **`reset_database() -> None`**:
  - Completely resets the database by deleting and recreating it
  - **Process:**
    1. Deletes existing database file if it exists
    2. Calls `init_db()` to recreate database with migrations
    3. Logs the reset process
    4. Exits the application after completion
  - **Safety Features:**
    - Logs all operations for debugging
    - Graceful handling of missing database files
    - Clean application exit after reset

**Usage:**
- Development environment database refresh
- Testing environment cleanup
- Recovery from corrupted database states

---

## 📁 Migrations Package

The migrations directory contains SQL scripts for database schema evolution, applied sequentially by the migration system:

### Migration Files

- **`001_initial.sql`** - Initial database schema creation
  - Creates core tables: `recipes`, `ingredients`, `meal_selections`, `shopping_lists`, `meal_logs`, `recipe_ingredients`
  - Establishes foreign key relationships
  - Sets up basic table structure

- **`002_meal_logs.sql`** - Enhanced meal logging functionality
  - Adds meal logging capabilities
  - Tracks meal preparation and consumption

- **`003_recipe_history.sql`** - Recipe usage tracking
  - Adds `recipe_histories` table
  - Tracks when recipes are cooked
  - Enables recipe suggestion algorithms

- **`004_saved_meal_state.sql`** - Meal planner state persistence
  - Adds `saved_meal_state` table
  - Persists active meal planner selections

- **`005_shopping_state.sql`** - Shopping list state management
  - Adds `shopping_state` table
  - Tracks checked/unchecked status of shopping items
  - Enables persistent shopping list interactions

- **`006_add_created_at.sql`** - Timestamp tracking
  - Adds `created_at` fields to existing tables
  - Enables creation date tracking across models

- **`007_add_favorites.sql`** - Favorites system
  - Adds favorites functionality to recipes
  - Enables user preference tracking

- **`008_add_meal_type.sql`** - Meal categorization
  - Adds meal type categorization (breakfast, lunch, dinner)
  - Enhances recipe organization capabilities

---

## 📁 Models Package

### 📄 ingredient.py

**Path:** database/models/ingredient.py

#### 📝 Purpose
Defines the `Ingredient` model for managing ingredient data with CRUD operations and relationship management.

#### ⚙️ Core Class: `Ingredient`

**Attributes:**
- `id: Optional[int]` - Primary key
- `ingredient_name: str` - Name of the ingredient (validated, min_length=1)
- `ingredient_category: str` - Category of the ingredient (validated, min_length=1)

**Validation:**
- **`strip_strings` validator**: Automatically trims whitespace from string fields before validation

**Methods:**
- **`display_label() -> str`**: Returns a human-friendly label in format "Name (Category)"
- **`get_recipes(connection: Optional[sqlite3.Connection] = None) -> List[Recipe]`**: 
  - Returns all recipes that include this ingredient
  - Uses JOIN query to fetch related recipes through `recipe_ingredients` table
  - Supports optional connection parameter for transaction management

**Usage Example:**
```python
ingredient = Ingredient(ingredient_name="Flour", ingredient_category="Baking")
ingredient.save()
recipes = ingredient.get_recipes()  # Get all recipes using this ingredient
```

---

### 📄 recipe.py

**Path:** database/models/recipe.py

#### 📝 Purpose
Defines the `Recipe` model for managing recipe data with full CRUD operations, ingredient relationships, and cooking history tracking.

#### ⚙️ Core Class: `Recipe`

**Attributes:**
- `id: Optional[int]` - Primary key
- `recipe_name: str` - Recipe name (validated, min_length=1)
- `recipe_category: str` - Recipe category (validated, min_length=1)
- `meal_type: str` - Meal type (default="Dinner", min_length=1)
- `total_time: Optional[int]` - Total cooking time in minutes
- `servings: Optional[int]` - Number of servings
- `directions: Optional[str]` - Cooking instructions
- `image_path: Optional[str]` - Path to recipe image
- `created_at: datetime` - Creation timestamp (auto-generated)
- `is_favorite: bool` - Favorite status (default=False)

**Validation:**
- **`strip_strings` validator**: Automatically trims whitespace from string fields and directions

**Class Methods:**
- **`recent(days: int = 30) -> List[Recipe]`**: 
  - Returns recipes created in the last N days
  - Ordered by creation date descending
- **`list_all() -> List[Recipe]`**: 
  - Returns all recipes ordered by creation date
- **`suggest(days: int) -> List[Recipe]`**: 
  - Returns recipes that haven't been cooked in the last N days
  - Uses `last_cooked()` method to determine eligibility

**Instance Methods:**
- **`formatted_time() -> str`**: Returns time formatted as "Xh Ym" or "Ym"
- **`formatted_servings() -> str`**: Returns servings as string
- **`get_recipe_ingredients(connection: Optional[sqlite3.Connection] = None) -> List[RecipeIngredient]`**: 
  - Returns all RecipeIngredient link objects for this recipe
- **`get_ingredients(connection: Optional[sqlite3.Connection] = None) -> List[Ingredient]`**: 
  - Returns all Ingredient models linked to this recipe
- **`last_cooked(connection: Optional[sqlite3.Connection] = None) -> Optional[datetime]`**: 
  - Returns the last time this recipe was cooked from recipe_histories table
- **`get_directions_list() -> list[str]`**: 
  - Returns each non-empty line of directions as a separate step
- **`get_ingredient_details(connection: Optional[sqlite3.Connection] = None) -> List[IngredientDetail]`**: 
  - Returns consolidated ingredient details using RecipeIngredient relationships

**Usage Example:**
```python
recipe = Recipe(
    recipe_name="Chocolate Cake",
    recipe_category="Dessert",
    meal_type="Dessert",
    total_time=90,
    servings=8
)
recipe.save()
ingredients = recipe.get_ingredients()
last_made = recipe.last_cooked()
```

---

### 📄 recipe_ingredient.py

**Path:** database/models/recipe_ingredient.py

#### 📝 Purpose
Defines the `RecipeIngredient` model for managing the many-to-many relationship between recipes and ingredients with quantity and unit information.

#### ⚙️ Supporting Classes

**`IngredientDetail` (NamedTuple):**
- `ingredient_name: str`
- `ingredient_category: str`
- `quantity: Optional[float]`
- `unit: Optional[str]`

#### ⚙️ Core Class: `RecipeIngredient`

**Attributes:**
- `recipe_id: int` - Foreign key to recipes table (validated, description provided)
- `ingredient_id: int` - Foreign key to ingredients table (validated, description provided)
- `quantity: Optional[float]` - Quantity for this recipe (description provided)
- `unit: Optional[str]` - Unit of measure for this ingredient (description provided)

**Class Methods:**
- **`table_name() -> str`**: Overrides default pluralization to return "recipe_ingredients"

**Instance Methods:**
- **`get_ingredient_detail() -> IngredientDetail`**: 
  - Fetches the complete ingredient information and combines it with quantity/unit
  - Returns an IngredientDetail NamedTuple for consolidated access
  - Raises ValueError if ingredient not found

**Custom Methods:**
- **`__repr__() -> str`**: Custom string representation for debugging

**Usage Example:**
```python
recipe_ingredient = RecipeIngredient(
    recipe_id=1,
    ingredient_id=5,
    quantity=2.0,
    unit="cups"
)
recipe_ingredient.save()
detail = recipe_ingredient.get_ingredient_detail()  # Get full ingredient info
```

---

### 📄 meal_selection.py

**Path:** database/models/meal_selection.py

#### 📝 Purpose
Defines the `MealSelection` model for managing complete meal configurations with main and side recipes.

#### ⚙️ Core Class: `MealSelection`

**Attributes:**
- `id: Optional[int]` - Primary key
- `meal_name: str` - Name of the meal (validated, min_length=1)
- `main_recipe_id: int` - Foreign key to main recipe (validated, ge=1)
- `side_recipe_1: Optional[int]` - Foreign key to first side recipe
- `side_recipe_2: Optional[int]` - Foreign key to second side recipe
- `side_recipe_3: Optional[int]` - Foreign key to third side recipe

**Validation:**
- **`strip_strings` validator**: Automatically trims whitespace from meal_name

**Instance Methods:**
- **`get_main_recipe() -> Recipe`**: Returns the primary Recipe for this meal
- **`get_side_recipes() -> List[Recipe]`**: Returns any side dish Recipes for this meal
- **`get_all_recipes() -> List[Recipe]`**: Returns all recipes (main and sides) for this meal

**Usage Example:**
```python
meal = MealSelection(
    meal_name="Sunday Dinner",
    main_recipe_id=10,
    side_recipe_1=15,
    side_recipe_2=20
)
meal.save()
all_recipes = meal.get_all_recipes()  # Get main + side recipes
```

---

### 📄 shopping_item.py

**Path:** database/models/shopping_item.py

#### 📝 Purpose
Defines the `ShoppingItem` model as a structured data transfer object for shopping list items, combining recipe-derived and manually added items for unified display.

#### ⚙️ Core Class: `ShoppingItem`

**Inheritance:** Inherits from `pydantic.BaseModel` (not ModelBase - this is a DTO, not a database table)

**Attributes:**
- `ingredient_name: str` - Name of the ingredient (validated, min_length=1)
- `quantity: float` - Quantity needed (validated, ge=0)
- `unit: Optional[str]` - Unit of measurement
- `category: Optional[str]` - Ingredient category
- `source: Literal["recipe", "manual"]` - Source of the item (recipe-derived or manually added)
- `have: bool` - Whether the item has been acquired (default=False)

**Validation:**
- **`strip_name` validator**: Trims whitespace from ingredient_name
- **`normalize_strings` validator**: 
  - Normalizes ingredient_name and unit fields
  - Converts unit to lowercase and removes trailing periods

**Instance Methods:**
- **`label() -> str`**: 
  - Returns formatted display label: "2 cups • Flour"
  - Handles integer vs. decimal quantity display
- **`toggle_have()`**: Toggles the 'have' status for checkbox interactions
- **`key() -> str`**: 
  - Returns normalized key for grouping like ingredients
  - Format: "ingredient_name::unit"
- **`to_model() -> ShoppingList`**: 
  - Converts ShoppingItem back to ShoppingList database model
  - Only works for manual items (raises ValueError for recipe items)

**Usage Example:**
```python
item = ShoppingItem(
    ingredient_name="Flour",
    quantity=2.0,
    unit="cups",
    source="recipe",
    have=False
)
display_text = item.label()  # "2 cups • Flour"
item.toggle_have()  # Mark as acquired
```

---

### 📄 shopping_list.py

**Path:** database/models/shopping_list.py

#### 📝 Purpose
Defines the `ShoppingList` model for managing manually added shopping list items that are persisted in the database.

#### ⚙️ Core Class: `ShoppingList`

**Attributes:**
- `id: Optional[int]` - Primary key
- `ingredient_name: str` - Name of the shopping item (validated, min_length=1)
- `quantity: float` - Item quantity (validated, ge=0)
- `unit: str` - Measurement unit (validated, min_length=1)
- `have: bool` - Whether the item has been acquired (default=False)

**Validation:**
- **`strip_strings` validator**: Trims whitespace from ingredient_name and unit fields

**Instance Methods:**
- **`label() -> str`**: 
  - Returns checklist-style label: "✔ Flour: 2.0 cups" or "✖ Flour: 2.0 cups"
- **`to_item() -> ShoppingItem`**: 
  - Converts database row to ShoppingItem DTO for unified display
  - Sets source as "manual" and category as None

**Usage Example:**
```python
shopping_item = ShoppingList(
    ingredient_name="Milk",
    quantity=1.0,
    unit="gallon",
    have=False
)
shopping_item.save()
display_item = shopping_item.to_item()  # Convert to DTO for UI
```

---

### 📄 shopping_state.py

**Path:** database/models/shopping_state.py

#### 📝 Purpose
Tracks the 'checked' state of shopping list items from recipe sources, persisting checkbox values across sessions while handling dynamic quantity updates.

#### ⚙️ Core Class: `ShoppingState`

**Attributes:**
- `key: str` - Normalized key for the shopping item (ingredient_name::unit)
- `quantity: float` - Current quantity for the item
- `unit: str` - Unit of measurement
- `checked: bool` - Whether the item is checked off (default=False)

**Validation:**
- **`normalize_key` validator**: 
  - Normalizes key and unit fields (trim, lowercase, strip punctuation)

**Class Methods:**
- **`get_state(key: str, connection: Optional[sqlite3.Connection] = None) -> Optional[ShoppingState]`**: 
  - Fetches saved state by normalized key
  - Includes debug logging for state retrieval
  - Supports transaction management

- **`update_state(key: str, quantity: float, unit: str, checked: bool, connection: Optional[sqlite3.Connection] = None) -> ShoppingState`**: 
  - Adds or updates the checkbox state for a shopping item
  - Updates existing state or creates new state as needed
  - Handles transaction management automatically
  - Includes comprehensive debug logging

**Usage Example:**
```python
# Save state for an item
state = ShoppingState.update_state(
    key="flour::cups",
    quantity=2.0,
    unit="cups",
    checked=True
)

# Retrieve state later
saved_state = ShoppingState.get_state("flour::cups")
if saved_state:
    is_checked = saved_state.checked
```

---

### 📄 saved_meal_state.py

**Path:** database/models/saved_meal_state.py

#### 📝 Purpose
Defines the `SavedMealState` model for persisting the current state of the meal planner, tracking which meals are currently active.

#### ⚙️ Core Class: `SavedMealState`

**Attributes:**
- `meal_id: int` - Foreign key to meal_selections table

**Class Methods:**
- **`all() -> list[SavedMealState]`**: 
  - Fetches all saved meal states from the database
  - Includes debug logging for the number of states loaded
  - Overrides base `all()` method to add logging

- **`clear_all() -> None`**: 
  - Deletes all entries from the saved meal state table
  - Iterates through all entries and deletes them individually

**Usage Example:**
```python
# Save current meal state
state = SavedMealState(meal_id=5)
state.save()

# Load all saved states
saved_states = SavedMealState.all()

# Clear all saved states
SavedMealState.clear_all()
```

---

### 📄 schema_version.py

**Path:** database/models/schema_version.py

#### 📝 Purpose
Tracks which SQL migrations have been applied to the database, enabling proper migration management and version control.

#### ⚙️ Core Class: `SchemaVersion`

**Attributes:**
- `id: Optional[int]` - Primary key
- `version: str` - Identifier of the applied migration (e.g., '001_initial') (validated, min_length=1)
- `applied_on: datetime` - When this migration was applied (auto-generated)

**Usage Example:**
```python
# Record a migration
version = SchemaVersion(
    version="003_recipe_history.sql"
)
version.save()

# Check applied migrations
applied = SchemaVersion.all()
```

---

### 📄 meal_log.py

**Path:** database/models/meal_log.py

#### 📝 Purpose
Logs each time a MealSelection was made or checked off, providing meal history and analytics capabilities.

#### ⚙️ Core Class: `MealLog`

**Attributes:**
- `id: Optional[int]` - Primary key
- `meal_selection_id: int` - Foreign key to meal_selections table (validated, ge=1)
- `checked_at: datetime` - When this meal was logged (auto-generated)

**Instance Methods:**
- **`get_meal() -> MealSelection`**: Returns the associated MealSelection object

**Usage Example:**
```python
# Log a meal selection
log = MealLog(meal_selection_id=10)
log.save()

# Get the associated meal
meal = log.get_meal()
```

---

### 📄 recipe_history.py

**Path:** database/models/recipe_history.py

#### 📝 Purpose
Tracks when recipes were cooked, enabling recipe suggestion algorithms and usage analytics.

#### ⚙️ Core Class: `RecipeHistory`

**Attributes:**
- `id: Optional[int]` - Primary key
- `recipe_id: int` - Foreign key to recipes table (validated, ge=1)
- `cooked_at: datetime` - When this recipe was cooked (auto-generated)

**Instance Methods:**
- **`get_recipe() -> Recipe`**: Returns the associated Recipe object

**Usage Example:**
```python
# Record cooking a recipe
history = RecipeHistory(recipe_id=15)
history.save()

# Get the associated recipe
recipe = history.get_recipe()
```

---

### 📄 weekly_menu.py

**Path:** database/models/weekly_menu.py

#### 📝 Purpose
Manages weekly meal planning and menu organization, tracking which recipes are planned for specific time periods.

#### ⚙️ Core Class: `WeeklyMenu`

**Attributes:**
- `id: Optional[int]` - Primary key
- `recipe_id: int` - Foreign key to recipes table (validated, ge=1)
- `added_at: datetime` - When this recipe was added to the weekly menu (auto-generated)

**Instance Methods:**
- **`get_recipe() -> Recipe`**: Returns the Recipe added to the weekly menu

**Usage Example:**
```python
# Add recipe to weekly menu
menu_item = WeeklyMenu(recipe_id=20)
menu_item.save()

# Get the planned recipe
recipe = menu_item.get_recipe()
```

---

## 🔧 Data Access Patterns

### Transaction Management
All models support transaction management through the connection context manager:

```python
with get_connection() as conn:
    # All operations within this block are transactional
    recipe = Recipe(name="Test Recipe")
    recipe.save()
    # Automatically commits on success, rolls back on exception
```

### Query Optimization
- Models use parameterized queries to prevent SQL injection
- Indexes are strategically placed on frequently queried columns
- Foreign key constraints ensure data integrity

### Error Handling
- Models raise appropriate exceptions for constraint violations
- Database connection errors are handled gracefully
- Logging is integrated for debugging database operations

---

## 🧠 Design Notes

### Model Architecture
- All models follow a consistent pattern with `save()`, class method queries, and `to_dict()` methods
- Optional connection parameters allow for transaction management
- Models are designed to be lightweight with minimal dependencies

### Relationship Management
- Foreign key relationships are properly defined with appropriate CASCADE and SET NULL behaviors
- Many-to-many relationships are handled through junction tables (e.g., `recipe_ingredients`)
- State persistence is separated from core data models for better organization

### Performance Considerations
- Indexes are created on commonly queried columns
- Bulk operations are supported through `execute_many()`
- Connection pooling is handled through the connection manager

### Future Extensibility
- Schema versioning support for migrations
- Model base classes could be extracted for common functionality
- Additional indexes can be added as query patterns evolve