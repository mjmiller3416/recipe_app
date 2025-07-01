"""High-level coordination for shopping list features."""

from typing import List, Optional
import sqlite3

from app.core.data.models.shopping_item import ShoppingItem
from .meal_service import MealService
from .shopping_repository import ShoppingRepository
from .base_service import BaseService
from app.core.dev_tools import DebugLogger


class ShoppingService(BaseService):
    """Provide user-facing shopping list operations."""

    @staticmethod
    def get_ingredient_breakdown(
        recipe_ids: List[int],
        conn: Optional[sqlite3.Connection] = None,
    ) -> dict[str, list[tuple[str, float, str]]]:
        """Return a breakdown of ingredient usage by recipe."""
        return ShoppingRepository.ingredient_breakdown(recipe_ids, conn)

    @staticmethod
    def generate_shopping_list(
        recipe_ids: List[int],
        conn: Optional[sqlite3.Connection] = None,
    ) -> List[ShoppingItem]:
        """Generate the full shopping list for the given recipes."""
        items = ShoppingRepository.aggregated_items(recipe_ids, conn)
        ShoppingRepository.restore_have_states(items, conn)
        items.extend(ShoppingRepository.fetch_manual_items(conn))
        DebugLogger.log(
            f"[ShoppingService] Total ingredients generated: {len(items)}", "info"
        )
        return items

    @staticmethod
    def get_recipe_ids_from_meals(meal_ids: List[int]) -> List[int]:
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

    @staticmethod
    def add_manual_item(
        name: str,
        qty: float,
        unit: str,
        conn: Optional[sqlite3.Connection] = None,
    ) -> None:
        """Add a manual item to the shopping list."""
        ShoppingRepository.add_manual_item(name, qty, unit, conn)

    @staticmethod
    def clear_manual_items(conn: Optional[sqlite3.Connection] = None) -> None:
        """Remove all manual items from the shopping list."""
        ShoppingRepository.clear_manual_items(conn)

    @staticmethod
    def toggle_have_status(
        item_name: str,
        conn: Optional[sqlite3.Connection] = None,
    ) -> None:
        """Toggle the 'have' status of a shopping item."""
        ShoppingRepository.toggle_have_status(item_name, conn)


