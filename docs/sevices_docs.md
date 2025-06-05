# 📦 Services Package Overview

This section documents the structure and functionality of the services package for the MealGenie application. This package provides a higher-level API for interacting with the application's data, encapsulating business logic and data manipulation tasks with comprehensive transaction support and error handling.

---

## 📂 File Structure

```
└── 📁services
    ├── __init__.py
    ├── ingredient_service.py
    ├── meal_service.py
    ├── planner_service.py
    ├── recipe_service.py
    ├── shopping_service.py
    └── 📁dtos
        ├── __init__.py
        ├── ingredient_dtos.py
        └── recipe_dtos.py
```

---

## 📄 Core Service Files

### 📄 ingredient_service.py

**Path:** services/ingredient_service.py

#### 📝 Purpose
Service class for managing `Ingredient` entities with transactional support. Provides methods for searching, creating, and validating ingredients, often used in conjunction with recipe creation workflows.

#### ⚙️ Core Class: `IngredientService`

Static service class that provides ingredient-related operations with optional database connection management for transaction consistency.

##### 📋 Methods

**`list_all_ingredient_names(connection: Optional[sqlite3.Connection] = None) -> list[str]`**
- **Purpose**: Retrieves all distinct ingredient names from the database
- **Parameters**:
  - `connection`: Optional database connection for transaction management
- **Returns**: List of unique ingredient name strings
- **Usage**: Populating autocomplete dropdowns, ingredient validation
- **Example**:
  ```python
  # Get all ingredient names for autocomplete
  ingredient_names = IngredientService.list_all_ingredient_names()
  # Returns: ["chicken breast", "onion", "garlic", ...]
  ```

**`find_matching_ingredients(query: str, connection: Optional[sqlite3.Connection] = None) -> list[Ingredient]`**
- **Purpose**: Searches for ingredients using case-insensitive partial matching
- **Parameters**:
  - `query`: Search term to match against ingredient names
  - `connection`: Optional database connection for transaction management
- **Returns**: List of `Ingredient` model instances matching the query
- **Usage**: Search functionality, ingredient discovery
- **Example**:
  ```python
  # Search for ingredients containing "chick"
  matches = IngredientService.find_matching_ingredients("chick")
  # Returns: [Ingredient(name="chicken breast"), Ingredient(name="chicken thigh"), ...]
  ```

**`get_or_create_ingredient(name: str, category: str, connection: Optional[sqlite3.Connection] = None) -> Ingredient`**
- **Purpose**: Atomically finds existing ingredient or creates new one if not found
- **Parameters**:
  - `name`: Ingredient name
  - `category`: Ingredient category
  - `connection`: Optional database connection for transaction management
- **Returns**: Existing or newly created `Ingredient` instance
- **Usage**: Recipe creation, ensuring ingredient consistency
- **Transaction Behavior**: Creates connection context if none provided to ensure atomicity
- **Example**:
  ```python
  # Get or create ingredient within transaction
  with get_connection() as conn:
      ingredient = IngredientService.get_or_create_ingredient(
          "chicken breast", "Protein", connection=conn
      )
  ```
---

### 📄 recipe_service.py

**Path:** services/recipe_service.py

#### 📝 Purpose
Service class for comprehensive recipe management with transactional integrity. Handles complex recipe creation workflows including ingredient linking, duplicate prevention, and recipe filtering with advanced search capabilities.

#### 🚨 Custom Exceptions

**`RecipeSaveError(Exception)`**
- **Purpose**: Raised when recipe save operations fail due to database errors
- **Usage**: Provides context-aware error handling for recipe persistence failures

**`DuplicateRecipeError(Exception)`**
- **Purpose**: Raised when attempting to create a recipe that already exists
- **Usage**: Prevents duplicate recipe creation based on name and category

#### ⚙️ Core Class: `RecipeService`

Static service class providing transactional recipe operations with comprehensive error handling and data validation.

##### 📋 Methods

**`create_recipe_with_ingredients(recipe_dto: RecipeCreateDTO) -> Recipe`**
- **Purpose**: Atomically creates recipe with all associated ingredients in single transaction
- **Parameters**:
  - `recipe_dto`: `RecipeCreateDTO` containing recipe data and ingredient list
- **Returns**: Created `Recipe` instance with assigned ID
- **Raises**: 
  - `DuplicateRecipeError`: If recipe with same name/category exists
  - `RecipeSaveError`: If database operation fails
- **Transaction Behavior**: All operations wrapped in single database transaction
- **Example**:
  ```python
  from services.dtos.recipe_dtos import RecipeCreateDTO, RecipeIngredientInputDTO
  
  # Create recipe DTO with ingredients
  ingredients = [
      RecipeIngredientInputDTO(
          ingredient_name="chicken breast",
          ingredient_category="Protein",
          quantity=1.5,
          unit="lb"
      ),
      RecipeIngredientInputDTO(
          ingredient_name="olive oil",
          ingredient_category="Oil",
          quantity=2,
          unit="tbsp"
      )
  ]
  
  recipe_dto = RecipeCreateDTO(
      recipe_name="Grilled Chicken",
      recipe_category="Main Course",
      meal_type="Dinner",
      instructions="Grill chicken until cooked through",
      prep_time=15,
      cook_time=25,
      servings=4,
      ingredients=ingredients
  )
  
  try:
      recipe = RecipeService.create_recipe_with_ingredients(recipe_dto)
      print(f"Created recipe: {recipe.recipe_name} with ID: {recipe.id}")
  except DuplicateRecipeError as e:
      print(f"Recipe already exists: {e}")
  except RecipeSaveError as e:
      print(f"Failed to save recipe: {e}")
  ```

**`toggle_favorite(recipe_id: int) -> Recipe`**
- **Purpose**: Toggles the favorite status of a recipe
- **Parameters**:
  - `recipe_id`: ID of recipe to toggle favorite status
- **Returns**: Updated `Recipe` instance
- **Raises**: `ValueError` if recipe with given ID doesn't exist
- **Example**:
  ```python
  # Toggle favorite status
  try:
      updated_recipe = RecipeService.toggle_favorite(123)
      print(f"Recipe favorite status: {updated_recipe.is_favorite}")
  except ValueError as e:
      print(f"Recipe not found: {e}")
  ```

