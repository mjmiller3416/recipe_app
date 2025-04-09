"""
Package: app/database

This module provides low-level database operations for managing recipes, ingredients, 
and weekly menus in the Meal Planner database.

It includes:
- SQL execution for insert, update, delete, and retrieval.
- Database integrity validation before performing operations.
"""

# 🔸 Local Imports
from debug_logger import DebugLogger

class DatabaseHelper:
    """Handles low-level database operations for recipes and ingredients."""

    #🔹INSERT DATA
    @staticmethod
    def insert_recipe(cursor, recipe_data): # ✅
        """
        Inserts a new recipe into the database.

        Args:
            cursor (sqlite3.Cursor): Active database cursor.
            recipe_data (dict): Dictionary containing recipe details.

        Returns:
            int: The ID of the newly inserted recipe.
        """
        DebugLogger().log("🔵 Inserting recipe into the database...", "info")
        DebugLogger().log(f"🟢 Recipe Name: {recipe_data["recipe_name"]}, Category: {recipe_data["recipe_category"]}, Total Time: {recipe_data["total_time"]}, Servings: {recipe_data["servings"]}\n", "debug")
        cursor.execute(
            """
            INSERT INTO recipes (recipe_name, recipe_category, total_time, servings, directions, image_path)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                recipe_data["recipe_name"],
                recipe_data["recipe_category"],
                recipe_data["total_time"],
                recipe_data["servings"],
                recipe_data["directions"],
                recipe_data["image_path"]
            )
        )
        return cursor.lastrowid

    def insert_ingredient(cursor, ingredient_data): # ✅
        """
        Inserts a new ingredient into the 'ingredients' table.
        - No quantity or unit, because we only store that in recipe_ingredients.
        
        Args:
            ingredient_data (dict): For example:
                {
                    "ingredient_name": "Flour",
                    "ingredient_category": "Baking"
                }

        Returns:
            int: The ID of the newly inserted ingredient.
        """
        DebugLogger().log("🔵 Inserting ingredient into the database...", "info")
        DebugLogger().log(f"🟢 Ingredient Name: {ingredient_data["ingredient_name"]}, Ingredient Category: {ingredient_data["ingredient_category"]}\n", "debug")
        cursor.execute(
            """
            INSERT INTO ingredients (ingredient_name, ingredient_category)
            VALUES (?, ?)
            """,
            (
                ingredient_data["ingredient_name"],
                ingredient_data["ingredient_category"]
            )
        )
        return cursor.lastrowid
        # Add logging for debugging via custom DebugLogger
    @staticmethod
    def insert_recipe_ingredient(cursor, recipe_id, ingredient_id, quantity, unit): # ✅
        """
        Inserts a record into the recipe_ingredients join table.
        """
        DebugLogger().log("🔵 Linking ingredient to recipe...", "info")
        DebugLogger().log("🟢 Recipe ID: {recipe_id}, Ingredient ID: {ingredient_id}, Quantity: {quantity}, Unit: {unit}\n", "debug")
        cursor.execute(
            """
            INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit)
            VALUES (?, ?, ?, ?)
            """,
            (recipe_id, ingredient_id, quantity, unit)
        )

    @staticmethod
    def insert_meal(cursor, meal_name, main_recipe_id, side_recipes):
        """
        Inserts a new meal into the database.

        Args:
            cursor (sqlite3.Cursor): Active database cursor.
            meal_name (str): The name of the meal.
            main_recipe_id (int): The main recipe's ID.
            side_recipes (list): List of up to 3 side recipes.

        Returns:
            int: The ID of the newly inserted meal.
        """
        DebugLogger().log(f"🔵 Inserting meal '{meal_name}' into the database...", "info")

        cursor.execute(
            """
            INSERT INTO meal_selection (meal_name, main_recipe_id, side_recipe_1, side_recipe_2, side_recipe_3)
            VALUES (?, ?, ?, ?, ?)
            """,
            (meal_name, main_recipe_id, *side_recipes)
        )
        return cursor.lastrowid

    #🔹REMOVE DATA
    def delete_recipe(cursor, recipe_id): # ❌
        """
        Removes a recipe from the database.
        Low-level SQL delete operation.

        Args:
            recipe_id (int): The ID of the recipe to remove.
        """
        pass

    def delete_ingredient(cursor, ingredient_id): # ❌
        """
        Removes an ingredient from the database.
        Low-level SQL delete operation.

        Args:
            ingredient_id (int): The ID of the ingredient to remove.
        """
        pass

    def delete_weekly_recipe(cursor, recipe_id): # ❌
        """
        Removes a weekly recipe from the database.
        Low-level SQL delete operation. 
        """
        # Remove the weekly recipe from the database
        # Return True if successful, False otherwise
        pass

    #🔹FETCH DATA
    @staticmethod
    def get_all_recipes(cursor): # ✅
        """
        Retrieves all recipes from the database.

        Args:
            cursor (sqlite3.Cursor): Active database cursor.

        Returns:
            list: A list of dictionaries, each containing recipe details.
        """
        DebugLogger().log("🔵 Fetching all recipes from the database...", "info")

        cursor.execute("""
            SELECT id, recipe_name, recipe_category, total_time, servings, directions, image_path
            FROM recipes
        """)

        rows = cursor.fetchall()
        if not rows:
            return []

        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    @staticmethod
    def get_recipe(cursor, recipe_id): # ✅
        """
        Retrieves a single recipe by its unique ID.

        Args:
            cursor (sqlite3.Cursor): Active database cursor.
            recipe_id (int): The ID of the recipe to retrieve.

        Returns:
            dict or None: A dictionary representing the recipe if found, 
                        or None if no recipe matches the given ID.
        """
        DebugLogger().log("🟢 Fetching recipe with ID '{recipe_id}' from the database...", "debug")
        
        cursor.execute("""
            SELECT id, recipe_name, recipe_category, total_time, servings, directions, image_path
            FROM recipes
            WHERE id = ?
        """, (recipe_id,))
        
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        
        return None

    def get_all_ingredients(cursor, recipe_id): # ⚠️
        """
        Fetch all ingredients for a recipe from the database.
        Low-level SQL select operation.

        Args:
            recipe_id (int): The ID of the recipe to fetch ingredients for.

        Returns:
            list: A list of dictionaries representing the ingredients.
        """
        DebugLogger().log("Fetching all ingredients for recipe with ID '{recipe_id}' from the database...", "debug")
        cursor.execute("SELECT * FROM ingredients WHERE recipe_id = ?", (recipe_id,))
        return cursor.fetchall()
        # Add logging for debugging via custom DebugLogger

    def get_ingrediet(cursor, ingredient_id): # ❌
        """
        Fetch an ingredient by ID from the database.
        Low-level SQL select operation.

        Args:
            ingredient_id (int): The ID of the ingredient to fetch.

        Returns:
            dict: A dictionary representing the ingredient.
        """
        pass

    @staticmethod 
    def get_recipe_ingredients(cursor, recipe_id): # ⚠️
        """
        Retrieves all ingredients linked to a recipe.

        Args:
            cursor (sqlite3.Cursor): Active database cursor.
            recipe_id (int): The ID of the recipe to fetch ingredients for.

        Returns:
            list: A list of dictionaries containing ingredient details.
        """
        # DebugLogger().log("🟢 Fetching ingredients for recipe ID '{recipe_id}'...\n", "debug")
        
        cursor.execute("""
            SELECT i.id, i.ingredient_name, i.ingredient_category, ri.quantity, ri.unit
            FROM recipe_ingredients ri
            JOIN ingredients i ON ri.ingredient_id = i.id
            WHERE ri.recipe_id = ?
        """, (recipe_id,))
        
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @staticmethod
    def get_meal(cursor, meal_id):
        """
        Retrieves a meal from the database.

        Args:
            cursor (sqlite3.Cursor): Active database cursor.
            meal_id (int): The ID of the meal.

        Returns:
            dict: The meal's details, or None if not found.
        """
        DebugLogger().log(f"🟢 Fetching meal with ID: {meal_id}...", "debug")

        cursor.execute(
            """
            SELECT id, meal_name, main_recipe_id, side_recipe_1, side_recipe_2, side_recipe_3
            FROM meal_selection
            WHERE id = ?
            """,
            (meal_id,)
        )
        
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        
        return None
    
    @staticmethod
    def get_all_meals(cursor):
        """
        Fetches all saved meals from the meal_selection table.

        Args:
            cursor (sqlite3.Cursor): Active database cursor.

        Returns:
            list: List of meal records as dictionaries.
        """
        DebugLogger().log("🔵 Fetching all meals from the database...", "info")

        cursor.execute("""
            SELECT id, meal_name, main_recipe_id, side_recipe_1, side_recipe_2, side_recipe_3
            FROM meal_selection
        """)

        rows = cursor.fetchall()
        if not rows:
            return []

        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    #🔹CHECK DATA
    def recipe_exists(self, name, category): # ⚠️
        """
        Check if a recipe with the given name and category already exists.

        Args:
            name (str): The name of the recipe.
            category (str): The category of the recipe.

        Returns:
            bool: True if the recipe exists, False otherwise.
        """
        DebugLogger().log("Checking if recipe '{name}' exists in category '{category}'...", "debug")
        query = "SELECT 1 FROM recipes WHERE name = ? AND category = ?"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (name, category))
            return cursor.fetchone() is not None

    def ingredient_exists(self, name): # ❌
        """
        Check if an ingredient with the given name already exists.

        Args:
            name (str): The name of the ingredient.

        Returns:
            bool: True if the ingredient exists, False otherwise.
        """
        # Check if an ingredient with the given name exists
        # Return True if it exists, False otherwise
        pass

    def recipe_in_menu(self, recipe_id): # ❌   
        """
        Check if a recipe is already in the weekly menu.

        Args:
            recipe_id (int): The ID of the recipe.

        Returns:
            bool: True if the recipe is in the weekly menu, False otherwise.
        """
        # Check if the recipe is in the weekly menu
        # Return True if it is, False otherwise
        pass

#🔸END