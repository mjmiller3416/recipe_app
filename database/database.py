"""
Package: database

This module defines the `ApplicationDatabase` class, a singleton that manages
high-level interactions with the SQLite database for the Meal Planner application.

It provides:
- Centralized access to the database.
- CRUD operations for recipes, ingredients, and weekly menus.
- Integration with `DatabaseHelper` for low-level SQL operations.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
import os
import sqlite3
from typing import List

from core.helpers.debug_logger import DebugLogger
from core.modules.recipe_module import Recipe


from database.db_helpers import DatabaseHelper

# ── Class Definition ────────────────────────────────────────────────────────────
class ApplicationDatabase:
    """
    Singleton class that manages all database interactions.

    Provides high-level CRUD operations for recipes, ingredients, and weekly menus.
    Uses `DatabaseHelper` for low-level SQL execution.
    """

    _instance = None  #🔹Stores the singleton instance

    def __new__(cls, db_path=None):
        """Creates a single instance of the database class."""
        if cls._instance is None:
            if not db_path:
                raise RuntimeError("Database path must be provided for initialization.")
            cls._instance = super(ApplicationDatabase, cls).__new__(cls)
            cls._instance.init_db(db_path)
        return cls._instance

    def init_db(self, db_path):
        """
        Initializes the database. If the database file does not exist,
        it attempts to create and initialize it.

        Args:
            db_path (str): Path to the SQLite database file.
        """
        DebugLogger.log("Initializing the database...", "debug")

        if not db_path:
            raise ValueError("Database path cannot be None or empty.")

        if not os.path.exists(db_path):
            DebugLogger.log("Database file not found. Initializing new database...", "warning")
            from .initialize_db import initialize_database
            initialize_database(db_path, "database/db_tables.sql")

        self.db_path = db_path  # Store path for future connections
        DebugLogger.log(f"Database successfully initialized at: {db_path}\n", "info")

    @classmethod
    def connect(cls):
        """
        Provides a new database connection.

        Returns:
            sqlite3.Connection: An active database connection.

        Raises:
            RuntimeError: If the database has not been initialized.
        """
        if cls._instance is None:
            raise RuntimeError("Database has not been initialized. Call ApplicationDatabase(db_path) first.")
        return sqlite3.connect(cls._instance.db_path)

    def close_connection(self):
        """
        Closes the active database connection, if any.

        Logs any exceptions that occur during closure.
        """
        try:
            if hasattr(self, "db_path"):
                conn = sqlite3.connect(self.db_path)
                conn.close()
                DebugLogger.log("Database connection closed.", "info")
        except Exception as e:
            DebugLogger.log(f"Error closing database connection: {e}", "error")

    # CRUD Operations

    #🔹CREATE
    def save_recipe(self, recipe_data): # ✅
        """
        Adds a new recipe to the database.

        Args:
            recipe_data (dict): The recipe data to be stored.

        Returns:
            int: The ID of the newly added recipe.
        """
        DebugLogger().log("🔵 Adding new recipe...", "info")
        with self.connect() as conn:
            cursor = conn.cursor()
            recipe_id = DatabaseHelper.insert_recipe(cursor, recipe_data)
            conn.commit()
        DebugLogger().log("🟢 Recipe added with ID: {recipe_id}\n", "debug")
        return recipe_id

    def save_ingredients(self, recipe_id, ingredient_data):
        """
        Saves all ingredients to the database and links them to the given recipe_id.

        Args:
            recipe_id (int): The ID of the recipe these ingredients belong to.
            ingredient_data (list): A list of ingredient dicts to save.
        """
        DebugLogger().log("🔵 Saving all ingredients to the database...", "info")

        with self.connect() as conn:
            cursor = conn.cursor()
            for ing in ingredient_data:
                # Insert into `ingredients` table
                ingredient_id = DatabaseHelper.insert_ingredient(cursor, ing)
                DebugLogger().log("🟢 Ingredient with ID '{ingredient_id}' linked to recipe ID '{recipe_id}'\n", "debug")
                # Insert linking record
                DatabaseHelper.insert_recipe_ingredient(
                    cursor,
                    recipe_id,
                    ingredient_id,
                    ing["quantity"],
                    ing["unit"]
                )

            conn.commit()

        DebugLogger().log("🔵 All ingredients successfully inserted and linked. 🔵\n", "info")

    def save_meal(self, meal_name, main_recipe_id, side_recipes): # ✅
        """
        Saves a meal to the database.

        Args:
            meal_name (str): The name of the meal.
            main_recipe_id (int): The ID of the main recipe.
            side_recipes (list): List of up to 3 side recipe IDs.

        Returns:
            int: The ID of the newly added meal.
        """
        DebugLogger().log(f"🔵 Saving meal '{meal_name}' with main recipe {main_recipe_id}", "info")

        with self.connect() as conn:
            cursor = conn.cursor()

            # Ensure side_recipes always has 3 values (fill with None if missing)
            side_recipes = (side_recipes + [None] * 3)[:3]

            meal_id = DatabaseHelper.insert_meal(cursor, meal_name, main_recipe_id, side_recipes)

            conn.commit()

        DebugLogger().log(f"🟢 Meal saved with ID: {meal_id}", "info")
        return meal_id

    #🔹READ
    def recipe_exists(self, recipe_name, recipe_category):
        """
        Check if a recipe with the given name and category already exists.

        Args:
            recipe_name (str): The name of the recipe.
            recipe_category (str): The category of the recipe.

        Returns:
            bool: True if the recipe exists, False otherwise.
        """
        DebugLogger().log(
            "Checking if recipe '{recipe_name}' exists in category '{recipe_category}'...",
            "debug"
        )
        query = "SELECT 1 FROM recipes WHERE recipe_name = ? AND recipe_category = ?"
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (recipe_name, recipe_category))
            return cursor.fetchone() is not None

    def get_all_recipes(self) -> List[Recipe]: # <-- Return List[Recipe]
        """
        Retrieves all recipes from the database as fully populated Recipe objects,
        including associated ingredients handled via the Recipe class constructor.

        Returns:
            List[Recipe]: A list of Recipe objects with ingredients populated.
        """
        DebugLogger().log("🟢 Fetching all recipes and their ingredients...", "debug")

        recipe_objects: List[Recipe] = []

        with self.connect() as conn:
            cursor = conn.cursor()

            # 1. Fetch core recipe details as dictionaries
            core_recipe_data_list = DatabaseHelper.get_all_recipes(cursor) # Returns List[Dict]
            if not core_recipe_data_list:
                DebugLogger().log("🔴 No recipes found in the database.\n", "warning")
                return []

            # 2. For each recipe dictionary, fetch its ingredient dictionaries
            for recipe_dict in core_recipe_data_list:
                recipe_id = recipe_dict.get("id")
                if recipe_id is None:
                    DebugLogger().log(f"⚠️ Skipping recipe dict with no ID: {recipe_dict}", "warning")
                    continue

                # Fetch ingredient data (List[Dict]) for this recipe
                # This now returns dicts with 'ingredient_id' key correctly
                ingredient_data_list = DatabaseHelper.get_recipe_ingredients(cursor, recipe_id)

                # 3. Add the ingredient list to the recipe dictionary
                recipe_dict["ingredients"] = ingredient_data_list

                # 4. Now, create the Recipe object using the combined dictionary
                try:
                    # Recipe.__init__ handles mapping dict keys ('recipe_name', etc.)
                    # and creating RecipeIngredient objects from the 'ingredients' list.
                    recipe_obj = Recipe(recipe_dict)
                    recipe_objects.append(recipe_obj)
                except Exception as e:
                    # Log error if Recipe instantiation fails
                    DebugLogger().log(f"🔴 Error creating Recipe object for ID {recipe_id}: {e}\nData: {recipe_dict}", "error")

        return recipe_objects # Return the list of fully populated Recipe objects

    def get_recipe(self, recipe_id): # ✅
        """
        Retrieves a complete recipe including its ingredients.

        Args:
            recipe_id (int): The ID of the recipe to retrieve.

        Returns:
            dict: A dictionary containing recipe details along with a list of its ingredients.
        """
        DebugLogger().log("🟢 Fetching full recipe with ingredients for ID: '{recipe_id}'...", "debug")

        with self.connect() as conn:
            cursor = conn.cursor()

            # Fetch the main recipe details
            recipe = DatabaseHelper.get_recipe(cursor, recipe_id)
            if not recipe:
                DebugLogger().log("🔴 Recipe ID '{recipe_id}' not found.\n", "warning")
                return None

            # Fetch associated ingredients
            recipe["ingredients"] = DatabaseHelper.get_recipe_ingredients(cursor, recipe_id)

        return recipe

    def get_all_ingredients(app_db): # ⚠️
        """
        Retrieves ingredients from the database and sorts by name.
        Called when the application starts to load all ingredients into memory.
        Imported into the Ingredients page to display all ingredients.
        Called when adding a new recipe to populate the ingredient combobox.

        Args:
            app_db (ApplicationDatabase): The database connection instance.

        Returns:
            dict: A dictionary of ingredients with their quantities, units, and categories.
        """
        DebugLogger().log("Fetching all ingredients from the database...", "debug")

        ingredients = {}
        all_recipes = app_db.get_all_recipes()

        # ✅ Open one connection for efficiency
        with app_db.connect() as conn:
            cursor = conn.cursor()

            for recipe in all_recipes:
                recipe_id = recipe[0]
                ingredient_data = cursor.execute(
                    "SELECT name, ingredient_category, quantity, unit FROM ingredients WHERE recipe_id = ?",
                    (recipe_id,)
                ).fetchall()

                for name, category, quantity, unit in ingredient_data:
                    if name in ingredients:
                        ingredients[name]["quantity"] += quantity
                    else:
                        ingredients[name] = {
                            "quantity": quantity,
                            "unit": unit,
                            "ingredient_category": category
                        }

        return ingredients

    def get_ingredient(self, ingredient_id): # ❌
        """
        Retrieve an ingredient by ID from the database.
        """
        # Fetch the ingredient by ID
        # Return the ingredient
        pass

    def get_meal(self, meal_id):
        DebugLogger().log(f"🟢 Fetching meal with ID: {meal_id}", "info")
        with self.connect() as conn:
            cursor = conn.cursor()
            meal = DatabaseHelper.get_meal(cursor, meal_id)
            if meal:
                # Combine individual side recipe columns into a list
                side_recipe_ids = [
                    meal.get("side_recipe_1"),
                    meal.get("side_recipe_2"),
                    meal.get("side_recipe_3")
                ]
                meal["side_recipes"] = [
                    DatabaseHelper.get_recipe(cursor, rid) for rid in side_recipe_ids if rid
                ]
                # Fetch the main recipe details
                meal["main_recipe"] = DatabaseHelper.get_recipe(cursor, meal["main_recipe_id"])
        return meal

    def get_all_meals(self):
        """
        Retrieves all saved meals from the database.

        Returns:
            list: A list of dictionaries, each representing a saved meal.
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            return DatabaseHelper.get_all_meals(cursor)

    #🔹UPDATE
    def update_recipe(self, recipe_id, recipe_data): # ❌
        """
        Update an existing recipe in the database.

        Args:
            recipe_id (int): The ID of the recipe to update.
            recipe_data (dict): The updated data for the recipe.
        """
        # Update the recipe
        # Return True if successful, False otherwise
        pass

    def update_ingredient(self, ingredient_id, ingredient_data): # ❌
        """
        Update an existing ingredient in the database.

        Args:
            ingredient_id (int): The ID of the ingredient to update.
            ingredient_data (dict): The updated data for the ingredient.
        """
        # Update the ingredient
        # Return True if successful, False otherwise
        pass

    def update_meal(self, meal_id, meal_data): # ✅
        """
        Updates an existing meal record in the database.

        Args:
            meal_id (int): The ID of the meal to update.
            meal_data (dict): A dictionary containing updated recipe IDs.
                            Expected keys:
                                "main"  - ID of the main recipe (required)
                                "side1" - ID of side recipe 1 (or None)
                                "side2" - ID of side recipe 2 (or None)
                                "side3" - ID of side recipe 3 (or None)

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                # Extract values from meal_data, using None if a side is not provided
                main_recipe_id = meal_data.get("main")
                side1 = meal_data.get("side1")
                side2 = meal_data.get("side2")
                side3 = meal_data.get("side3")

                cursor.execute(
                    """
                    UPDATE meal_selection
                    SET main_recipe_id = ?,
                        side_recipe_1 = ?,
                        side_recipe_2 = ?,
                        side_recipe_3 = ?
                    WHERE id = ?
                    """,
                    (main_recipe_id, side1, side2, side3, meal_id)
                )
                conn.commit()
            DebugLogger().log(f"🟢 Meal with ID: {meal_id} successfully updated.", "info")
            return True
        except Exception as e:
            DebugLogger().log(f"Error updating meal with ID: {meal_id} - {e}", "error")
            return False

    #🔹DELETE
    def delete_recipe(self, recipe_id): # ❌
        """
        Delete a recipe from the database.
        Calls remove_recipe from db_helpers.py.

        Args:
            recipe_id (int): The ID of the recipe to delete.
        """
        # Delete the recipe
        # Prompt for confirmation - additional prompt for deleting ingredients
        # Return False if canceled, True if successful
        pass

    def delete_ingredient(self, ingredient_id): # ❌
        """
        Delete an ingredient from the database.
        Calls remove_ingredient from db_helpers.py.

        Args:
            ingredient_id (int): The ID of the ingredient to delete.
        """
        # Delete the ingredient
        # Prompt for confirmation
        # Return False if canceled, True if successful

        pass

    def delete_meal(self, meal_id): # ✅
        """
        Deletes a meal record from the database.

        Args:
            meal_id (int): The ID of the meal to delete.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM meal_selection WHERE id = ?", (meal_id,))
                conn.commit()
            DebugLogger().log(f"🟢 Meal with ID: {meal_id} successfully deleted.", "info")
            return True
        except Exception as e:
            DebugLogger().log(f"Error deleting meal with ID: {meal_id} - {e}", "error")
            return False


# 🔹 Create a Global Database Instance
DB_INSTANCE = ApplicationDatabase("database/app_data.db")

#🔸END