**`list_filtered(recipe_category: str | None = None, meal_type: str | None = None, sort_by: str | None = None, favorites_only: bool = False) -> list[Recipe]`**
- **Purpose**: Advanced recipe filtering with multiple criteria and sorting options
- **Parameters**:
  - `recipe_category`: Filter by recipe category ("All" or None for no filter)
  - `meal_type`: Filter by meal type ("All" or None for no filter)
  - `sort_by`: Sort order ("A-Z", "Z-A", or None for default)
  - `favorites_only`: If True, return only favorite recipes
- **Returns**: List of filtered and sorted `Recipe` instances
- **Usage**: Recipe browsing, search functionality, favorites management
- **Example**:
  ```python
  # Get favorite dinner recipes sorted A-Z
  favorite_dinners = RecipeService.list_filtered(
      meal_type="Dinner",
      sort_by="A-Z",
      favorites_only=True
  )
  
  # Get all main course recipes
  main_courses = RecipeService.list_filtered(
      recipe_category="Main Course"
  )
  
  # Get all recipes sorted Z-A
  all_recipes_desc = RecipeService.list_filtered(sort_by="Z-A")
  ```

---

### 📄 meal_service.py

**Path:** services/meal_service.py

#### 📝 Purpose
Service class for CRUD operations on `MealSelection` entities. Handles meal creation, updates, and loading with comprehensive error handling and logging support for meal planning workflows.

#### ⚙️ Core Class: `MealService`

Static service class providing meal management operations with transaction support and integrated debug logging.

##### 📋 Methods

**`create_meal(meal: MealSelection, connection: Optional[sqlite3.Connection] = None) -> MealSelection`**
- **Purpose**: Creates and persists a new meal selection to the database
- **Parameters**:
  - `meal`: Unsaved `MealSelection` instance (id should be None)
  - `connection`: Optional database connection for transaction management
- **Returns**: Saved `MealSelection` instance with assigned ID
- **Raises**: `ValueError` if meal already has an ID
- **Transaction Behavior**: Creates connection context if none provided
- **Logging**: Success event logged with meal details
- **Example**:
  ```python
  # Create new meal
  new_meal = MealSelection(
      meal_name="Sunday Dinner",
      main_recipe_id=123,
      side_recipe_1=456,
      side_recipe_2=789
  )
  
  try:
      saved_meal = MealService.create_meal(new_meal)
      print(f"Created meal with ID: {saved_meal.id}")
  except ValueError as e:
      print(f"Cannot create meal: {e}")
  ```

**`update_meal(meal: MealSelection, connection: Optional[sqlite3.Connection] = None) -> None`**
- **Purpose**: Updates an existing meal selection in the database
- **Parameters**:
  - `meal`: `MealSelection` instance with valid ID
  - `connection`: Optional database connection for transaction management
- **Returns**: None
- **Raises**: `ValueError` if meal doesn't have an ID
- **Transaction Behavior**: Creates connection context if none provided
- **Logging**: Update event logged with meal details
- **Fields Updated**: `meal_name`, `main_recipe_id`, `side_recipe_1`, `side_recipe_2`, `side_recipe_3`
- **Example**:
  ```python
  # Update existing meal
  existing_meal = MealService.load_meal(123)
  if existing_meal:
      existing_meal.meal_name = "Updated Sunday Dinner"
      existing_meal.side_recipe_3 = 999
      
      try:
          MealService.update_meal(existing_meal)
          print("Meal updated successfully")
      except ValueError as e:
          print(f"Cannot update meal: {e}")
  ```

**`load_meal(meal_id: int) -> Optional[MealSelection]`**
- **Purpose**: Loads a meal selection from the database by ID
- **Parameters**:
  - `meal_id`: ID of the meal to load
- **Returns**: `MealSelection` instance if found, None otherwise
- **Logging**: Success/warning events logged based on result
- **Example**:
  ```python
  # Load meal by ID
  meal = MealService.load_meal(123)
  if meal:
      print(f"Loaded meal: {meal.meal_name}")
      print(f"Main recipe ID: {meal.main_recipe_id}")
      print(f"Side recipes: {meal.get_side_recipe_ids()}")
  else:
      print("Meal not found")
  ```

---

### 📄 planner_service.py

**Path:** services/planner_service.py

#### 📝 Purpose
Service class for managing Meal Planner application state. Handles persistence of active meal IDs, state validation, and planner session management with comprehensive transaction support.

#### ⚙️ Core Class: `PlannerService`

Static service class managing `SavedMealState` data for meal planner session persistence and state management.

##### 📋 Methods

**`load_saved_meal_ids(connection: Optional[sqlite3.Connection] = None) -> List[int]`**
- **Purpose**: Retrieves all saved meal IDs from previous planner session
- **Parameters**:
  - `connection`: Optional database connection for transaction management
- **Returns**: List of meal IDs that were active in the last session
- **Logging**: Loaded IDs logged for debugging
- **Usage**: Application startup, session restoration
- **Example**:
  ```python
  # Load saved meal planner state on app startup
  saved_meal_ids = PlannerService.load_saved_meal_ids()
  print(f"Restoring {len(saved_meal_ids)} meals from last session")
  # Returns: [123, 456, 789] - meal IDs from last session
  ```

**`save_active_meal_ids(meal_ids: List[int], connection: Optional[sqlite3.Connection] = None) -> None`**
- **Purpose**: Atomically saves current active meal IDs as planner state
- **Parameters**:
  - `meal_ids`: List of currently active meal IDs
  - `connection`: Optional database connection for transaction management
- **Returns**: None
- **Transaction Behavior**: Atomically clears existing state and inserts new meal IDs
- **Logging**: Saved IDs logged for debugging
- **Usage**: Application shutdown, state persistence
- **Example**:
  ```python
  # Save current planner state before closing
  active_meals = [123, 456, 789]
  PlannerService.save_active_meal_ids(active_meals)
  print("Planner state saved successfully")
  
  # Within transaction context
  with get_connection() as conn:
      PlannerService.save_active_meal_ids(active_meals, connection=conn)
  ```

**`clear_planner_state(connection: Optional[sqlite3.Connection] = None) -> None`**
- **Purpose**: Clears all saved meal planner state from database
- **Parameters**:
  - `connection`: Optional database connection for transaction management
