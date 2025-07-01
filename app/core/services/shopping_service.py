"""app/core/services/shopping_service.py

High level coordination for shopping list features."""

# ── Imports ─────────────────────────────────────────────────────────────────────────────
from typing import List, Optional
import sqlite3

from app.core.models.shopping_item import ShoppingItem
from app.core.models.shopping_state import ShoppingState
from app.core.services.meal_service import MealService
from .shopping_repository import ShoppingRepository
from .base_service import BaseService
from dev_tools import DebugLogger

# ── Class Definition ────────────────────────────────────────────────────────────────────
class ShoppingService(BaseService):
    """Provides aggregated shopping list operations."""

    @staticmethod
    def generate_shopping_list(
        recipe_ids: List[int],
        conn: Optional[sqlite3.Connection] = None,
    ) -> List[ShoppingItem]:
        """Generate a shopping list including manual items.
        
        Args:
            recipe_ids (List[int]): List of recipe IDs to generate shopping list from.
            conn (Optional[sqlite3.Connection]): Optional database connection.
            
        Returns:
            List[ShoppingItem]: List of ShoppingItem objects representing shopping list.
        """
        with ShoppingService.connection_ctx(conn) as db:
            result: List[ShoppingItem] = []
            for item in ShoppingRepository.aggregate_ingredients(recipe_ids, db):
                state = ShoppingState.get_state(item.key(), connection=db)
                if state:
                    item.have = state.checked
                result.append(item)
            for manual in ShoppingRepository.get_manual_items(db):
                result.append(manual.to_item())
            DebugLogger.log(f"[ShoppingService] Total ingredients generated: {len(result)}", "info")
            return result

    @staticmethod
    def get_recipe_ids_from_meals(meal_ids: List[int]) -> List[int]:
        """Return recipe IDs for given meal selections.
        
        Args:
            meal_ids (List[int]): List of meal IDs to extract recipe IDs from.
        
        Returns:
            List[int]: List of recipe IDs associated with the meals.
        """
        recipe_ids: List[int] = []
        for meal_id in meal_ids:
            meal = MealService.load_meal(meal_id)
            if not meal:
                continue
            recipe_ids.append(meal.main_recipe_id)
            if meal.side_recipe_1:
                recipe_ids.append(meal.side_recipe_1)
            if meal.side_recipe_2:
                recipe_ids.append(meal.side_recipe_2)
            if meal.side_recipe_3:
                recipe_ids.append(meal.side_recipe_3)
        return recipe_ids

    # static methods to interact with the repository
    add_manual_item = ShoppingRepository.add_manual_item
    clear_manual_items = ShoppingRepository.clear_manual_items
    toggle_have_status = ShoppingRepository.toggle_have_status
    get_ingredient_breakdown = ShoppingRepository.ingredient_breakdown

