"""Database helpers for ShoppingService."""

from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple
import sqlite3

from app.core.data.models.ingredient import Ingredient
from app.core.data.models.recipe import Recipe
from app.core.data.models.recipe_ingredient import RecipeIngredient
from app.core.data.models.shopping_item import ShoppingItem
from app.core.data.models.shopping_list import ShoppingList
from app.core.data.models.shopping_state import ShoppingState
from .base_service import BaseService


class ShoppingRepository(BaseService):
    """Low-level shopping list database operations."""

    _CONVERSIONS: Dict[str, Dict[str, float]] = {
        "butter": {"stick": 8.0, "tbsp": 1.0},
    }

    @staticmethod
    def _convert_qty(name: str, qty: float, unit: str) -> Tuple[float, str]:
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
    def _fetch_join_rows(recipe_ids: List[int], conn: sqlite3.Connection) -> list[sqlite3.Row]:
        placeholders = ",".join("?" for _ in recipe_ids)
        sql = (
            "SELECT ri.*, i.ingredient_name, i.ingredient_category, r.recipe_name "
            "FROM recipe_ingredients ri "
            "JOIN ingredients i ON ri.ingredient_id = i.id "
            "JOIN recipes r ON ri.recipe_id = r.id "
            f"WHERE ri.recipe_id IN ({placeholders})"
        )
        cursor = conn.execute(sql, tuple(recipe_ids))
        return cursor.fetchall()

    @classmethod
    def aggregated_items(cls, recipe_ids: List[int], conn: Optional[sqlite3.Connection] = None) -> List[ShoppingItem]:
        with cls.connection_ctx(conn) as conn:
            rows = cls._fetch_join_rows(recipe_ids, conn)
            agg: Dict[int, Dict[str, Any]] = defaultdict(lambda: {"qty": 0.0, "unit": None, "category": None, "name": None})
            for row in rows:
                data = agg[row["ingredient_id"]]
                data["name"] = row["ingredient_name"]
                data["category"] = row["ingredient_category"]
                data["unit"] = row["unit"] or data["unit"]
                data["qty"] += row["quantity"] or 0.0
            items: List[ShoppingItem] = []
            for data in agg.values():
                q, u = cls._convert_qty(data["name"], data["qty"], data["unit"] or "")
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

    @classmethod
    def ingredient_breakdown(cls, recipe_ids: List[int], conn: Optional[sqlite3.Connection] = None) -> dict[str, list[tuple[str, float, str]]]:
        with cls.connection_ctx(conn) as conn:
            rows = cls._fetch_join_rows(recipe_ids, conn)
            breakdown: dict[str, list[tuple[str, float, str]]] = defaultdict(list)
            for row in rows:
                qty, unit = cls._convert_qty(row["ingredient_name"], row["quantity"] or 0.0, row["unit"] or "")
                key = f"{row['ingredient_name'].lower()}::{unit}"
                breakdown[key].append((row["recipe_name"], qty, unit))
            return breakdown

    @classmethod
    def fetch_manual_items(cls, conn: Optional[sqlite3.Connection] = None) -> List[ShoppingItem]:
        with cls.connection_ctx(conn) as conn:
            rows = ShoppingList.raw_query(f"SELECT * FROM {ShoppingList.table_name()}", (), connection=conn)
            return [row.to_item() for row in rows]

    @classmethod
    def add_manual_item(cls, name: str, qty: float, unit: str, conn: Optional[sqlite3.Connection] = None) -> None:
        with cls.connection_ctx(conn) as conn:
            ShoppingList(
                ingredient_name=name,
                quantity=qty,
                unit=unit,
                have=False,
            ).save(connection=conn)

    @classmethod
    def clear_manual_items(cls, conn: Optional[sqlite3.Connection] = None) -> None:
        with cls.connection_ctx(conn) as conn:
            ShoppingList.raw_query(
                f"DELETE FROM {ShoppingList.table_name()}", (), connection=conn
            )

    @classmethod
    def toggle_have_status(cls, item_name: str, conn: Optional[sqlite3.Connection] = None) -> None:
        with cls.connection_ctx(conn) as conn:
            items = ShoppingList.raw_query(
                f"SELECT * FROM {ShoppingList.table_name()} WHERE ingredient_name = ?",
                (item_name,),
                connection=conn,
            )
            if items:
                item = items[0]
                item.have = not item.have
                item.save(connection=conn)

    @classmethod
    def restore_have_states(cls, items: List[ShoppingItem], conn: Optional[sqlite3.Connection] = None) -> None:
        with cls.connection_ctx(conn) as conn:
            for item in items:
                state = ShoppingState.get_state(item.key(), connection=conn)
                if state:
                    item.have = state.checked