- **Returns**: None
- **Transaction Behavior**: Creates connection context if none provided
- **Logging**: Clear event logged
- **Usage**: Reset functionality, clearing saved sessions
- **Example**:
  ```python
  # Clear all saved planner state
  PlannerService.clear_planner_state()
  print("Planner state cleared")
  
  # Verify state is cleared
  remaining_ids = PlannerService.load_saved_meal_ids()
  assert len(remaining_ids) == 0
  ```

**`validate_meal_ids(meal_ids: List[int]) -> List[int]`**
- **Purpose**: Validates meal IDs against database to ensure they exist
- **Parameters**:
  - `meal_ids`: List of meal IDs to validate
- **Returns**: List containing only valid meal IDs that exist in database
- **Usage**: Data integrity, cleanup of orphaned meal IDs
- **Example**:
  ```python
  # Validate meal IDs before using them
  potentially_invalid_ids = [123, 456, 999, 789]  # 999 might not exist
  valid_ids = PlannerService.validate_meal_ids(potentially_invalid_ids)
  print(f"Valid meal IDs: {valid_ids}")
  # Returns: [123, 456, 789] - only existing meals
  
  # Use in planner restoration
  saved_ids = PlannerService.load_saved_meal_ids()
  valid_saved_ids = PlannerService.validate_meal_ids(saved_ids)
  # Only restore tabs for meals that still exist
  ```

---

### 📄 shopping_service.py

**Path:** services/shopping_service.py

#### 📝 Purpose
Comprehensive service for shopping list management. Combines ingredients from multiple recipes, handles manual item management, performs intelligent unit conversions, and maintains persistent item states across sessions.

#### ⚙️ Core Class: `ShoppingService`

Static service class providing unified shopping list operations with advanced aggregation, unit conversion, and state persistence capabilities.

##### 🔧 Unit Conversion System

**`_CONVERSIONS: Dict[str, Dict[str, float]]`**
- **Purpose**: Predefined conversion rules for ingredient standardization
- **Structure**: `{ingredient_name: {unit: conversion_factor}}`
- **Example Configuration**:
  ```python
  _CONVERSIONS = {
      "butter": {"stick": 8.0, "tbsp": 1.0},
      # More conversions can be added
  }
  ```

**`_convert_qty(name: str, qty: float, unit: str) -> Tuple[float, str]`**
- **Purpose**: Converts ingredient quantities to standardized units
- **Parameters**:
  - `name`: Ingredient name (used to lookup conversion rules)
  - `qty`: Original quantity
  - `unit`: Original unit
- **Returns**: Tuple of (converted_quantity, standardized_unit)
- **Logic**: Attempts to convert to larger, more convenient units when possible
- **Example**:
  ```python
  # Convert butter sticks to tablespoons
  qty, unit = ShoppingService._convert_qty("butter", 2, "stick")
  # Returns: (16.0, "tbsp") - 2 sticks = 16 tablespoons
  ```

##### 📋 Core Methods

**`generate_shopping_list(recipe_ids: List[int], connection: Optional[sqlite3.Connection] = None) -> List[ShoppingItem]`**
- **Purpose**: Generates comprehensive shopping list from recipe IDs with state restoration
- **Parameters**:
  - `recipe_ids`: List of recipe IDs to include in shopping list
  - `connection`: Optional database connection for transaction management
- **Returns**: List of `ShoppingItem` objects with aggregated quantities and restored states
- **Process**:
  1. Aggregates ingredients from all recipes
  2. Applies unit conversions for standardization
  3. Restores "checked" states from `ShoppingState` table
  4. Appends manually added items from `ShoppingList` table
- **Example**:
  ```python
  # Generate shopping list for multiple recipes
  recipe_ids = [123, 456, 789]
  shopping_items = ShoppingService.generate_shopping_list(recipe_ids)
  
  for item in shopping_items:
      status = "✓" if item.have else "○"
      print(f"{status} {item.quantity} {item.unit} {item.ingredient_name}")
  
  # Output:
  # ○ 2.5 lb chicken breast
  # ✓ 1 cup onion (previously checked)
  # ○ 3 tbsp olive oil
  ```

**`_aggregate_recipe_ingredients(recipe_ids: List[int], connection: Optional[sqlite3.Connection] = None) -> List[ShoppingItem]`**
- **Purpose**: Aggregates and consolidates ingredients from multiple recipes
- **Parameters**:
  - `recipe_ids`: List of recipe IDs to aggregate
  - `connection`: Optional database connection for transaction management
- **Returns**: List of consolidated `ShoppingItem` objects
- **Aggregation Logic**:
  - Groups identical ingredients by ID
  - Sums quantities for duplicate ingredients
  - Applies unit conversions for consistency
  - Creates `ShoppingItem` objects marked as from "recipe" source
- **Example**:
  ```python
  # Internal aggregation for recipes needing chicken breast
  # Recipe 1: 1.5 lb chicken breast
  # Recipe 2: 1 lb chicken breast
  # Result: 2.5 lb chicken breast (aggregated)
  ```

**`get_recipe_ids_from_meals(meal_ids: List[int]) -> List[int]`**
- **Purpose**: Extracts all recipe IDs from a list of meal selections
- **Parameters**:
  - `meal_ids`: List of meal selection IDs
- **Returns**: Flattened list of all recipe IDs from the meals
- **Process**:
  - Loads each `MealSelection` using `MealService`
  - Collects main recipe ID and all side recipe IDs
  - Returns deduplicated list of recipe IDs
- **Example**:
  ```python
  # Extract recipes from meal selections
  meal_ids = [10, 20, 30]
  recipe_ids = ShoppingService.get_recipe_ids_from_meals(meal_ids)
  # Returns: [123, 456, 789, 101, 102] - all recipes from the meals
  
  # Use for shopping list generation
  shopping_list = ShoppingService.generate_shopping_list(recipe_ids)
  ```

**`get_ingredient_breakdown(recipe_ids: List[int], connection: Optional[sqlite3.Connection] = None) -> Dict[str, List[Tuple[str, float, str]]]`**
- **Purpose**: Provides detailed breakdown of ingredient usage across recipes
- **Parameters**:
  - `recipe_ids`: List of recipe IDs to analyze
  - `connection`: Optional database connection for transaction management
