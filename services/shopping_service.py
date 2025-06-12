""" services/shopping_service.py

Structured service for managing shopping lists.
Combines ingredients from recipes and manual entries for unified display and processing.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
import sqlite3
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

from core.utilities.debug_logger import DebugLogger
from database.db import get_connection
from database.models.ingredient import Ingredient
from database.models.recipe import Recipe
from database.models.recipe_ingredient import RecipeIngredient
from database.models.shopping_item import ShoppingItem
from database.models.shopping_list import ShoppingList
from database.models.shopping_state import ShoppingState
from services.meal_service import MealService


class ShoppingService:
    """
    Structured service for managing shopping lists.
    Combines ingredients from recipes and manual entries for unified display and processing.
    """

    # ── Constants ───────────────────────────────────────────────────────────────
    _CONVERSIONS: Dict[str, Dict[str, float]] = {
        "butter": {"stick": 8.0, "tbsp": 1.0},
        # Add more conversions as needed
    }

    @staticmethod
    def _convert_qty(
        name: str,
        qty: float,
        unit: str
    ) -> Tuple[float, str]:
        key = name.lower()
        if key in ShoppingService._CONVERSIONS:
            group = ShoppingService._CONVERSIONS[key]
            base = unit
            factor = group.get(unit)
            if factor is None:
                return qty, unit
            qty_base = qty * factor
            for u, f in sorted(group.items(), key=lambda it: -it[1]):
                if qty_base % f == 0:
                    return qty_base // f, u
            return qty_base / group[base], base
        return qty, unit

    @staticmethod
    def get_ingredient_breakdown(
        recipe_ids: list[int],
        connection: Optional[sqlite3.Connection] = None
    ) -> dict[str, list[tuple[str, float, str]]]:
        """
        Returns a mapping from ShoppingItem.key() →
        list of (recipe_name, qty, unit) tuples.
        """
        if connection is None:
            with get_connection() as conn:
                return ShoppingService.get_ingredient_breakdown(recipe_ids, connection=conn)

        # fetch all RecipeIngredient rows for these recipes
        placeholders = ",".join("?" for _ in recipe_ids)
        sql = f"SELECT * FROM recipe_ingredients WHERE recipe_id IN ({placeholders})"
        rows = RecipeIngredient.raw_query(sql, tuple(recipe_ids), connection=connection)

        breakdown: dict[str, list[tuple[str, float, str]]] = defaultdict(list)
        for ri in rows:
            ing = Ingredient.get(ri.ingredient_id)                    # :contentReference[oaicite:0]{index=0}
            rec = Recipe.get(ri.recipe_id)                            # assumes a Recipe model
            # normalize/convert qty exactly as in _aggregate_recipe_ingredients
            qty, unit = ShoppingService._convert_qty(
                ing.ingredient_name, ri.quantity or 0.0, ri.unit or ""
            )
            key = f"{ing.ingredient_name.lower()}::{unit}"
            breakdown[key].append((rec.recipe_name, qty, unit))

        return breakdown

    @staticmethod
    def generate_shopping_list(
        recipe_ids: List[int],
        connection: Optional[sqlite3.Connection] = None
    ) -> List[ShoppingItem]:
        """
        Generate a shopping list based on recipe IDs, restoring 'have' states.
        """
        if connection is None:
            with get_connection() as conn:
                return ShoppingService.generate_shopping_list(recipe_ids, connection=conn)

        result: List[ShoppingItem] = []
        # Load from Recipes
        for item in ShoppingService._aggregate_recipe_ingredients(recipe_ids, connection=connection):
            state = ShoppingState.get_state(item.key(), connection=connection)
            if state:
                item.have = state.checked
            result.append(item)

        # Append Manual Items
        manual_rows = ShoppingList.raw_query(
            f"SELECT * FROM {ShoppingList.table_name()}",
            (),
            connection=connection
        )
        for m in manual_rows:
            result.append(m.to_item())

        DebugLogger.log(f"[ShoppingService] Total ingredients generated: {len(result)}", "info")
        return result

    @staticmethod
    def _aggregate_recipe_ingredients(
        recipe_ids: List[int],
        connection: Optional[sqlite3.Connection] = None
    ) -> List[ShoppingItem]:
        """
        Aggregate ingredients from recipes into a shopping list.
        """
        if connection is None:
            with get_connection() as conn:
                return ShoppingService._aggregate_recipe_ingredients(recipe_ids, connection=conn)

        agg: Dict[int, Dict[str, Any]] = defaultdict(lambda: {
            "qty": 0.0,
            "unit": None,
            "category": None,
            "name": None
        })

        # Query only relevant recipe_ingredients
        placeholders = ",".join("?" for _ in recipe_ids)
        sql = f"SELECT * FROM recipe_ingredients WHERE recipe_id IN ({placeholders})"
        rows = RecipeIngredient.raw_query(sql, tuple(recipe_ids), connection=connection)

        for ri in rows:
            ing = Ingredient.get(ri.ingredient_id)
            data = agg[ri.ingredient_id]
            data["name"] = ing.ingredient_name
            data["category"] = ing.ingredient_category
            data["unit"] = ri.unit or data["unit"]
            data["qty"] += ri.quantity or 0.0

        items: List[ShoppingItem] = []
        for data in agg.values():
            q, u = ShoppingService._convert_qty(data["name"], data["qty"], data["unit"] or "")
            item = ShoppingItem(
                ingredient_name=data["name"],
                quantity=q,
                unit=u,
                category=data["category"],
                source="recipe",
                have=False
            )
            items.append(item)
        return items

    @staticmethod
    def get_recipe_ids_from_meals(
        meal_ids: List[int]
    ) -> List[int]:
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
        connection: Optional[sqlite3.Connection] = None
    ) -> None:
        """
        Add a manual item to the shopping list.
        """
        if connection is None:
            with get_connection() as conn:
                return ShoppingService.add_manual_item(name, qty, unit, connection=conn)

        item = ShoppingList(
            ingredient_name=name,
            quantity=qty,
            unit=unit,
            have=False
        ).save(connection=connection)

    @staticmethod
    def clear_manual_items(
        connection: Optional[sqlite3.Connection] = None
    ) -> None:
        """Clear all manual items from the shopping list."""
        if connection is None:
            with get_connection() as conn:
                return ShoppingService.clear_manual_items(connection=conn)

        ShoppingList.raw_query(
            f"DELETE FROM {ShoppingList.table_name()}",
            (),
            connection=connection
        )

    @staticmethod
    def toggle_have_status(
        item_name: str,
        connection: Optional[sqlite3.Connection] = None
    ) -> None:
        """
        Toggle the 'have' status of a shopping list item.
        """
        if connection is None:
            with get_connection() as conn:
                return ShoppingService.toggle_have_status(item_name, connection=conn)

        items = ShoppingList.raw_query(
            f"SELECT * FROM {ShoppingList.table_name()} WHERE ingredient_name = ?",
            (item_name,),
            connection=connection
        )
        if items:
            item = items[0]
            item.have = not item.have
            item.save(connection=connection)