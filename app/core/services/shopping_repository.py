"""app/core/services/shopping_repository.py

Low-level shopping list database operations."""

# ── Imports ─────────────────────────────────────────────────────────────────────────────
import sqlite3
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

from app.core.models.ingredient import Ingredient
from app.core.models.recipe import Recipe
from app.core.models.recipe_ingredient import RecipeIngredient
from app.core.models.shopping_item import ShoppingItem
from app.core.models.shopping_list import ShoppingList
from .base_service import BaseService

# ── Class Definition ────────────────────────────────────────────────────────────────────
class ShoppingRepository(BaseService):
    """Encapsulates direct shopping list DB logic."""

    _CONVERSIONS: Dict[str, Dict[str, float]] = {
        "butter": {"stick": 8.0, "tbsp": 1.0},
    }

    @staticmethod
    def _convert_qty(
        name: str, 
        qty: float, 
        unit: str
    ) -> Tuple[float, str]:
        """ Convert ingredient quantity to a standard unit if applicable.

        Args:
            name (str): Ingredient name.
            qty (float): Quantity to convert.
            unit (str): Current unit of the ingredient.
        Returns:
            Tuple[float, str]: Converted quantity and unit.
        """
        key = name.lower()
        if key in ShoppingRepository._CONVERSIONS:
            group = ShoppingRepository._CONVERSIONS[key]
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
    def _fetch_rows(
        recipe_ids: List[int], 
        conn: sqlite3.Connection
    ) -> List[RecipeIngredient]:
        """Fetch all recipe ingredients for given recipe IDs.

        Args:
            recipe_ids (List[int]): List of recipe IDs to fetch ingredients for.
            conn (sqlite3.Connection): Database connection.

        Returns:
            List[RecipeIngredient]: List of RecipeIngredient objects.
        """
        placeholders = ",".join("?" for _ in recipe_ids)
        sql = f"SELECT * FROM recipe_ingredients WHERE recipe_id IN ({placeholders})"
        return RecipeIngredient.raw_query(sql, tuple(recipe_ids), connection=conn)

    @staticmethod
    def aggregate_ingredients(
        recipe_ids: List[int],
        conn: Optional[sqlite3.Connection] = None,
    ) -> List[ShoppingItem]:
        """Aggregate ingredients from recipes into a shopping list.

        Args:
            recipe_ids (List[int]): List of recipe IDs to aggregate ingredients from.
            conn (Optional[sqlite3.Connection]): Optional database connection.

        Returns:
            List[ShoppingItem]: List of aggregated ShoppingItem objects.
        """
        with ShoppingRepository.connection_ctx(conn) as db:
            rows = ShoppingRepository._fetch_rows(recipe_ids, db)
            agg: Dict[int, Dict[str, Any]] = defaultdict(lambda: {
                "qty": 0.0,
                "unit": None,
                "category": None,
                "name": None,
            })
            for ri in rows:
                ing = Ingredient.get(ri.ingredient_id)
                data = agg[ri.ingredient_id]
                data["name"] = ing.ingredient_name
                data["category"] = ing.ingredient_category
                data["unit"] = ri.unit or data["unit"]
                data["qty"] += ri.quantity or 0.0

            items: List[ShoppingItem] = []
            for data in agg.values():
                q, u = ShoppingRepository._convert_qty(data["name"], data["qty"], data["unit"] or "")
                items.append(
                    ShoppingItem(
                        ingredient_name=data["name"],
                        quantity=q,
                        unit=u,
                        category=data["category"],
                        source="recipe",
                        have=False,
                    )
                )
            return items

    @staticmethod
    def ingredient_breakdown(
        recipe_ids: List[int],
        conn: Optional[sqlite3.Connection] = None,
    ) -> Dict[str, List[Tuple[str, float, str]]]:
        """Get detailed breakdown of ingredients used in recipes.

        Args:
            recipe_ids (List[int]): List of recipe IDs to get breakdown for.
            conn (Optional[sqlite3.Connection]): Optional database connection.

        Returns:
            Dict[str, List[Tuple[str, float, str]]]: Breakdown of ingredients by name and unit.
        """
        with ShoppingRepository.connection_ctx(conn) as db:
            rows = ShoppingRepository._fetch_rows(recipe_ids, db)
            breakdown: Dict[str, List[Tuple[str, float, str]]] = defaultdict(list)
            for ri in rows:
                ing = Ingredient.get(ri.ingredient_id)
                rec = Recipe.get(ri.recipe_id)
                qty, unit = ShoppingRepository._convert_qty(
                    ing.ingredient_name, ri.quantity or 0.0, ri.unit or ""
                )
                key = f"{ing.ingredient_name.lower()}::{unit}"
                breakdown[key].append((rec.recipe_name, qty, unit))
            return breakdown

    # ── Manual Item Operations ──────────────────────────────────────────────────────────
    @staticmethod
    def add_manual_item(
        name: str,
        qty: float,
        unit: str,
        conn: Optional[sqlite3.Connection] = None
    ) -> None:
        """Add a manual item to the shopping list.

        Args:
            name (str): Name of the ingredient.
            qty (float): Quantity of the ingredient.
            unit (str): Unit of measurement for the ingredient.
            conn (Optional[sqlite3.Connection]): Optional database connection.
        """
        with ShoppingRepository.connection_ctx(conn) as db:
            ShoppingList(
                ingredient_name=name,
                quantity=qty,
                unit=unit,
                have=False,
            ).save(connection=db)

    @staticmethod
    def clear_manual_items(conn: Optional[sqlite3.Connection] = None) -> None:
        """Clear all manual items from the shopping list.

        Args:
            conn (Optional[sqlite3.Connection]): Optional database connection.
        """
        with ShoppingRepository.connection_ctx(conn) as db:
            ShoppingList.raw_query(
                f"DELETE FROM {ShoppingList.table_name()}",
                (),
                connection=db,
            )

    @staticmethod
    def toggle_have_status(
        item_name: str,
        conn: Optional[sqlite3.Connection] = None
    ) -> None:
        """Toggle the 'have' status of a manual item.

        Args:
            item_name (str): Name of the item to toggle.
            conn (Optional[sqlite3.Connection]): Optional database connection.
        """
        with ShoppingRepository.connection_ctx(conn) as db:
            items = ShoppingList.raw_query(
                f"SELECT * FROM {ShoppingList.table_name()} WHERE ingredient_name = ?",
                (item_name,),
                connection=db,
            )
            if items:
                item = items[0]
                item.have = not item.have
                item.save(connection=db)

    @staticmethod
    def get_manual_items(conn: Optional[sqlite3.Connection] = None) -> List[ShoppingList]:
        """Retrieve all manual items from the shopping list.

        Args:
            conn (Optional[sqlite3.Connection]): Optional database connection.

        Returns:
            List[ShoppingList]: List of manual ShoppingList items.
        """
        with ShoppingRepository.connection_ctx(conn) as db:
            return ShoppingList.raw_query(
                f"SELECT * FROM {ShoppingList.table_name()}",
                (),
                connection=db,
            )