- **Returns**: Dictionary mapping ingredient keys to list of (recipe_name, quantity, unit) tuples
- **Usage**: Debugging, detailed ingredient analysis, recipe planning
- **Example**:
  ```python
  # Get detailed ingredient breakdown
  breakdown = ShoppingService.get_ingredient_breakdown([123, 456])
  
  # breakdown = {
  #     "chicken breast::lb": [
  #         ("Grilled Chicken", 1.5, "lb"),
  #         ("Chicken Stir Fry", 1.0, "lb")
  #     ],
  #     "olive oil::tbsp": [
  #         ("Grilled Chicken", 2, "tbsp"),
  #         ("Chicken Stir Fry", 1, "tbsp")
  #     ]
  # }
  ```

##### 🛒 Manual Item Management

**`add_manual_item(name: str, qty: float, unit: str, connection: Optional[sqlite3.Connection] = None) -> None`**
- **Purpose**: Adds user-specified items to shopping list
- **Parameters**:
  - `name`: Item name
  - `qty`: Quantity
  - `unit`: Unit of measurement
  - `connection`: Optional database connection for transaction management
- **Returns**: None
- **Behavior**: Creates `ShoppingList` record with `have=False` by default
- **Example**:
  ```python
  # Add manual shopping items
  ShoppingService.add_manual_item("paper towels", 1, "pack")
  ShoppingService.add_manual_item("milk", 1, "gallon")
  
  # Items will appear in next shopping list generation
  ```

**`clear_manual_items(connection: Optional[sqlite3.Connection] = None) -> None`**
- **Purpose**: Removes all manually added items from shopping list
- **Parameters**:
  - `connection`: Optional database connection for transaction management
- **Returns**: None
- **Behavior**: Bulk deletes all records from `ShoppingList` table
- **Example**:
  ```python
  # Clear all manual items
  ShoppingService.clear_manual_items()
  
  # Verify manual items are cleared
  shopping_list = ShoppingService.generate_shopping_list([])
  manual_items = [item for item in shopping_list if item.source == "manual"]
  assert len(manual_items) == 0
  ```

**`toggle_have_status(item_name: str) -> None`**
- **Purpose**: Toggles the "have" status of manually added items
- **Parameters**:
  - `item_name`: Name of the manual item to toggle
- **Returns**: None
- **Behavior**: Finds manual item by name and toggles its `have` boolean status
- **Note**: Operates only on `ShoppingList` (manual items), not `ShoppingState` (recipe items)
- **Example**:
  ```python
  # Toggle manual item status
  ShoppingService.add_manual_item("milk", 1, "gallon")
  ShoppingService.toggle_have_status("milk")  # Now marked as "have"
  ShoppingService.toggle_have_status("milk")  # Back to "don't have"
  ```

#### 🧠 Architecture Notes

**State Persistence Strategy**:
- **`ShoppingList` Table**: Stores manually added items with their own `have` status
- **`ShoppingState` Table**: Stores checked status for recipe-derived ingredients
- **Separation Benefits**: Recipe changes don't affect manual item states, and manual items don't interfere with recipe ingredient state tracking

**Unit Conversion Benefits**:
- **Consistency**: Standardizes measurements for better aggregation
- **User Experience**: Presents quantities in most convenient units
- **Extensibility**: Easy to add new conversion rules via `_CONVERSIONS` dictionary

**Transaction Support**:
- All methods support optional connection parameters for transaction consistency
- Follows application-wide pattern for database operation management
- Enables complex workflows with guaranteed atomicity

---

## 📄 Data Transfer Objects (DTOs)

The DTOs package provides Pydantic-based data validation and transformation objects that ensure type safety and data integrity across service boundaries.

### 📄 ingredient_dtos.py

**Path:** services/dtos/ingredient_dtos.py

#### 📝 Purpose
Defines data transfer objects for ingredient-related operations, providing structured search capabilities with built-in validation.

#### 🏗️ DTO Classes

**`IngredientSearchDTO`**
- **Purpose**: Validates and structures ingredient search parameters
- **Base Class**: `pydantic.BaseModel`
- **Fields**:
  - `search_term: str` - Required search term with minimum length validation
  - `category: Optional[str]` - Optional category filter
- **Validation**: Ensures search term is not empty
- **Usage Example**:
  ```python
  from services.dtos.ingredient_dtos import IngredientSearchDTO
  
  # Create search DTO with validation
  search_dto = IngredientSearchDTO(
      search_term="chicken",
      category="Meat"
  )
  
  # Use in service methods
  results = IngredientService.search_ingredients(search_dto)
  ```

### 📄 recipe_dtos.py

**Path:** services/dtos/recipe_dtos.py

#### 📝 Purpose
Comprehensive DTOs for recipe operations including creation, ingredient input, and filtering with advanced validation and data transformation capabilities.

#### 🏗️ DTO Classes

**`RecipeIngredientInputDTO`**
- **Purpose**: Validates individual ingredient inputs for recipe creation
- **Base Class**: `pydantic.BaseModel`
- **Fields**:
  - `ingredient_name: str` - Required ingredient name (auto-stripped)
  - `ingredient_category: str` - Required ingredient category (auto-stripped)
  - `quantity: Optional[float]` - Optional quantity amount
  - `unit: Optional[str]` - Optional measurement unit
- **Validators**:
  - `strip_strings`: Automatically removes leading/trailing whitespace from string fields
- **Usage Example**:
  ```python
  from services.dtos.recipe_dtos import RecipeIngredientInputDTO
  
  # Create ingredient input with validation
  ingredient = RecipeIngredientInputDTO(
      ingredient_name="  Chicken Breast  ",  # Will be auto-stripped
      ingredient_category="Meat",
      quantity=1.5,
      unit="lbs"
  )
  ```

**`RecipeCreateDTO`**
- **Purpose**: Validates complete recipe creation data with ingredient list
- **Base Class**: `pydantic.BaseModel`
- **Fields**:
  - `recipe_name: str` - Required recipe name with minimum length
  - `recipe_category: str` - Required recipe category with minimum length
  - `meal_type: str` - Meal type (defaults to "Dinner")
  - `instructions: Optional[str]` - Optional cooking instructions
  - `prep_time: Optional[int]` - Optional preparation time in minutes
  - `cook_time: Optional[int]` - Optional cooking time in minutes
  - `servings: Optional[int]` - Optional number of servings
  - `ingredients: List[RecipeIngredientInputDTO]` - List of recipe ingredients
