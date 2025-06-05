"""service/ingredient_service.py

Service class for managing ingredients.
Provides methods to retrieve, create, and validate ingredients.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
import sqlite3
from typing import Optional

from database.db import get_connection
from database.models.ingredient import Ingredient
from services.dtos.ingredient_dtos import IngredientSearchDTO, IngredientCreateDTO

# ── Class Definition ────────────────────────────────────────────────────────────
class IngredientService:
    """
    Service class for managing ingredients.
    Provides methods to retrieve, create, and validate ingredients with transactional support.
    """

    @staticmethod
    def list_all_ingredient_names(
        conn: Optional[sqlite3.Connection] = None
    ) -> list[str]:
        """
        Returns a list of all distinct ingredient names.
        
        Args:
            connection (Optional[sqlite3.Connection]): Database connection to use.
        Returns:
            list[str]: List of distinct ingredient names.
        """
        sql = "SELECT DISTINCT ingredient_name FROM ingredients"
        results = Ingredient.raw_query(sql, (), connection=conn)
        return [r.ingredient_name for r in results]

    @staticmethod
    def find_matching_ingredients(
        search_dto: IngredientSearchDTO,
        conn: Optional[sqlite3.Connection] = None
    ) -> list[Ingredient]:
        """
        Finds ingredients matching the search term in a case-insensitive manner.

        Args:
            search_dto (IngredientSearchDTO): DTO containing the search term.
            connection (Optional[sqlite3.Connection]): Database connection to use.
        Returns:
            list[Ingredient]: List of matching Ingredient objects.
        """
        term = search_dto.search_term 

        sql = "SELECT * FROM ingredients WHERE ingredient_name LIKE ?"
        params = [f"%{term}%"]
        if search_dto.category:
            sql += " AND ingredient_category = ?"
            params.append(search_dto.category.strip())
        return Ingredient.raw_query(sql, tuple(params), connection=conn)

    @staticmethod
    def get_or_create_ingredient(
        create_dto: IngredientCreateDTO,
        conn: Optional[sqlite3.Connection] = None # Parameter name is 'conn'
    ) -> Ingredient:
        """
        Retrieves an existing ingredient or creates a new one if it doesn't exist.

        Args:
            create_dto (IngredientCreateDTO): DTO containing the ingredient details.
            connection (Optional[sqlite3.Connection]): Database connection to use.
        Returns:
            Ingredient: The existing or newly created Ingredient object.
        """
        name = create_dto.ingredient_name
        category = create_dto.ingredient_category

        # try to find an existing ingredient (by name+category).
        existing = Ingredient.get_by_field(
            connection=conn, 
            ingredient_name=name, 
            ingredient_category=category 
        )
        if existing:
            return existing

        new_ing = Ingredient(
            ingredient_name=name,
            ingredient_category=category
        )
        new_ing.save(connection=conn) # 'connection' is correctly passed to save
        return new_ing