- **Usage Example**:
  ```python
  from services.dtos.recipe_dtos import RecipeCreateDTO, RecipeIngredientInputDTO
  
  # Create complete recipe DTO
  recipe_dto = RecipeCreateDTO(
      recipe_name="Grilled Chicken",
      recipe_category="Main Course",
      meal_type="Dinner",
      instructions="Season and grill chicken until cooked through",
      prep_time=15,
      cook_time=20,
      servings=4,
      ingredients=[
          RecipeIngredientInputDTO(
              ingredient_name="Chicken Breast",
              ingredient_category="Meat",
              quantity=2.0,
              unit="lbs"
          ),
          RecipeIngredientInputDTO(
              ingredient_name="Olive Oil",
              ingredient_category="Oils",
              quantity=2.0,
              unit="tbsp"
          )
      ]
  )
  
  # Use in service
  recipe_id = RecipeService.create_recipe(recipe_dto)
  ```

**`RecipeFilterDTO`**
- **Purpose**: Validates and structures recipe filtering and sorting parameters
- **Base Class**: `pydantic.BaseModel`
- **Fields**:
  - `category: Optional[str]` - Filter by recipe category
  - `meal_type: Optional[str]` - Filter by meal type
  - `sort_by: Optional[str]` - Sort criteria
  - `favorites_only: bool` - Show only favorited recipes (defaults to False)
- **Usage Example**:
  ```python
  from services.dtos.recipe_dtos import RecipeFilterDTO
  
  # Create filter DTO
  filter_dto = RecipeFilterDTO(
      category="Main Course",
      meal_type="Dinner",
      favorites_only=True,
      sort_by="name"
  )
  
  # Use in service
  filtered_recipes = RecipeService.get_filtered_recipes(filter_dto)
  ```

#### 🔒 DTO Benefits

**Type Safety**:
- Compile-time and runtime type checking via Pydantic
- Automatic validation of required fields and data types
- Clear error messages for invalid data

**Data Transformation**:
- Automatic string stripping for text fields
- Field validation and normalization
- Default value assignment for optional fields

**API Consistency**:
- Standardized data structures across service boundaries
- Clear contracts between UI and service layers
- Reduced coupling between components

**Documentation**:
- Self-documenting field definitions with constraints
- Type hints provide IDE autocomplete and validation
- Field descriptions and validation rules are explicit

---

## 🏗️ Service Architecture Patterns

The services package follows consistent architectural patterns that ensure reliability, maintainability, and transaction safety across the application.

### 🔄 Transaction Management Pattern

All service methods support optional database connection parameters to enable transaction management and ensure data consistency across complex operations.

#### Pattern Implementation
```python
def service_method(self, data: Any, connection: Optional[sqlite3.Connection] = None) -> Any:
    """Service method with transaction support."""
    if connection:
        # Use provided connection (part of larger transaction)
        return some_database_operation(data, connection)
    else:
        # Create new connection for standalone operation
        with get_database_connection() as conn:
            return some_database_operation(data, conn)
```

#### Benefits
- **Atomicity**: Multiple service calls can be wrapped in a single transaction
- **Consistency**: Either all operations succeed or all are rolled back
- **Flexibility**: Methods work both standalone and as part of larger workflows
- **Error Safety**: Automatic rollback on exceptions

#### Usage Examples
```python
# Standalone operation (auto-transaction)
recipe_id = RecipeService.create_recipe(recipe_dto)

# Multi-service transaction
with get_database_connection() as conn:
    try:
        recipe_id = RecipeService.create_recipe(recipe_dto, conn)
        MealService.add_meal(meal_dto, conn)
        PlannerService.add_to_plan(plan_dto, conn)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
```

### 🎯 Service Responsibility Pattern

Each service has a clearly defined scope of responsibility, promoting separation of concerns and maintainable code organization.

#### Service Boundaries

**`IngredientService`**:
- ✅ Ingredient CRUD operations
- ✅ Ingredient validation and search
- ✅ Ingredient name management
- ❌ Recipe-ingredient relationships (handled by RecipeService)

**`RecipeService`**:
- ✅ Recipe CRUD operations
- ✅ Recipe-ingredient relationship management
- ✅ Recipe filtering and search
- ❌ Meal planning logic (handled by PlannerService)

**`MealService`**:
- ✅ Meal selection CRUD operations
- ✅ Meal metadata management
- ❌ Complex meal planning workflows (handled by PlannerService)

**`PlannerService`**:
- ✅ Meal planning state management
- ✅ Plan persistence and retrieval
- ✅ Date-based meal organization
- ❌ Shopping list generation (handled by ShoppingService)

**`ShoppingService`**:
- ✅ Shopping list generation from meal plans
- ✅ Manual shopping item management
- ✅ Shopping state persistence
- ❌ Meal plan modification (handled by PlannerService)

### 🔍 Data Flow Pattern

Services follow a consistent data flow pattern that ensures data integrity and clear component boundaries.

#### Flow Architecture
```
UI Layer
    ↓ (DTOs)
Service Layer
    ↓ (Entity Objects)
Database Layer
    ↓ (Raw Data)
SQLite Database
```

#### Data Transformation Stages

1. **Input Validation**: DTOs validate and transform user input
2. **Business Logic**: Services apply business rules and coordinate operations
3. **Data Persistence**: Database classes handle raw data storage and retrieval
4. **Result Formatting**: Services transform database results for UI consumption

### 🚨 Error Handling Pattern

Services implement consistent error handling strategies that provide meaningful feedback and maintain system stability.

#### Error Categories

**Validation Errors**:
- Source: DTO validation failures
- Handling: Caught at service boundary, translated to user-friendly messages
- Example: Invalid recipe name length, missing required fields

**Business Logic Errors**:
- Source: Custom service exceptions (e.g., `RecipeNotFoundError`)
- Handling: Specific exception types with descriptive messages
- Example: Attempting to delete non-existent recipe

**Database Errors**:
- Source: SQLite constraint violations, connection issues
- Handling: Wrapped in service-specific exceptions with context
- Example: Foreign key constraint violations, duplicate entries

**System Errors**:
- Source: File system, network, or unexpected runtime errors
- Handling: Logged with full context, graceful degradation where possible
- Example: Database file corruption, disk space issues

#### Error Propagation Strategy
```python
try:
    # Service operation
    result = service_method(data)
except ValidationError as e:
    # DTO validation failed
    raise ServiceValidationError(f"Invalid input: {e}")
except DatabaseError as e:
    # Database operation failed
    raise ServiceDatabaseError(f"Data operation failed: {e}")
except Exception as e:
    # Unexpected error
    logger.error(f"Unexpected error in {service_method.__name__}: {e}")
    raise ServiceError("An unexpected error occurred")
```

### 🔧 Dependency Injection Pattern

Services use dependency injection for database connections and external dependencies, enabling testability and flexibility.

#### Pattern Benefits
- **Testability**: Easy to mock dependencies for unit testing
- **Configuration**: Different database connections for different environments
- **Flexibility**: Services don't directly instantiate dependencies
- **Transaction Control**: External transaction management capability

#### Implementation Example
```python
class RecipeService:
    @staticmethod
    def create_recipe(recipe_dto: RecipeCreateDTO, 
                     connection: Optional[sqlite3.Connection] = None) -> int:
        # Dependency injection: connection can be provided or created
        db_manager = RecipeDatabase(connection) if connection else RecipeDatabase()
        return db_manager.create_recipe(recipe_dto)
```

---

## 🔄 Comprehensive Usage Examples

This section demonstrates common workflows and integration patterns using the services package, showing how different services work together to accomplish complex tasks.

### 📝 Recipe Creation Workflow

Complete workflow for creating a new recipe with ingredients, including validation and error handling.

```python
from services.dtos.recipe_dtos import RecipeCreateDTO, RecipeIngredientInputDTO
from services.recipe_service import RecipeService
from services.ingredient_service import IngredientService

def create_complete_recipe():
    """Example: Create a recipe with ingredient validation."""
    
    # Step 1: Prepare ingredient data with validation
    ingredients = [
        RecipeIngredientInputDTO(
            ingredient_name="Chicken Breast",
            ingredient_category="Meat",
            quantity=2.0,
            unit="lbs"
        ),
        RecipeIngredientInputDTO(
            ingredient_name="Olive Oil",
            ingredient_category="Oils",
            quantity=2.0,
            unit="tbsp"
        ),
        RecipeIngredientInputDTO(
            ingredient_name="Garlic",
            ingredient_category="Vegetables",
            quantity=3.0,
            unit="cloves"
        )
    ]
    
    # Step 2: Create recipe DTO with all metadata
    recipe_dto = RecipeCreateDTO(
        recipe_name="Garlic Grilled Chicken",
        recipe_category="Main Course",
        meal_type="Dinner",
        instructions="""
        1. Marinate chicken in olive oil and minced garlic for 30 minutes
        2. Preheat grill to medium-high heat
        3. Grill chicken 6-7 minutes per side until internal temp reaches 165°F
        4. Let rest 5 minutes before serving
        """.strip(),
        prep_time=35,  # Including marination
        cook_time=15,
        servings=4,
        ingredients=ingredients
    )
    
    # Step 3: Create recipe with transaction safety
    try:
        recipe_id = RecipeService.create_recipe(recipe_dto)
        print(f"Recipe created successfully with ID: {recipe_id}")
        
        # Step 4: Verify creation by retrieving recipe
        created_recipe = RecipeService.get_recipe_by_id(recipe_id)
        print(f"Recipe '{created_recipe.recipe_name}' has {len(created_recipe.ingredients)} ingredients")
        
        return recipe_id
        
    except RecipeValidationError as e:
        print(f"Recipe validation failed: {e}")
        return None
    except RecipeCreationError as e:
        print(f"Recipe creation failed: {e}")
        return None
```

### 🗓️ Meal Planning Workflow

Complete workflow for creating a meal plan, including recipe selection and meal scheduling.

```python
from datetime import datetime, timedelta
from services.recipe_service import RecipeService
from services.meal_service import MealService
from services.planner_service import PlannerService
from services.dtos.recipe_dtos import RecipeFilterDTO

def create_weekly_meal_plan():
    """Example: Create a complete weekly meal plan."""
    
    # Step 1: Get available recipes for different meal types
    dinner_filter = RecipeFilterDTO(
        meal_type="Dinner",
        favorites_only=False,
        sort_by="name"
    )
    
    lunch_filter = RecipeFilterDTO(
        meal_type="Lunch",
        favorites_only=False,
        sort_by="name"
    )
    
    dinner_recipes = RecipeService.get_filtered_recipes(dinner_filter)
    lunch_recipes = RecipeService.get_filtered_recipes(lunch_filter)
    
    print(f"Available recipes: {len(dinner_recipes)} dinners, {len(lunch_recipes)} lunches")
    
    # Step 2: Plan meals for the week
    start_date = datetime.now().date()
    meal_plan = {}
    
    with get_database_connection() as conn:
        try:
            for day_offset in range(7):  # 7-day plan
                current_date = start_date + timedelta(days=day_offset)
                
                # Add lunch if available
                if lunch_recipes and day_offset < len(lunch_recipes):
                    lunch_recipe = lunch_recipes[day_offset % len(lunch_recipes)]
                    lunch_meal_id = MealService.add_meal(
                        recipe_id=lunch_recipe.recipe_id,
                        meal_type="Lunch",
                        connection=conn
                    )
                    
                    PlannerService.add_to_plan(
                        meal_id=lunch_meal_id,
                        date=current_date,
                        connection=conn
                    )
                    
                    meal_plan[f"{current_date}_lunch"] = lunch_recipe.recipe_name
                
                # Add dinner
                if dinner_recipes and day_offset < len(dinner_recipes):
                    dinner_recipe = dinner_recipes[day_offset % len(dinner_recipes)]
                    dinner_meal_id = MealService.add_meal(
                        recipe_id=dinner_recipe.recipe_id,
                        meal_type="Dinner",
                        connection=conn
                    )
                    
                    PlannerService.add_to_plan(
                        meal_id=dinner_meal_id,
                        date=current_date,
                        connection=conn
                    )
                    
                    meal_plan[f"{current_date}_dinner"] = dinner_recipe.recipe_name
            
            conn.commit()
            print("Weekly meal plan created successfully!")
            
            # Step 3: Display the plan
            for day_offset in range(7):
                current_date = start_date + timedelta(days=day_offset)
                day_name = current_date.strftime("%A")
                
                lunch = meal_plan.get(f"{current_date}_lunch", "No lunch planned")
                dinner = meal_plan.get(f"{current_date}_dinner", "No dinner planned")
                
                print(f"{day_name} ({current_date}):")
                print(f"  Lunch: {lunch}")
                print(f"  Dinner: {dinner}")
            
            return meal_plan
            
        except Exception as e:
            conn.rollback()
            print(f"Meal planning failed: {e}")
            return None
```

### 🛒 Shopping List Generation Workflow

Complete workflow for generating a shopping list from meal plans with quantity aggregation.

```python
from datetime import datetime, timedelta
from services.planner_service import PlannerService
from services.shopping_service import ShoppingService

def generate_weekly_shopping_list():
    """Example: Generate shopping list for current week's meal plan."""
    
    # Step 1: Get current week's date range
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    print(f"Generating shopping list for {start_of_week} to {end_of_week}")
    
    # Step 2: Get meal plan for the week
    meal_plan = PlannerService.get_plan_for_date_range(start_of_week, end_of_week)
    
    if not meal_plan:
        print("No meal plan found for this week")
        return None
    
    print(f"Found {len(meal_plan)} planned meals")
    
    # Step 3: Generate shopping list from meal plan
    try:
        shopping_list = ShoppingService.generate_shopping_list_from_plan(meal_plan)
        
        # Step 4: Add some manual items
        manual_items = [
            ("Milk", "Dairy", "1 gallon"),
            ("Bread", "Bakery", "1 loaf"),
            ("Coffee", "Beverages", "1 bag")
        ]
        
        for item_name, category, quantity in manual_items:
            ShoppingService.add_manual_item(
                item_name=item_name,
                category=category,
                quantity=quantity
            )
        
        # Step 5: Get complete shopping list
        complete_list = ShoppingService.get_complete_shopping_list()
        
        # Step 6: Display organized shopping list
        print("\n=== SHOPPING LIST ===")
        current_category = None
        
        for item in complete_list:
            if item.category != current_category:
                current_category = item.category
                print(f"\n{current_category.upper()}:")
                print("-" * 20)
            
            status = "✓" if item.have else "☐"
            source = "(planned)" if hasattr(item, 'recipe_ids') and item.recipe_ids else "(manual)"
            print(f"{status} {item.quantity} {item.item_name} {source}")
        
        return complete_list
        
    except Exception as e:
        print(f"Shopping list generation failed: {e}")
        return None

def manage_shopping_progress():
    """Example: Mark items as purchased and track progress."""
    
    shopping_list = ShoppingService.get_complete_shopping_list()
    
    if not shopping_list:
        print("No shopping list found")
        return
    
    print(f"Shopping list has {len(shopping_list)} items")
    
    # Simulate shopping progress
    purchased_items = ["Milk", "Chicken Breast", "Garlic"]
    
    for item_name in purchased_items:
        try:
            ShoppingService.mark_item_purchased(item_name)
            print(f"✓ Marked '{item_name}' as purchased")
        except Exception as e:
            print(f"Failed to mark '{item_name}' as purchased: {e}")
    
    # Check progress
    updated_list = ShoppingService.get_complete_shopping_list()
    purchased_count = sum(1 for item in updated_list if item.have)
    total_count = len(updated_list)
    progress = (purchased_count / total_count) * 100 if total_count > 0 else 0
    
    print(f"\nShopping progress: {purchased_count}/{total_count} items ({progress:.1f}%)")
```

### 🔍 Recipe Search and Management Workflow

Advanced recipe search, filtering, and management operations.

```python
from services.recipe_service import RecipeService
from services.ingredient_service import IngredientService
from services.dtos.recipe_dtos import RecipeFilterDTO
from services.dtos.ingredient_dtos import IngredientSearchDTO

def advanced_recipe_search():
    """Example: Advanced recipe search with multiple criteria."""
    
    # Step 1: Search for recipes by ingredient
    ingredient_search = IngredientSearchDTO(
        search_term="chicken",
        category="Meat"
    )
    
    recipes_with_chicken = RecipeService.search_recipes_by_ingredient(ingredient_search)
    print(f"Found {len(recipes_with_chicken)} recipes containing chicken")
    
    # Step 2: Filter favorite dinner recipes
    dinner_favorites = RecipeFilterDTO(
        meal_type="Dinner",
        favorites_only=True,
        sort_by="name"
    )
    
    favorite_dinners = RecipeService.get_filtered_recipes(dinner_favorites)
    print(f"Found {len(favorite_dinners)} favorite dinner recipes")
    
    # Step 3: Get recipe details with ingredients
    for recipe in favorite_dinners[:3]:  # Show first 3
        recipe_details = RecipeService.get_recipe_by_id(recipe.recipe_id)
        print(f"\n{recipe_details.recipe_name}:")
        print(f"  Category: {recipe_details.recipe_category}")
        print(f"  Prep Time: {recipe_details.prep_time} min")
        print(f"  Cook Time: {recipe_details.cook_time} min")
        print(f"  Servings: {recipe_details.servings}")
        print(f"  Ingredients: {len(recipe_details.ingredients)}")
        
        # Show first few ingredients
        for ingredient in recipe_details.ingredients[:3]:
            quantity_str = f"{ingredient.quantity} {ingredient.unit}" if ingredient.quantity else "As needed"
            print(f"    - {quantity_str} {ingredient.ingredient_name}")
    
    return favorite_dinners

def recipe_management_workflow():
    """Example: Complete recipe management operations."""
    
    # Step 1: Get all recipe categories
    all_recipes = RecipeService.get_all_recipes()
    categories = set(recipe.recipe_category for recipe in all_recipes)
    print(f"Recipe categories: {', '.join(sorted(categories))}")
    
    # Step 2: Manage favorites
    recipe_to_favorite = all_recipes[0] if all_recipes else None
    
    if recipe_to_favorite:
        print(f"Managing favorites for: {recipe_to_favorite.recipe_name}")
        
        # Toggle favorite status
        current_status = RecipeService.is_recipe_favorite(recipe_to_favorite.recipe_id)
        print(f"Current favorite status: {current_status}")
        
        if current_status:
            RecipeService.remove_from_favorites(recipe_to_favorite.recipe_id)
            print("Removed from favorites")
        else:
            RecipeService.add_to_favorites(recipe_to_favorite.recipe_id)
            print("Added to favorites")
    
    # Step 3: Recipe statistics
    total_recipes = len(all_recipes)
    favorite_count = len([r for r in all_recipes if RecipeService.is_recipe_favorite(r.recipe_id)])
    
    meal_type_counts = {}
    for recipe in all_recipes:
        meal_type = recipe.meal_type
        meal_type_counts[meal_type] = meal_type_counts.get(meal_type, 0) + 1
    
    print(f"\nRecipe Statistics:")
    print(f"  Total recipes: {total_recipes}")
    print(f"  Favorites: {favorite_count}")
    print(f"  By meal type:")
    for meal_type, count in sorted(meal_type_counts.items()):
        print(f"    {meal_type}: {count}")
```

### 🔗 Service Integration Example

Example showing how all services work together in a complete application workflow.

```python
def complete_application_workflow():
    """Example: Complete workflow using all services together."""
    
    print("=== COMPLETE MEAL PLANNING WORKFLOW ===")
    
    # Phase 1: Recipe Management
    print("\n1. Recipe Management")
    recipes = RecipeService.get_all_recipes()
    print(f"Available recipes: {len(recipes)}")
    
    # Phase 2: Meal Planning
    print("\n2. Meal Planning")
    start_date = datetime.now().date()
    meal_count = 0
    
    with get_database_connection() as conn:
        try:
            # Plan 3 days of meals
            for day_offset in range(3):
                current_date = start_date + timedelta(days=day_offset)
                
                if recipes and day_offset < len(recipes):
                    recipe = recipes[day_offset]
                    meal_id = MealService.add_meal(
                        recipe_id=recipe.recipe_id,
                        meal_type="Dinner",
                        connection=conn
                    )
                    
                    PlannerService.add_to_plan(
                        meal_id=meal_id,
                        date=current_date,
                        connection=conn
                    )
                    
                    meal_count += 1
                    print(f"  Planned: {recipe.recipe_name} for {current_date}")
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            print(f"Meal planning failed: {e}")
            return
    
    # Phase 3: Shopping List Generation
    print("\n3. Shopping List Generation")
    end_date = start_date + timedelta(days=2)
    meal_plan = PlannerService.get_plan_for_date_range(start_date, end_date)
    
    if meal_plan:
        shopping_list = ShoppingService.generate_shopping_list_from_plan(meal_plan)
        print(f"Generated shopping list with {len(shopping_list)} items")
        
        # Add manual items
        ShoppingService.add_manual_item("Milk", "Dairy", "1 gallon")
        ShoppingService.add_manual_item("Bread", "Bakery", "1 loaf")
        
        complete_list = ShoppingService.get_complete_shopping_list()
        print(f"Complete shopping list: {len(complete_list)} items")
        
        # Phase 4: Shopping Progress
        print("\n4. Shopping Progress Simulation")
        item_names = [item.item_name for item in complete_list[:3]]
        
        for item_name in item_names:
            ShoppingService.mark_item_purchased(item_name)
            print(f"  Purchased: {item_name}")
        
        # Final status
        updated_list = ShoppingService.get_complete_shopping_list()
        purchased = sum(1 for item in updated_list if item.have)
        total = len(updated_list)
        
        print(f"\nWorkflow completed successfully!")
        print(f"  Meals planned: {meal_count}")
        print(f"  Shopping items: {total}")
        print(f"  Items purchased: {purchased}")
        print(f"  Shopping progress: {(purchased/total)*100:.1f}%")
    
    else:
        print("No meal plan found for shopping list generation")

# Example usage:
if __name__ == "__main__":
    # Run individual workflows
    create_complete_recipe()
    create_weekly_meal_plan()
    generate_weekly_shopping_list()
    advanced_recipe_search()
    
    # Run complete integrated workflow
    complete_application_workflow()
```

---

## 📋 Summary

The services package provides a comprehensive, well-structured API layer for the MealGenie application with the following key characteristics:

### 🎯 Key Features

**Comprehensive Business Logic**:
- Complete CRUD operations for all major entities (recipes, meals, ingredients, plans, shopping lists)
- Advanced search and filtering capabilities with DTO-based validation
- Complex workflow orchestration (meal planning, shopping list generation)
- State management for shopping progress and meal plan persistence

**Robust Architecture**:
- Consistent transaction management patterns across all services
- Optional dependency injection for testability and flexibility
- Clear separation of concerns between service responsibilities
- Comprehensive error handling with meaningful feedback

**Type Safety & Validation**:
- Pydantic-based DTOs for input validation and data transformation
- Runtime type checking and automatic data normalization
- Clear contracts between UI and service layers
- Self-documenting API with type hints and validation rules

**Production-Ready Patterns**:
- Atomic transaction support for complex operations
- Graceful error handling and recovery
- Efficient database connection management
- Extensible design for future feature additions

### 🔧 Integration Benefits

**For Developers**:
- Clear, consistent API patterns across all services
- Type-safe interfaces with comprehensive documentation
- Easy testing through dependency injection
- Predictable error handling and transaction behavior

**For Applications**:
- Reliable data consistency through transaction management
- Flexible workflow composition through service orchestration
- Scalable architecture supporting complex business requirements
- Maintainable codebase with clear component boundaries

### 📈 Usage Patterns

The services package supports three primary usage patterns:

1. **Simple Operations**: Direct service method calls for basic CRUD operations
2. **Transactional Workflows**: Multi-service operations wrapped in database transactions
3. **Complex Integrations**: Full application workflows combining all services

Each pattern provides appropriate levels of abstraction and transaction safety for different application needs.

---

*This documentation provides complete coverage of the services package functionality. For database layer details, see the database documentation. For UI integration examples, refer to the application documentation.*